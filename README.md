
    
# AOS Ansible Modules

Ansible modules used to interact with Apstra AOS.

## Current Modules

### Generic
* aos_login

### Resources
* aos_asn_pool
* aos_vni_pool
* aos_ip_pool

### Blueprint
* aos_blueprint_deploy

## Installation
Clone repo into Library directory of your Ansible project

`cd ./library
git clone https://github.com/Apstra/aos-ansible.git`

Install aos-ansible requrements

`cd aos-ansible
pip install -r requirements.txt`

Add library reference to ansible.cfg if not in standard project library


## Contribution
[Adding new modules or roles](https://github.com/Apstra/aos-ansible/blob/develop/CONTRIBUTING.md)

# License
Apache 2.0
