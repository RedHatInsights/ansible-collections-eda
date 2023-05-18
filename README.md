# Event-Driven Ansible for Red Hat Insights

`redhatinsights.eda.insights`


## Description

This collection contains the event source plugin for receiving events out of
[Red Hat Insights](https://console.redhat.com/insights).


## Installation

From source:
```
git clone https://github.com/RedHatInsights/ansible-collections-eda.git
ansible-galaxy collection install -U ./ansible-collections-eda
```
From Ansible Galaxy:
```
ansible-galaxy collection install redhatinsights.eda ansible-collections-eda
```


To set up an integration with Red Hat Insights please follow
[official documentation](https://access.redhat.com/documentation/en-us/red_hat_hybrid_cloud_console/2023/html/configuring_notifications_and_integrations_on_the_red_hat_hybrid_cloud_console/index).
Use integration type "Event-Driven Ansible" from the dropdown.

## Usage

```yaml
  sources:
    - redhatinsights.eda.insights:
        host:     # hostname to listen to. (default: 127.0.0.1)
        port:     # TCP port to listen to. (default: 5000)
        token:    # secret token.
        certfile: # (optional) path to a certificate file to enable TLS support
        keyfile:  # (optional) path to a key file to be used together with certfile
        password: # (optional) path to a key file to be used together with certfile
```

## Examples

Prerequisite for running examples is installed [Ansible Rulebook](https://ansible-rulebook.readthedocs.io/en/stable/installation.html).


To run an example execute:
```
SECRET=mysecret ansible-rulebook -r example_rulebook.yaml -v -E="SECRET" -i inventory.yaml
```
and set the `SECRET` value to your secret token value.
Use the secret value when setting up Ansible integration on
[Red Hat Hybrid Console](https://console.redhat.com/settings/integrations).

For inventory, you might create a file `inventory.yaml` containing:
```
all:
```


### Advisor Recommendation to ServiceNow Incident

Rulebook example of creating a ServiceNow Incident out of Insights Advisor recommendation events.

Prerequisites:
* `servicenow.itsm` collection installed

```yaml
# example_rulebook.yaml
- name: ServiceNow Incidents out of Red Hat Insights
  hosts: localhost
  sources:
    - redhatinsights.eda.insights:
        host: 0.0.0.0
        token: "{{ SECRET }}"
  rules:
    - name: match advisor recommendation event
      condition:
        event.payload.application == "advisor"
        and event.payload.event_type == "new-recommendation"
      action:
        run_playbook:
          name: example_playbook.yaml
```
```yaml
# example_playbook.yaml
---
- hosts: localhost
  gather_facts: no
  tasks:
  - name: Create an incident
    servicenow.itsm.incident:
      instance:
        host: https://instance_id.service-now.com
        username: user
        password: pass
      state: new
      short_description: "{{ ansible_eda.event.payload.application | upper }}: {{ item.payload.rule_description | default('Recommendation') }}"
      description: |-
        Account id: {{ ansible_eda.event.payload.account_id | default("") }}
        Affected system: {{ ansible_eda.event.payload.context.display_name | default("") }}
        Event type: {{ ansible_eda.event.payload.event_type | default("") }}
        Rule url : {{ item.payload.rule_url | default("") }}
        Reboot required: {{ item.payload.reboot_required | default("") }}
        Total risk: {{ item.payload.total_risk | default("") }}
        Has incident: {{ item.payload.has_incident | default("") }}
        Bundle: {{ ansible_eda.event.payload.bundle | default("") }}
        Created at: {{ ansible_eda.event.payload.timestamp | default("") }}
    loop: "{{ ansible_eda.event.payload.events | default([]) }}"
```

## Development

### Setting up environment

Create virtualenv and install dependencies:
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Running tests

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
