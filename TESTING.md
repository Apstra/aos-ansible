# Testing

#### Setup local Enviroment:

~~~~
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt -r test-requirements.txt
~~~~

#### Run test (tox)

NOTE: Ansible playbook `test_playbook.yaml` relies on the AOS instance
from `ansible.cfg` to be running or these tests will fail

~~~~
tox
~~~~

