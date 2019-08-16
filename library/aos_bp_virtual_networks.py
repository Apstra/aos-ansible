# virtual_network
# (c) 2017 Apstra Inc, <community@apstra.com>

ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: aos_bp_virtual_networks
author: ryan@apstra.com (@that1guy15)
version_added: "2.7"
short_description: Manage virtual networks (VLANs) within an AOS blueprint
description:
  - Create, update and manage virtual networks (VLANs) within an existing AOS
    blueprint. Assign and manage fabric devices to a virtual network.
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
      - Name of virtual network, as defined by AOS when created.
    required: false
    type: str
  id:
    description:
      - ID of virtual network, as defined by AOS when created.
    required: false
    type: str
  state:
    description:
      - Indicates the expected state of the virtual network.
    default: present
    choices: ['present', 'absent']
    required: false
    type: str
  vn_id:
    description:
      - VLAN ID number used by devices.
    choices: 1 - 4094
    required: false
    type: int
  vn_type:
    description:
      - Rack local or Inter-rack virtual network using vxlan.
    choices: ['vxlan' , 'vlan']
    required: false
    default: vlan
    type: str
  sec_zone_id:
    description:
      - ID of existing security zone to apply virtual network
    required: str
    default: default
    type: str
  bound_to_name:
    description:
      - enable virtual network to be used on the given leaf switches
        by blueprint hostname.
    required: true
    type: list
  bound_to_id:
    description:
      - enable virtual network to be used on the given leaf switches
        by blueprint node id.
    required: true
    type: list
  ipv4_enabled:
    description:
      - enable virtual network for use with IPv4 networks
    required: false
    type: bool
  ipv6_enabled:
    description:
      - enable virtual network for use with IPv6 networks
    required: false
    type: bool
  ipv4_subnet:
    description:
      - IPv4 subnet assigned to virtual network
    required: false
    type: str
  ipv6_subnet:
    description:
      - IPv4 subnet assigned to virtual network
    required: false
    type: str
  virtual_gw_ipv4:
    description:
      - Gateway used for IPv4 network
    required: false
    type: str
  virtual_gw_ipv6:
    description:
      - Gateway used for IPv6 network
    required: false
    type: str
  svi_ips:
    description:
      - IP pool used to assign the virtual network SVI
    required: false
    type: dict
  dhcp_service:
    description:
      - IP of DHCP server for relay services
    required: false
    type: bool
'''

EXAMPLES = '''
- name: Create new vxlan VN on Rack1 and Rack2 leaf1
    local_action:
      module: aos_bp_virtual_networks
      session: "{{ aos_session }}"
      blueprint_id: "{{bp_id}}"
      name: "my-virt-net"
      vn_type: "vxlan"
      bound_to_name:
          - "rack_001_leaf1"
          - "rack_002_leaf1"
      state: present
    register: test_vn

- name: Update existing VN (by ID) to include Rack3 leaf1
    local_action:
      module: aos_bp_virtual_networks
      session: "{{ aos_session }}"
      blueprint_id: "{{bp_id}}"
      id: "{{test_vn.id}}"
      vn_type: "vxlan"
      bound_to_name:
          - "rack_001_leaf1"
          - "rack_002_leaf1"
          - "rack_003_leaf1"
      state: present

- name: Delete a given list of VNs by name
    local_action:
      module: aos_bp_virtual_networks
      session: "{{ aos_session }}"
      blueprint_id: "{{bp_id}}"
      name: "{{ item }}"
      state: absent
    register: vn_test
    with_items:
      - 'my-virt-net'
      - 'my-virt-net2'
'''

RETURNS = '''
vn_id:
  description: ID of the AOS virtual network created
  returned: always
  type: string
  sample: "db6588fe-9f36-4b04-8def-89e7dcd00c17"
vn_name:
  description: name of the AOS virtual network created
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
from library.aos import aos_get, aos_post, aos_put, aos_delete, validate_vlan_id, \
    validate_vni_id, validate_ip_format, find_bp_system_nodes


ENDPOINT = '/virtual-networks'


def vn_add_otions(new_vn, vn_id, ipv4_enabled, ipv6_enabled, ipv4_subnet,
                  ipv6_subnet, virtual_gw_ipv4, virtual_gw_ipv6, dhcp_service):
    if vn_id:
        new_vn["vn_id"] = str(vn_id)

    if ipv4_enabled:
        new_vn["ipv4_enabled"] = ipv4_enabled

    if ipv6_enabled:
        new_vn["ipv6_enabled"] = ipv6_enabled

    if ipv4_subnet:
        new_vn["ipv4_subnet"] = ipv4_subnet

    if ipv6_subnet:
        new_vn["ipv6_subnet"] = ipv6_subnet

    if virtual_gw_ipv4:
        new_vn["virtual_gw_ipv4"] = virtual_gw_ipv4

    if virtual_gw_ipv6:
        new_vn["virtual_gw_ipv6"] = virtual_gw_ipv6

    if dhcp_service:
        new_vn["dhcp_service"] = 'dhcpServiceEnabled'
    else:
        new_vn["dhcp_service"] = 'dhcpServiceDisabled'


def virt_net_absent(module, session, endpoint, my_vn):
    """
    Remove virtual-network if exist and is not in use
    :param module: Ansible built in
    :param session: dict
    :param endpoint: str
    :param my_vn: dict
    :return: success(bool), changed(bool), results(dict)
    """
    if not my_vn:
        return True, False, {'label': '',
                             'id': '',
                             'msg': 'security-zone does not exist'}

    if not module.check_mode:
        aos_delete(session, endpoint, my_vn['id'])

        return True, True, my_vn

    return True, False, my_vn


def virt_net_present(module, session, endpoint, my_vn, vn_id, sec_zone_id,
                     ipv4_enabled, ipv6_enabled, ipv4_subnet, ipv6_subnet,
                     virtual_gw_ipv4, virtual_gw_ipv6, bound_to, dhcp_service):
    """
    Create new virtual-network or modify existing pool
    :param module: Ansible built in
    :param session: dict
    :param endpoint: str
    :param my_vn: dict
    :param vn_id: str
    :param sec_zone_id: str
    :param ipv4_enabled: bool
    :param ipv6_enabled: bool
    :param ipv4_subnet: bool
    :param ipv6_subnet: bool
    :param virtual_gw_ipv4: str
    :param virtual_gw_ipv6: str
    :param bound_to: list
    :param dhcp_service: bool
    :return: success(bool), changed(bool), results(dict)
    """
    margs = module.params

    if not my_vn:

        if 'name' not in margs.keys():
            return False, False, {"msg": "name required to create a new "
                                         "virtual-network"}

        new_vn = {"vn_type": margs['vn_type'],
                  "label": margs['name'],
                  "bound_to": bound_to,
                  "sec_zone_id": sec_zone_id
                  }

        if sec_zone_id:
            new_vn["security_zone_id"] = sec_zone_id

        vn_add_otions(new_vn, vn_id, ipv4_enabled, ipv6_enabled,
                      ipv4_subnet, ipv6_subnet, virtual_gw_ipv4,
                      virtual_gw_ipv6, dhcp_service)

        if not module.check_mode:
            resp = aos_post(session, endpoint, new_vn)

            new_vn['id'] = resp['id']

            return True, True, new_vn

        return True, False, new_vn

    else:

        endpoint_put = "{}/{}".format(endpoint, my_vn['id'])

        new_vn = {"vn_type": my_vn['vn_type'],
                  "label": my_vn['label'],
                  "bound_to": bound_to,
                  "id": my_vn['id']
                  }

        vn_add_otions(new_vn, vn_id, ipv4_enabled, ipv6_enabled,
                      ipv4_subnet, ipv6_subnet, virtual_gw_ipv4,
                      virtual_gw_ipv6, dhcp_service)

        if not module.check_mode:
            aos_put(session, endpoint_put, new_vn)

            return True, True, new_vn

        return True, False, my_vn


def virtual_network(module):
    """
    Main function to create, change or delete virtual networks within an
    AOS blueprint
    """
    margs = module.params

    endpoint = 'blueprints/{}/virtual-networks'.format(margs['blueprint_id'])

    name = margs.get('name', None)
    uuid = margs.get('id', None)
    vn_id = margs.get('vn_id', None)
    sec_zone_id = margs.get('sec_zone_id', None)
    ipv4_enabled = margs.get('ipv4_enabled', False)
    ipv6_enabled = margs.get('ipv6_enabled', False)
    ipv4_subnet = margs.get('ipv4_subnet', None)
    ipv6_subnet = margs.get('ipv6_subnet', None)
    virtual_gw_ipv4 = margs.get('virtual_gw_ipv4', None)
    virtual_gw_ipv6 = margs.get('virtual_gw_ipv6', None)
    dhcp_service = margs.get('dhcp_service', True)
    bound_to_id = margs.get('bound_to_id', [])
    bound_to_name = margs.get('bound_to_name', [])

    errors = []

    if vn_id and margs['vn_type'] == 'vlan':
        try:
            vn_id = int(vn_id)
        except ValueError:
            module.fail_json(msg="Invalid ID: must be an integer")

        err = validate_vlan_id(vn_id)

        if err:
            errors.append(err)

    elif vn_id and margs['vn_type'] == 'vxlan':
        try:
            vn_id = int(vn_id)
        except ValueError:
            module.fail_json(msg="Invalid ID: must be an integer")

        err = validate_vni_id(vn_id)

        if err:
            errors.append(err)

    for i in [ipv4_subnet, virtual_gw_ipv4]:
        if i:
            err = validate_ip_format([i], 'ipv4')

            if err:
                errors.append(err)

    for i in [ipv6_subnet, virtual_gw_ipv6]:
        if i:
            err = validate_ip_format([i], 'ipv6')

            if err:
                errors.append(err)

    if errors:
        module.fail_json(msg=errors)

    bound_to = []
    if bound_to_id:
        for n in bound_to_id:
            bound_to.append({"system_id": n})
    elif bound_to_name:
        node_data = find_bp_system_nodes(margs['session'],
                                         margs['blueprint_id'],
                                         bound_to_name)

        if node_data:
            for n in node_data:
                bound_to.append({"system_id": n['id']})
        else:
            module.fail_json(msg="System Node not found by name")

    vn_data = aos_get(margs['session'], endpoint)
    my_vn = {}

    if not uuid:
        if vn_data:
            for k, v in vn_data['virtual_networks'].items():
                if v['label'] == name:
                    my_vn = v
    else:
        if vn_data:
            for k, v in vn_data['virtual_networks'].items():
                if v['id'] == uuid:
                    my_vn = v

    if margs['state'] == 'absent':
        success, changed, results = virt_net_absent(module, margs['session'],
                                                    endpoint, my_vn)

    elif margs['state'] == 'present':
        success, changed, results = virt_net_present(module, margs['session'],
                                                     endpoint, my_vn, vn_id,
                                                     sec_zone_id, ipv4_enabled,
                                                     ipv6_enabled, ipv4_subnet,
                                                     ipv6_subnet, virtual_gw_ipv4,
                                                     virtual_gw_ipv6, bound_to,
                                                     dhcp_service)

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
                       default="present"),
            vn_id=dict(required=False),
            vn_type=dict(required=False,
                         choices=['vlan', 'vxlan'],
                         default="vlan"),
            sec_zone_id=dict(required=False),
            ipv4_enabled=dict(required=False, type='bool'),
            ipv6_enabled=dict(required=False, type='bool'),
            bound_to_id=dict(required=False, type='list',
                             default=[]),
            bound_to_name=dict(required=False, type='list',
                               default=[]),
            ipv4_subnet=dict(required=False),
            ipv6_subnet=dict(required=False),
            virtual_gw_ipv4=dict(required=False),
            virtual_gw_ipv6=dict(required=False),
            svi_ips=dict(required=False, type='dict'),
            dhcp_service=dict(required=False, type='bool'),
        ),
        mutually_exclusive=[('name', 'id'),
                            ('bound_to_id', 'bound_to_name')],
        required_one_of=[('name', 'id')],
        required_if=[
            ["state", "present", ["bound_to_name"], ["bound_to_id"]]
        ],
        supports_check_mode=True
    )

    virtual_network(module)


if __name__ == "__main__":
    main()
