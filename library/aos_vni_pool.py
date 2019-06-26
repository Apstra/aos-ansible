# (c) 2017 Apstra Inc, <community@apstra.com>


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
    type: dict
  name:
    description:
      - Name of the VNI Pool to manage.
        Only one of I(name) or I(id)can be set.
    required: false
    type: str    
  id:
    description:
      - AOS Id of the VNI Pool to manage.
         Only one of I(name) or I(id)can be set.
    required: false
    type: str     
  state:
    description:
      - Indicates the expected state of the VNI Pool (present or absent).
    default: present
    choices: ['present', 'absent']
    required: false
    type: str
  ranges:
    description:
      - List of VNIs ranges to add to the VNI Pool. Each range (list) must have
        2 values. A start of range and an end of range.
    required: false
    type: list    
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
from library.aos import aos_post, aos_put, aos_delete, find_resource_item

ENDPOINT = 'resources/vni-pools'


def validate_ranges(ranges):
    """
    Validate VNI ranges provided are valid and properly formatted
    :param ranges: list
    :return: list
    """
    errors = []

    for vni_range in ranges:
        if not isinstance(vni_range, list):
            errors.append("Invalid range: must be a list")
        elif len(vni_range) != 2:
            errors.append("Invalid range: must be a list of 2 members")
        elif any(map(lambda r: not isinstance(r, int), vni_range)):
            errors.append("Invalid range: Expected integer values")
        elif vni_range[1] <= vni_range[0]:
            errors.append("Invalid range: 2nd element must be bigger than 1st")
        elif vni_range[0] <= 4095 or vni_range[1] >= 16777213:
            errors.append("Invalid range: must be a valid range between 4096"
                          " and 16777214")

    return errors


def get_ranges(pool):
    """
    convert VNI pool list to dict format
    :param pool: list
    :return: dict
    """
    return [{"first": r[0], "last": r[1]} for r in pool]


def vni_pool_absent(module, session, my_pool):
    """
    Remove VNI pool if exist and is not in use
    :param module: Ansible built in
    :param session: dict
    :param my_pool: dict
    :return: success(bool), changed(bool), results(dict)
    """

    # If the resource does not exist, return directly
    if not my_pool:
        return True, False, {'display_name': '',
                             'id': '',
                             'msg': 'Pool does not exist'}

    if my_pool['status'] != 'not_in_use':

        return False, False, {"msg": "Unable to delete VNI Pool {},"
                              " currently in use".format(my_pool['display_name'])}

    if not module.check_mode:
        aos_delete(session, ENDPOINT, my_pool['id'])

        return True, True, my_pool

    return True, False, my_pool


def vni_pool_present(module, session, my_pool):
    """
    Create new VNI pool or modify existing pool
    :param module: Ansible built in
    :param session: dict
    :param my_pool: dict
    :return: success(bool), changed(bool), results(dict)
    """
    margs = module.params

    if not my_pool:

        if 'name' not in margs.keys():
            return False, False, {"msg": "name required to create a new resource"}

        new_pool = {"ranges": get_ranges(margs['ranges']),
                    "display_name": margs['name'],
                    "id": margs['name']}

        if not module.check_mode:
            aos_post(session, ENDPOINT, new_pool)

            return True, True, new_pool

        return True, False, new_pool

    else:
        if my_pool['ranges']:

            endpoint_put = "{}/{}".format(ENDPOINT, my_pool['id'])

            new_pool = {"ranges": get_ranges(margs['ranges']),
                        "display_name": my_pool['display_name'],
                        "id": my_pool['id']}

            for vni_range in my_pool['ranges']:
                new_pool['ranges'].append({'first': vni_range['first'],
                                           'last': vni_range['last']})

            if not module.check_mode:
                aos_put(session, endpoint_put, new_pool)

                return True, True, new_pool

            return True, False, new_pool

        return True, False, my_pool


def vni_pool(module):
    """
    Main function to create, change or delete AOS VNI resource pool
    """
    margs = module.params

    name = None
    uuid = None

    if margs['name'] is not None:
        name = margs['name']

    elif margs['id'] is not None:
        uuid = margs['id']

    if 'ranges' in margs.keys():
        errors = validate_ranges(margs['ranges'])

        if errors:
            module.fail_json(msg=errors)

    my_pool = find_resource_item(margs['session'], ENDPOINT,
                                 name=name, uuid=uuid)

    if margs['state'] == 'absent':
        success, changed, results = vni_pool_absent(module,
                                                    margs['session'],
                                                    my_pool)

    elif margs['state'] == 'present':
        success, changed, results = vni_pool_present(module,
                                                     margs['session'],
                                                     my_pool)

    if success:
        module.exit_json(changed=changed, name=results['display_name'],
                         id=results['id'], value=results)
    else:
        module.fail_json(msg=results)


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
