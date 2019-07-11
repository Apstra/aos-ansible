# virtual_network
# (c) 2017 Apstra Inc, <community@apstra.com>

ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: aos_blueprint_virtual_network
author: ryan@apstra.com (@that1guy15)
version_added: "2.7"
short_description: Manage virtual networks (VLANs) within an AOS blueprint
description:
  - Create, update and manage virtual networks (VLANs) within an existing AOS 
    blueprint. Assign and manage fabric devices and interfaces assigned to a 
    virtual network.
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
  description:
    description:
      - short description of virtual network
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
      - Rack local or Inter-rack virtual network. 
    choices: ['vxlan' , 'vlan']  
    required: false
    default: vlan
    type: str
  security_zone:
    description:
      - ID of existing security zone to apply virtual network
    required: str
    default: default
    type: str
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
  endpoints:
    description:
      - enable virtual network for the given devices and interfaces
    required: false
    type: dict
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
  virtual_mac:
    description:
      - Virtual mac address used for gateway
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
    type: str
  vtep_ips:
    description: 
      - IP pool used for VTEP IP assignment if address not statically assigned
    required: false
    type: dict
  vni_ips:
    description: 
      - IP pool used for VNI IP assignment if address not statically assigned
    required: false
    type: dict
'''
#TODO: Add examples
EXAMPLES = '''


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


import ipaddress
from ansible.module_utils.basic import AnsibleModule
from library.aos import aos_get, aos_put


ENDPOINT = '/virtual-networks'



def virtual_network(module):
    """
    Main function to create, change or delete virtual networks within an
    AOS blueprint
    """
    margs = module.params

    endpoint = 'blueprints/{}/virtual-networks'.format(margs['blueprint_id'])

    name = margs.get('name', None)
    uuid = margs.get('id', None)
    vni_id = margs.get('vni_id', None)
    vlan_id = margs.get('vlan_id', None)


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
            description=dict(required=False),
            vni_id=dict(required=False),
            vlan_id=dict(required=False),
            sec_zone=dict(required=False),
            ipv4_enable=dict(required=False, type='bool'),
            ipv6_enable=dict(required=False, type='bool'),
            ipv4_subnet=dict(required=False),
            ipv6_subnet=dict(required=False),
            virtual_gw_ipv4=dict(required=False),
            virtual_gw_ipv6=dict(required=False),
            virtual_mac=dict(required=False),
            svi_ips=dict(required=False, type='dict'),
            vtep_ips=dict(required=False, type='dict'),
            vni_ips=dict(required=False, type='dict'),
            dhcp_service=dict(required=False),
            endpoints=dict(required=False, type='dict'),
        ),
        mutually_exclusive=[('name', 'id')],
        required_one_of=[('name', 'id')],
        supports_check_mode=True
    )

    virtual_network(module)


if __name__ == "__main__":
    main()
