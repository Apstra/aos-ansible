#!/usr/bin/python
#
# (c) 2017 Apstra Inc, <community@apstra.com>
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.
#

ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = '''
---
module: aos_ip_pool
author: Ryan Booth (@that1guy15)
version_added: "2.7"
short_description: Manage AOS IP Pool
description:
  - Apstra AOS IP Pool module lets you manage your IP Pool easily. You can 
    create and delete IP Pools by Name, ID or by using a JSON File. This 
    module is idempotent and supports the I(check) mode. 
    It's using the AOS REST API.
options:
  session:
    description:
      - An existing AOS session as obtained by M(aos_login) module.
    required: true
  name:
    description:
      - Name of the IP Pool to manage.
        Only one of I(name), I(id) or I(content) can be set.
  id:
    description:
      - AOS Id of the IP Pool to manage.
        Only one of I(name), I(id) or I(content) can be set.
  state:
    description:
      - Indicates the expected state of the IP Pool (present or absent).
    default: present
    choices: ['present', 'absent']
  subnets:
    description:
      - List of IP subnets to add to the IP Pool. Each subnet (list) must be 
        given in valid CIDR notation. ex 192.168.59.0/24 or 2005::0/64. All
        subnets given must be of the same type defined with 'ip_version'
  ip_version:
    description:
      - IPv4 (4) or IPv6 (6) address type of the subnets being added. 
'''

EXAMPLES = '''

- name: "Create IP Pool"
  aos_ip_pool:
    session: "{{ aos_session }}"
    name: "my-ip-pool"
    subnets:
      - 192.168.59.0/24
    state: present
    register: ippool

- name: "Create IPv6 Pool"
  aos_ip_pool:
    session: "{{ aos_session }}"
    name: "my-ip-pool"
    subnets:
      - fe80:0:0:1::/64
      - fe80:0:0:2::/64
    ip_version: 6
    state: present
    register: ippool

- name: "Update IP Pool by Name"
  aos_ip_pool:
    session: "{{ aos_session }}"
    name: "{{ ippool.name }}"
    subnets:
      - 192.168.100.0/24
    state: present

- name: "Update IP Pool by ID"
  aos_ip_pool:
    session: "{{ aos_session }}"
    id: "{{ ippool.id }}"
    subnets:
      - 192.168.100.0/24
    state: present

- name: "Delete IP Pool"
  aos_ip_pool:
    session: "{{ aos_session }}"
    name: "my-ip-pool"
    state: absent
'''

RETURNS = '''
name:
  description: Name of the IP Pool
  returned: always
  type: str
  sample: Private-IP-pool

id:
  description: AOS unique ID assigned to the IP Pool
  returned: always
  type: str
  sample: fcc4ac1c-e249-4fe7-b458-2138bfb44c06

value:
  description: Value of the object as returned by the AOS Server
  returned: always
  type: dict
  sample: {'...'}
'''

import ipaddress
from ansible.module_utils.basic import AnsibleModule
from module_utils.aos import aos_post, aos_put, aos_delete, find_resource_item

V4_ENDPOINT = 'resources/ip-pools'
V6_ENDPOINT = 'resources/ipv6-pools'


def validate_subnets(module, subnets, addr_type):
    """
    Validate IP subnets provided are valid and properly formatted
    :param module: Ansible built in
    :param subnets: list
    :param addr_type: int
    :return: bool
    """
    for i, subnet in enumerate(subnets, 1):
        try:
            results = ipaddress.ip_network(subnet)
            if results.version != addr_type:
                module.fail_json(msg="Subnet {} does not match ip_version {} "
                                     "configured for the pool "
                                 .format(subnet, addr_type))

        except ValueError as e:
            module.fail_json(msg="Invalid subnet {}: {}"
                             .format(subnet, e))

    return True


def get_subnets(pool):
    """
    convert IP pool list to dict format
    :param pool: list
    :return: dict
    """
    return [{"network": r} for r in pool]


def ip_pool_absent(module, session, endpoint, my_pool):
    """
    Remove IP pool if exist and is not in use
    :param module: Ansible built in
    :param session: dict
    :param endpoint: str
    :param my_pool: dict
    :return: dict
    """
    margs = module.params

    # If the resource does not exist, return directly
    if not my_pool:
        module.exit_json(changed=False,
                         name=margs['name'],
                         id='',
                         value={})

    if my_pool['status'] != 'not_in_use':
        module.fail_json(msg="Unable to delete IP Pool {}, currently"
                             " in use".format(my_pool['display_name']))

    if not module.check_mode:
        aos_delete(session, endpoint, my_pool['id'])

    module.exit_json(changed=True,
                     name=my_pool['display_name'],
                     id=my_pool['id'],
                     value={})


def ip_pool_present(module, session, endpoint, my_pool):
    """
    Create new IP pool or modify existing pool
    :param module: Ansible built in
    :param session: dict
    :param endpoint: str
    :param my_pool: dict
    :return: dict
    """
    margs = module.params

    if not my_pool:

        if 'name' not in margs.keys():
            module.fail_json(msg="name is required to create a new resource")

        new_pool = {"subnets": get_subnets(margs['subnets']),
                    "display_name": margs['name'],
                    "id": margs['name']}

        if not module.check_mode:
            resp = aos_post(session, endpoint, new_pool)

            module.exit_json(changed=True,
                             name=new_pool['display_name'],
                             id=resp['id'],
                             value=new_pool)

        module.exit_json(changed=False,
                         name=new_pool['display_name'],
                         id={},
                         value={})

    else:
        if my_pool['subnets']:

            endpoint_put = "{}/{}".format(endpoint, my_pool['id'])

            new_pool = {"subnets": get_subnets(margs['subnets']),
                        "display_name": my_pool['display_name'],
                        "id": margs['name']}

            for ip_subnet in my_pool['subnets']:
                new_pool['subnets'].append({'network': ip_subnet['network']})

            if not module.check_mode:
                aos_put(session, endpoint_put, new_pool)

                module.exit_json(changed=True,
                                 name=new_pool['display_name'],
                                 id=my_pool['id'],
                                 value=new_pool)

            module.exit_json(changed=False,
                             name=new_pool['display_name'],
                             id={},
                             value={})


def ip_pool(module):
    """
    Main function to create, change or delete AOS IP resource pool
    """
    margs = module.params

    item_name = False
    item_id = False

    if margs['name'] is not None:
        item_name = margs['name']

    elif margs['id'] is not None:
        item_id = margs['id']

    if 'subnets' in margs.keys():
        validate_subnets(module, margs['subnets'], margs['ip_version'])

    if margs['ip_version'] == 6:
        endpoint = V6_ENDPOINT
    else:
        endpoint = V4_ENDPOINT

    my_pool = find_resource_item(margs['session'],
                                 endpoint,
                                 resource_name=item_name,
                                 resource_id=item_id)

    if margs['state'] == 'absent':
        ip_pool_absent(module, margs['session'], endpoint, my_pool)

    elif margs['state'] == 'present':
        ip_pool_present(module, margs['session'], endpoint, my_pool)


def main():
    """
    Main function to setup inputs
    """
    module = AnsibleModule(
        argument_spec=dict(
            session=dict(required=True, type="dict"),
            name=dict(required=False),
            id=dict(required=False),
            state=dict(required=False,
                       choices=['present', 'absent'],
                       default="present",),
            subnets=dict(required=False, type="list", default=[]),
            ip_version=dict(required=False,
                             type="int",
                             choices=[4, 6],
                             default=4),
        ),
        mutually_exclusive=[('name', 'id')],
        required_one_of=[('name', 'id')],
        supports_check_mode=True
    )

    ip_pool(module)


if __name__ == "__main__":
    main()
