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
  - Apstra AOS IP Pool module lets you manage your IP Pools easily. You can
    create and delete IP Pools by Name or ID. This
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
        Only one of I(name) or I(id) can be set.
  id:
    description:
      - AOS Id of the IP Pool to manage.
        Only one of I(name) or I(id) can be set.
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
    default: 4 (IPv4)
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

from ansible.module_utils.basic import AnsibleModule
from library.aos_resource import IpPool


def ip_pool(module):
    """
    Main function to create, change or delete AOS IP and IPv6 resource pool
    """
    margs = module.params
    target_state = margs['state']
    new_subnet = margs['subnets']
    addr_type = margs['ip_version']

    pool = IpPool(module, margs['session'], addr_type, module.check_mode)

    if 'subnets' in margs.keys():
        errors = pool.validate(new_subnet)

        if errors:
            pool.module_exit(error=errors,
                             name='', uuid='',
                             value='', changed=False)

    new_subnets = pool.get_subnets(new_subnet)

    existing = {}

    if margs['name'] is not None:
        name = margs['name']
        existing = pool.find_by_name(name)

    if margs['id'] is not None:
        uuid = margs['id']
        existing = pool.find_by_id(uuid)

    if target_state == 'present':
        if not existing:
            pool.create(new_subnets, margs['name'])
        else:
            pool.update(existing["display_name"],
                        existing["id"],
                        existing["subnets"],
                        new_subnets)

    elif target_state == "absent":
        if not existing:
            return pool.module_exit(error=[],
                                    name='', uuid='',
                                    value='', changed=False)

        pool.delete(existing["id"])


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
