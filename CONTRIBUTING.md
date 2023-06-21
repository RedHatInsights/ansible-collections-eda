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

## Publishing

To publish a new version of the collection increase the `version` within [`galaxy.yml`](galaxy.yml)
creating a pull request. Versions must follow [Semantic Versioninig](https://semver.org/)
guidelines.

The collection is published to [Ansible Galaxy](https://galaxy.ansible.com/redhatinsights/eda)
automatically with GitHub action [tag-and-release](.github/workflows/tag-and-release.yaml).
The action tags latest commit with a version tag from [`galaxy.yml`](galaxy.yml)'s version value, builds the collection and uploads it. Version tags follow the format: `vX.Y.Z`.

Note: that the GitHub project requires a valid Ansible Galaxy API Key set as `ANSIBLE_GALAXY_APIKEY`
by an administrator.

### Building for Automation Hub

To build the collection for Automation Hub run playbook `productize.yml` from the project root.
The playbook would build a collection tar used for publishing to Automation Hub
under the namespace `redhat` and name `insights_eda`.

```
ansible-playbook productize.yml
```
