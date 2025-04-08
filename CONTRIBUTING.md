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

Make sure you have java installed (required by ansible-rulebook) and JAVA_HOME environment variable is set e.g.:
```
export JAVA_HOME=/usr/lib/jvm/openjdk-jre-bin-17
```

Check for more information in [Ansible Rulebook documentation](https://ansible.readthedocs.io/projects/rulebook/en/latest/installation.html).


Run tests:
```
# source venv/bin/activate
pytest
```

## Publishing

To publish a new version of the collection increase the `version` within [`galaxy.yml`](galaxy.yml)
creating a pull request. Versions must follow [Semantic Versioninig](https://semver.org/)
guidelines.

When creating PR, also update CHANGELOG.md with changes added. If no code changes were added, update changelog with `Maintenance release` note. Having changelog updated with each release to Automation Hub is mandatory.

The collection is published to [Ansible Galaxy](https://galaxy.ansible.com/ui/repo/published/redhatinsights/eda/)
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

Also GH tag-and-release pipeline builds the collection and you can download the artifact from there.

To upload/update the collection in Automation hub manually, [navigate to](https://console.redhat.com/ansible/automation-hub/repo/published/redhat/insights_eda).
Upload collection file (without zip extension which is added by GH action) and upload it into stage repositories. Manual approval fro RH engineer is needed in order to get it published.
More information how to upload collection into automation hub can be found [here](https://docs.redhat.com/en/documentation/red_hat_ansible_automation_platform/2.5/html/managing_automation_content/managing-collections-hub#proc-uploading-collections).
