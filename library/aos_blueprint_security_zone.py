# (c) 2017 Apstra Inc, <community@apstra.com>

ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: aos_blueprint_security_zone
author: ryan@apstra.com (@that1guy15)
version_added: "2.7"
short_description: Manage security-zones within an AOS blueprint
description:
  - Create, update and manage security-zones within an existing AOS
    blueprint.
options:
  session:
    description:
      - Session details from aos_login generated session.
    required: true
    type: dict
  blueprint_id:
    description:
      - Name of blueprint, as defined by AOS when created
    required: true
    type: str
  name:
    description:
      - Name of security-zone and vrf.
    required: false
    type: str
  id:
    description:
      - ID of virtual network, as defined by AOS when created.
    required: false
    type: str
  state:
    description:
      - Indicates the expected state of the security-zone.
    default: present
    choices: ['present', 'absent']
    required: false
    type: str
  vni_id:
    description:
      - VNI ID number used by security-zone.
    choices: 4094 - 16777214
    required: false
    type: int
  vlan_id:
    description:
      - VLAN ID number used by security-zone.
    choices: 1 - 4094
    required: false
    type: int
  routing_policy:
    description:
      - Import and export policies along with aggregate and
        extra prefix definition
    required: false
    type: dict
'''

EXAMPLES = '''

- name: Deploy Blueprint DC1-EVPN by name
  aos_blueprint_deploy:
    session: "{{ aos_session }}"
    name: 'DC1-EVPN'

'''

RETURNS = '''
sz_id:
  description: ID of the AOS security-zone created
  returned: always
  type: string
  sample: "db6588fe-9f36-4b04-8def-89e7dcd00c17"
sz_name:
  description: name of the AOS security-zone created
  returned: always
  type: string
  sample: "vlan-101"
value:
  description: Value of the object as returned by the AOS Server
  returned: always
  type: dict
  sample: {'...'}
'''


from ansible.module_utils.basic import AnsibleModule
from library.aos import aos_get, aos_post, aos_put, aos_delete

ENDPOINT = 'security-zones'


def validate_vni_id(vni_id):
    """
    Validate VNI ID provided is an acceptable value
    :param vni_id: int
    :return: list
    """
    errors = []
    if vni_id <= 4095 or vni_id >= 16777213:
        errors.append("Invalid ID: must be a valid VNI number between 4096"
                      " and 16777214")

    return errors


def validate_vlan_id(vlan_id):
    """
    Validate VLAN ID provided is an acceptable value
    :param vlan_id: int
    :return: list
    """
    errors = []
    if vlan_id <= 1 or vlan_id > 4094:
        errors.append("Invalid ID: must be a valid vlan id between 1"
                      " and 4094")

    return errors


def sec_zone_absent(module, session, endpoint, my_sz):
    """
        Remove security-zone if exist and is not in use
        :param module: Ansible built in
        :param session: dict
        :param endpoint: str
        :param my_sz: dict
        :return: success(bool), changed(bool), results(dict)
        """
    if not my_sz:
        return True, False, {'display_name': '',
                             'id': '',
                             'msg': 'security-zone does not exist'}

    if not module.check_mode:
        aos_delete(session, endpoint, my_sz['id'])

        return True, True, my_sz

    return True, False, my_sz


def sec_zone_present(module, session, endpoint, my_sz, vni_id, vlan_id):
    """
        Create new security-zone or modify existing pool
        :param module: Ansible built in
        :param session: dict
        :param endpoint: str
        :param my_sz: dict
        :param vni_id: int
        :param vlan_id: int
        :return: success(bool), changed(bool), results(dict)
        """
    margs = module.params

    if not my_sz:

        if 'name' not in margs.keys():
            return False, False, {"msg": "name required to create a new "
                                         "security-zone"}

        new_sz = {"sz_type": "evpn",
                  "label": margs['name'],
                  "vrf_name": margs['name']}

        if vni_id:
            new_sz["vni_id"] = vni_id

        if vlan_id:
            new_sz["vlan_id"] = vlan_id

        if not module.check_mode:
            resp = aos_post(session, endpoint, new_sz)

            new_sz['id'] = resp['id']

            return True, True, new_sz

        return True, False, new_sz

    else:
        if vni_id or vlan_id:

            endpoint_put = "{}/{}".format(endpoint, my_sz['id'])

            new_sz = {"sz_type": "evpn",
                      "label": my_sz['label'],
                      "vrf_name": my_sz['vrf_name'],
                      "id": my_sz['id']}

            if vni_id:
                new_sz["vni_id"] = vni_id

            if vlan_id:
                new_sz["vlan_id"] = vlan_id

            if not module.check_mode:
                aos_put(session, endpoint_put, new_sz)

                return True, True, new_sz

            return True, False, new_sz

        return True, False, my_sz


def sec_zone(module):
    """
    Main function to create, change or delete security zones within an AOS blueprint
    """
    margs = module.params

    endpoint = 'blueprints/{}/security-zones'.format(margs['blueprint_id'])

    name = margs.get('name', None)
    uuid = margs.get('id', None)
    vni_id = margs.get('vni_id', None)
    vlan_id = margs.get('vlan_id', None)

    if vni_id:
        try:
            vni_id = int(vni_id)
        except ValueError:
            module.fail_json(msg="Invalid ID: must be an integer")

        errors = validate_vni_id(vni_id)

        if errors:
            module.fail_json(msg=errors)

    if vlan_id:
        try:
            vlan_id = int(vlan_id)
        except ValueError:
            module.fail_json(msg="Invalid ID: must be an integer")

        errors = validate_vlan_id(vlan_id)

        if errors:
            module.fail_json(msg=errors)

    sz_data = aos_get(margs['session'], endpoint)
    my_sz = {}

    if not uuid:

        for k, v in sz_data['items'].items():
            if v['label'] == name:
                my_sz = v
    else:

        for k, v in sz_data['items'].items():
            if v['id'] == uuid:
                my_sz = v

    if margs['state'] == 'absent':
        success, changed, results = sec_zone_absent(module, margs['session'],
                                                    endpoint, my_sz)

    elif margs['state'] == 'present':
        success, changed, results = sec_zone_present(module, margs['session'],
                                                     endpoint, my_sz, vni_id,
                                                     vlan_id)

    if success:
        module.exit_json(changed=changed, name=results['label'],
                         id=results['id'], value=results)
    else:
        module.fail_json(msg=results)


def main():
    """
    Main function to setup inputs
    """
    module = AnsibleModule(
        argument_spec=dict(
            session=dict(required=True, type='dict'),
            blueprint_id=dict(required=True,),
            name=dict(required=False),
            id=dict(required=False),
            state=dict(required=False,
                       choices=['present', 'absent'],
                       default="present",),
            vni_id=dict(required=False),
            vlan_id=dict(required=False),
        ),
        mutually_exclusive=[('name', 'id')],
        required_one_of=[('name', 'id')],
        supports_check_mode=True
    )

    sec_zone(module)


if __name__ == "__main__":
    main()
