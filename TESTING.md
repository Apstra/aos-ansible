# Testing

#### Setup local Enviroment:

~~~~
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt -r test-requirements.txt
~~~~

add enviroment variable to the venv for `inventory.ini`
~~~
export VAULT_PASSWORD=<password for inventory.ini>
~~~

Alternativley you can replace `inventory.ini` with an unencrypted
inventory of your own AOS test server.

#### Run test (tox)

NOTE: Ansible playbook `test_playbook.yaml` relies on the AOS instance
from `ansible.cfg` to be running or these tests will fail

~~~~
pip install -r requirements.txt
pip install -r test-requirements.txt
tox
~~~~

