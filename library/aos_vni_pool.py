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
module: aos_vni_pool
author: Ryan Booth (@that1guy15)
version_added: "2.7"
short_description: Manage AOS VNI Pool
description:
  - Apstra AOS VNI Pool module lets you manage your VNI pools easily. You can
    create and delete VNI Pools by Name, ID or by using a JSON File. This
    module is idempotent and supports the I(check) mode.
    It's using the AOS REST API.
options:
  session:
    description:
      - An existing AOS session as obtained by M(aos_login) module.
    required: true
  name:
    description:
      - Name of the VNI Pool to manage.
        Only one of I(name), I(id) or I(content) can be set.
  id:
    description:
      - AOS Id of the VNI Pool to manage.
        Only one of I(name), I(id) or I(content) can be set.
  state:
    description:
      - Indicates the expected state of the VNI Pool (present or absent).
    default: present
    choices: ['present', 'absent']
  ranges:
    description:
      - List of VNIs ranges to add to the VNI Pool. Each range (list) must have
        2 values. A start of range and an end of range.
'''

EXAMPLES = '''

- name: "Create VNI Pool"
  aos_vni_pool:
    session: "{{ aos_session }}"
    name: "my-vni-pool"
    ranges:
      - [ 100, 200 ]
    state: present
    register: vnipool

- name: "Update VNI Pool by Name"
  aos_vni_pool:
    session: "{{ aos_session }}"
    name: "{{ vnipool.name }}"
    ranges:
      - [ 300, 400 ]
    state: present

- name: "Update VNI Pool by ID"
  aos_vni_pool:
    session: "{{ aos_session }}"
    id: "{{ vnipool.id }}"
    ranges:
      - [ 300, 400 ]
    state: present

- name: "Delete VNI Pool"
  aos_vni_pool:
    session: "{{ aos_session }}"
    name: "my-vni-pool"
    state: absent
'''

RETURNS = '''
name:
  description: Name of the VNI Pool
  returned: always
  type: str
  sample: Private-VNI-pool

id:
  description: AOS unique ID assigned to the VNI Pool
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
from library.aos_resource import VniPool


def vni_pool(module):
    """
    Main function to create, change or delete AOS VNI resource pool
    """
    margs = module.params
    target_state = margs['state']
    new_range = margs['ranges']

    pool = VniPool(module, margs['session'], module.check_mode)

    if 'ranges' in margs.keys():
        errors = pool.validate(new_range)

        if errors:
            pool.module_exit(error=errors,
                             name='', uuid='',
                             value='', changed=False)

    new_ranges = pool.get_ranges(new_range)

    existing = {}

    if margs['name'] is not None:
        name = margs['name']
        existing = pool.find_by_name(name)

    if margs['id'] is not None:
        uuid = margs['id']
        existing = pool.find_by_id(uuid)

    if target_state == 'present':
        if not existing:
            pool.create(new_ranges, margs['name'])
        else:
            pool.update(existing["display_name"],
                        existing["id"],
                        existing["ranges"],
                        new_ranges)

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
            ranges=dict(required=False, type="list", default=[])
        ),
        mutually_exclusive=[('name', 'id')],
        required_one_of=[('name', 'id')],
        supports_check_mode=True
    )

    vni_pool(module)


if __name__ == "__main__":
    main()
