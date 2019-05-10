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
module: aos_asn_pool
author: Ryan Booth (@that1guy15)
version_added: "2.7"
short_description: Manage AOS ASN Pool
description:
  - Apstra AOS ASN Pool module lets you manage your ASN Pool easily. You can
    create and delete ASN Pools by Name, ID or by using a JSON File. This
    module is idempotent and supports the I(check) mode.
    It's using the AOS REST API.
options:
  session:
    description:
      - An existing AOS session as obtained by M(aos_login) module.
    required: true
  name:
    description:
      - Name of the ASN Pool to manage.
        Only one of I(name), I(id) or I(content) can be set.
  id:
    description:
      - AOS Id of the ASN Pool to manage.
        Only one of I(name), I(id) or I(content) can be set.
  content:
    description:
      - Datastructure of the ASN Pool to manage. The data can be in YAML / JSON or
        directly a variable. It's the same datastructure that is returned
        on success in I(value).
  state:
    description:
      - Indicate what is the expected state of the ASN Pool (present or not).
    default: present
    choices: ['present', 'absent']
  ranges:
    description:
      - List of ASNs ranges to add to the ASN Pool. Each range (list) must have
        2 values. A start of range and an end of range.
'''

EXAMPLES = '''

- name: "Create ASN Pool"
  aos_asn_pool:
    session: "{{ aos_session }}"
    name: "my-asn-pool"
    ranges:
      - [ 100, 200 ]
    state: present
    register: asnpool

- name: "Update ASN Pool by Name"
  aos_asn_pool:
    session: "{{ aos_session }}"
    name: "{{ asnpool.name }}"
    ranges:
      - [ 300, 400 ]
    state: present

- name: "Update ASN Pool by ID"
  aos_asn_pool:
    session: "{{ aos_session }}"
    id: "{{ asnpool.id }}"
    ranges:
      - [ 300, 400 ]
    state: present

- name: "Delete ASN Pool"
  aos_asn_pool:
    session: "{{ aos_session }}"
    name: "my-asn-pool"
    state: absent
'''

RETURNS = '''
name:
  description: Name of the ASN Pool
  returned: always
  type: str
  sample: Private-ASN-pool

id:
  description: AOS unique ID assigned to the ASN Pool
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
from library.aos import aos_post, aos_put, aos_delete, find_resource_item

ENDPOINT = 'resources/asn-pools'


def validate_ranges(module, ranges):
    """
    Validate ASN ranges provided are valid and properly formatted
    :param module: Ansible built in
    :param ranges: list
    :return: bool
    """
    for i, asn_range in enumerate(ranges, 1):
        if not isinstance(asn_range, list):
            module.fail_json(msg="Range {} must be a list not {}"
                             .format(i, type(asn_range)))
        elif len(asn_range) != 2:
            module.fail_json(msg="Range {} must be a list of 2 members, not {}"
                             .format(len(asn_range), i))
        elif not isinstance(asn_range[0], int):
            module.fail_json(msg="1st element of asn_range {} must be "
                                 "integer instead of {} "
                             .format(i, type(asn_range[0])))
        elif not isinstance(asn_range[1], int):
            module.fail_json(msg="2nd element of asn_range {} must be "
                                 "integer instead of {} "
                             .format(i, type(asn_range[1])))
        elif asn_range[1] <= asn_range[0]:
            module.fail_json(msg="2nd element of asn_range {} must be "
                                 "bigger than 1st ".format(i))

    return True


def get_ranges(pool):
    """
    convert ASN pool list to dict format
    :param pool: list
    :return: dict
    """
    return [{"first": r[0], "last": r[1]} for r in pool]


def asn_pool_absent(module, session, my_pool):
    """
    Remove ASN pool if exist and is not in use
    :param module: Ansible built in
    :param session: dict
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
        module.fail_json(msg="Unable to delete ASN Pool '%s', currently"
                             " in use" % my_pool['display_name'])

    if not module.check_mode:
        aos_delete(session, ENDPOINT, my_pool['id'])

    module.exit_json(changed=True,
                     name=my_pool['display_name'],
                     id=my_pool['id'],
                     value={})


def asn_pool_present(module, session, my_pool):
    """
    Create new ASN pool or modify existing pool
    :param module: Ansible built in
    :param session: dict
    :param my_pool: dict
    :return: dict
    """
    margs = module.params

    if not my_pool:

        if 'name' not in margs.keys():
            module.fail_json(msg="name is required to create a new resource")

        new_pool = {"ranges": get_ranges(margs['ranges']),
                    "display_name": margs['name'],
                    "id": margs['name']}

        if not module.check_mode:
            resp = aos_post(session, ENDPOINT, new_pool)

            module.exit_json(changed=True,
                             name=new_pool['display_name'],
                             id=resp['id'],
                             value=new_pool)

        module.exit_json(changed=False,
                         name=new_pool['display_name'],
                         id={},
                         value={})

    else:
        if my_pool['ranges']:

            endpoint_put = "{}/{}".format(ENDPOINT, my_pool['id'])

            new_pool = {"ranges": get_ranges(margs['ranges']),
                        "display_name": my_pool['display_name'],
                        "id": margs['name']}

            for asn_range in my_pool['ranges']:
                new_pool['ranges'].append({'first': asn_range['first'],
                                           'last': asn_range['last']})

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


def asn_pool(module):
    """
    Main function to create, change or delete AOS ASN resource pool
    """
    margs = module.params

    item_name = None
    item_id = None

    if margs['name'] is not None:
        item_name = margs['name']

    elif margs['id'] is not None:
        item_id = margs['id']

    if 'ranges' in margs.keys():
        validate_ranges(module, margs['ranges'])

    my_pool = find_resource_item(margs['session'],
                                 ENDPOINT,
                                 resource_name=item_name,
                                 resource_id=item_id)

    if margs['state'] == 'absent':
        asn_pool_absent(module, margs['session'], my_pool)

    elif margs['state'] == 'present':
        asn_pool_present(module, margs['session'], my_pool)


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
            ranges=dict(required=False, type="list", default=[])
        ),
        mutually_exclusive=[('name', 'id')],
        required_one_of=[('name', 'id')],
        supports_check_mode=True
    )

    asn_pool(module)


if __name__ == "__main__":
    main()
