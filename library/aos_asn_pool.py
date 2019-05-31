# (c) 2017 Apstra Inc, <community@apstra.com>


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
  - Apstra AOS ASN Pool module lets you manage your ASN Pools easily. You can
    create and delete ASN Pools by Name or ID. This
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
        Only one of I(name) or I(id) can be set.
  id:
    description:
      - AOS Id of the ASN Pool to manage.
        Only one of I(name) or I(id)can be set.
  state:
    description:
      - Indicates the expected state of the ASN Pool (present or absent).
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


def validate_ranges(ranges):
    """
    Validate ASN ranges provided are valid and properly formatted
    :param ranges: list
    :return: bool
    """
    errors = []

    for asn_range in ranges:
        if not isinstance(asn_range, list):
            errors.append("Invalid range: must be a list")
        elif len(asn_range) != 2:
            errors.append("Invalid range: must be a list of 2 members")
        elif any(map(lambda r: not isinstance(r, int), asn_range)):
            errors.append("Invalid range: Expected integer values")
        elif asn_range[1] <= asn_range[0]:
            errors.append("Invalid range: 2nd element must be bigger than 1st")

    return errors


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
    :return: success(bool), changed(bool), results(dict)
    """

    # If the resource does not exist, return directly
    if not my_pool:
        return True, False, {'display_name': '',
                             'id': '',
                             'msg': 'Pool does not exist'}

    if my_pool['status'] != 'not_in_use':

        return False, False, {"msg": "Unable to delete ASN Pool {},"
                              " currently in use".format(my_pool['display_name'])}

    if not module.check_mode:
        aos_delete(session, ENDPOINT, my_pool['id'])

        return True, True, my_pool

    return True, False, my_pool


def asn_pool_present(module, session, my_pool):
    """
    Create new ASN pool or modify existing pool
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

            for asn_range in my_pool['ranges']:
                new_pool['ranges'].append({'first': asn_range['first'],
                                           'last': asn_range['last']})

            if not module.check_mode:
                aos_put(session, endpoint_put, new_pool)

                return True, True, new_pool

            return True, False, new_pool

        return True, False, my_pool


def asn_pool(module):
    """
    Main function to create, change or delete AOS ASN resource pool
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
        success, changed, results = asn_pool_absent(module,
                                                    margs['session'],
                                                    my_pool)

    elif margs['state'] == 'present':
        success, changed, results = asn_pool_present(module,
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

    asn_pool(module)


if __name__ == "__main__":
    main()
