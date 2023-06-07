# Contributing

Please review [Ansible Community Guide](https://docs.ansible.com/ansible/devel/community/index.html)
and [Developing collections](https://docs.ansible.com/ansible/devel/dev_guide/developing_collections.html#contributing-to-collections)
guide prior to contributing to this collection.

## Environment setup

Create virtualenv and install dependencies:
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Running tests

Install test dependencies:
```
# source venv/bin/activate
pip install -r test_requirements.txt
```

Run tests:
```
# source venv/bin/activate
pytest
```
