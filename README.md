# Event-Driven Ansible for Red Hat Insights

`redhatinsights.eda.insights`


## Description

This collection contains event source plugin for receving events out of
[Red Hat Insights](https://console.redhat.com/insights).


## Installation

```
git clone https://github.com/RedHatInsights/ansible-collections-eda.git
ansible-galaxy collection install -U ./ansible-collections-eda
```

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
