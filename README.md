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

### Integration with ServicNow Incidents

Rulebook example of creating ServiceNow Incidents out of selected Insights events, including:
* [Advisor recommendations](https://access.redhat.com/documentation/en-us/red_hat_insights/2023/html/assessing_rhel_configuration_issues_using_the_red_hat_insights_advisor_service/index)
* newly detected [vulnerabilities](https://access.redhat.com/documentation/en-us/red_hat_insights/2023/html/assessing_and_monitoring_security_vulnerabilities_on_rhel_systems/index)
* detected vulnerabilites with a known exploit

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
          name: snow_advisor_playbook.yaml
    - name: match vulnerability event
      condition: |-
        event.payload.application == "vulnerability"
        and event.payload.event_type in [
          "new-recommendation",
          "any-cve-known-exploit",
          "new-cve-cvss",
          "new-cve-severity",
          "new-cve-security-rule"
        ]
      action:
        run_playbook:
          name: snow_vulnerability_playbook.yaml
    - name: match compliance below threshold
      condition:
        event.payload.application == "compliance"
        and event.payload.event_type == "compliance-below-threshold"
      action:
        run_playbook:
          name: snow_compliance_playbook.yaml
```

Playbooks:

```yaml
# snow_advisor_playbook.yaml
---
- hosts: localhost
  gather_facts: no
  tasks:
  - name: Create an Advisor incident
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
        Policy: {{ item.payload.policy_name | default("") }} [{{ item.payload.policy_id | default("") }}]
        Policy threshold: {{ item.payload.policy_threshold | default("") }}
        Compliance score: {{ item.payload.compliance_score | default("") }}
        Bundle: {{ ansible_eda.event.payload.bundle | default("") }}
        Created at: {{ ansible_eda.event.payload.timestamp | default("") }}
    loop: "{{ ansible_eda.event.payload.events | default([]) }}"
```
```yaml
# snow_vulnerability_playbook.yaml
---
- hosts: localhost
  gather_facts: no
  tasks:
  - name: Create a Vulnerability incident
    servicenow.itsm.incident:
      instance:
        host: https://instance_id.service-now.com
        username: user
        password: pass
      state: new
      short_description: "{{ ansible_eda.event.payload.application | upper }}: Reported {{ item.payload.reported_cve | default('') }}"
      description: |-
        Account id: {{ ansible_eda.event.payload.account_id | default("") }}
        Affected system: {{ ansible_eda.event.payload.context.display_name | default("") }}
        Event type: {{ ansible_eda.event.payload.event_type | default("") }}
        CVSS scroe : {{ item.payload.cvss_score | default("") }}
        Known exploit: {{ item.payload.known_exploit | default("false") }}
        Has rule: {{ item.payload.has_rule | default("false") }}
        Impact id: {{ item.payload.impact_id | default("") }}
        Publish date: {{ item.payload.publish_date | default("") }}
        CVE url: https://access.redhat.com/security/cve/{{ item.payload.reported_cve | default('') }}
        Bundle: {{ ansible_eda.event.payload.bundle | default("") }}
        Created at: {{ ansible_eda.event.payload.timestamp | default("") }}
    loop: "{{ ansible_eda.event.payload.events | default([]) }}"
```
```yaml
# snow_compliance_playbook.yaml
---
- hosts: localhost
  gather_facts: no
  tasks:
  - name: Create a Compliance incident
    servicenow.itsm.incident:
      instance:
        host: https://instance_id.service-now.com
        username: user
        password: pass
      state: new
      short_description: "{{ ansible_eda.event.payload.application | upper }}: System is non compliant to SCAP policy"
      description: |-
        Account id: {{ ansible_eda.event.payload.account_id | default("") }}
        Affected system: {{ ansible_eda.event.payload.context.display_name | default("") }}
        Event type: {{ ansible_eda.event.payload.event_type | default("") }}
        Policy: {{ ansible_eda.event.payload.policy_name | default("") }} [{{ ansible_eda.event.payload.policy_name | default("id") }}]
        Policy threshold: {{ ansible_eda.event.payload.policy_threshold | default("") }}
        Compliance score: {{ ansible_eda.event.payload.compliance_score | default("") }}
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
