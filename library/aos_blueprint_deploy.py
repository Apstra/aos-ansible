# (c) 2017 Apstra Inc, <community@apstra.com>

#

ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: aos_blueprint_deploy
author: ryan@apstra.com (@that1guy15)
version_added: "2.7"
short_description: Deploy staged blueprint in AOS
description:
  - Deploy staged blueprint changes in AOS. Changes to blueprint will be
    deployed to all devices in the bluerint.
options:
  session:
    description:
      - Session details from aos_login generated session.
    required: true
  name:
    description:
      -Name of blueprint, as defined by AOS when created.
    required: Np
  id:
    description:
      - ID of blueprint, as defined by AOS when created.
    required: No
'''

EXAMPLES = '''

- name: Deploy Blueprint DC1-EVPN by name
  aos_blueprint_deploy:
    session: "{{ aos_session }}"
    name: 'DC1-EVPN'

- name: Deploy Blueprint DC1-EVPN by id
  aos_blueprint_deploy:
    session: "{{ aos_session }}"
    id: "{{ aos_blueprint_id }}"
'''

RETURNS = '''
blueprint_id:
  description: ID of the AOS blueprint deployed
  returned: always
  type: string
  sample: "db6588fe-9f36-4b04-8def-89e7dcd00c17"
'''


from ansible.module_utils.basic import AnsibleModule
from library.aos import aos_get, aos_put

ENDPOINT = 'blueprints'


def get_blueprint_status(session, blueprint_id):
    endpoint = "{}/{}/deploy".format(ENDPOINT, blueprint_id)

    resp_data = aos_get(session, endpoint)

    return resp_data


def get_blueprint_version(session, blueprint_id):
    endpoint = "{}/{}".format(ENDPOINT, blueprint_id)

    resp_data = aos_get(session, endpoint)

    return resp_data['version']


def get_blueprint_id(session, blueprint_name):
    endpoint = "blueprints"

    resp_data = aos_get(session, endpoint)

    for i in resp_data['items']:
        if i['label'] == blueprint_name:
            return i['id']

    return None


def aos_blueprint_deploy(module):
    mod_args = module.params

    if mod_args['id']:
        blueprint_id = mod_args['id']
    else:
        blueprint_id = get_blueprint_id(mod_args['session'], mod_args['name'])

    endpoint = "{}/{}/deploy".format(ENDPOINT, blueprint_id)

    staged_version = get_blueprint_version(mod_args['session'],
                                           blueprint_id)
    deployed_version = get_blueprint_status(mod_args['session'],
                                            blueprint_id)['version']

    if staged_version == deployed_version:
        module.exit_json(changed=False,
                         ansible_facts=dict(blueprint_id=blueprint_id))

    payload = {"version": staged_version}

    response = aos_put(mod_args['session'], endpoint, payload)

    if response.ok:

        bp_status = get_blueprint_status(mod_args['session'], blueprint_id)

        if bp_status['state'] == 'failure':
            module.fail_json(msg="Unable to commit blueprint: {}"
                             .format(bp_status['error']))

        else:
            module.exit_json(changed=True,
                             ansible_facts=dict(blueprint_id=blueprint_id))

    else:
        error_message = str(response)
        try:
            error_message = response.json().get('errors')
        except (TypeError, ValueError) as e:
            module.fail_json(
                msg="Failed to decode JSON from response: {}, error: {}"
                    .format(response, e))

        module.fail_json(
            msg="Issue deploying blueprint {}: {}"
                .format(blueprint_id, error_message))


def main():
    module = AnsibleModule(
        argument_spec=dict(
            session=dict(required=True, type="dict"),
            name=dict(required=False),
            id=dict(required=False)
        ),
        mutually_exclusive=[('name', 'id')],
        required_one_of=[('name', 'id')],
        supports_check_mode=False
    )

    aos_blueprint_deploy(module)


if __name__ == '__main__':
    main()
