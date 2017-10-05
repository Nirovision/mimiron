# Mimiron

[![Build Status](https://travis-ci.org/ImageIntelligence/mimiron.svg?branch=master)](https://travis-ci.org/ImageIntelligence/mimiron)
[![PyPI version](https://badge.fury.io/py/mimiron.svg)](https://badge.fury.io/py/mimiron)

**Welcome to mimiron!**

> [Mimiron](http://www.wowhead.com/npc=33350/mimiron) is one of the Titanic Watchers. He once resided at the Temple of Invention, but is absent during the time of Loken's rebellion.

Mimiron is a CLI tool that aims provide a better workflow when manging Terraform variables.

When all of your Terraform config is completely modular, the only sane way to manage variables is to store them inside a `variables.json` file and pass that along when you run `terraform apply -var-file=variables.json`... but where do you store `variables.json` and how can you easily make changes?

Our approach is to store non-sensitive variables inside the same repository as our Terraform config. Sensitive variables like your AWS secret and master db password are stored elsewhere and pulled in via environment variables e.g. `TF_VAR_aws_access_key`. Mimiron does **not** manage sensitive variables for you.

We want to make simple tasks such as bumping an image version simple and Mimiron is a small CLI tool that does that. Mimiron provides a few commands to help automate the cumbersome tasks away.

## Installation

```
$ pip install mimiron
```

Export necessary environment variables to let Mimiron know where your terraform repo is located:

```bash
# Path to your Terraform configuration
export TF_DEPLOYMENT_PATH="~/workspace/terraform"

# Docker username, password and organisation (or account)
export DOCKER_USERNAME=""
export DOCKER_PASSWORD=""
export DOCKER_ORG=""
```

There are also optional environment variables you can override:

```bash
export DEFAULT_ENVIRONMENT=staging
export DEFAULT_GIT_BRANCH=master
```

## Assumptions

* Your Terraform config repo has a dir `/terraform/tfvars/` with your tfvars in a JSON file e.g. `/terraform/tfvars/staging.json`
* Docker image artifacts are stored in the DockerHub registry
* Docker image artifacts are named `service_name_image` e.g. `web_marketing_image`

## Usage

```
>>> mim --help
mimiron.py

usage:
    mim (bump|b) <service> [--env=<env>] [--latest] [--no-push] [--show-all]
    mim (status|st) [--env=<env>]
    mim (deploy|d) [--show-last=<n>] [--no-push] [--tag] [--empty-commit]

commands:
    (bump|b)         bumps the <service> with an image <artifact>
    (status|st)      shows the currently used artifact id for <env>
    (deploy|d)       triggers a deploy a chosen deployment repository

arguments:
    <artifact>       the deployment artifact (Docker image) we are pushing
    <service>        the application we're targeting
    --env=<env>      overrides the default repo environment
    --show-all       show all artifacts for the current service
    --show-last=<n>  show the last n commits
    --empty-commit   creates an empty commit on the chosen repository
    --tag            creates a git tag (git tag -a) on a chosen commit or [--empty-commit]

options:
    --no-push        make local changes without pushing to remote
    --latest         use the latest artifact when updating a service

    -h --help        shows this
    -v --version     shows version
```

## Development

Clone the project:

```bash
git clone git@github.com:ImageIntelligence/mimiron.git
```

Setup your virtualenv:

```bash
mkvirtualenv mimiron
```

Attach mim to your shell:

```bash
python setup.py develop
pip install -r requirements.txt
```

Testing:

```bash
python -m pytest
```

## Deployment

Create a `~/.pypirc` and replace the username and password with real credentials:

```
[distutils]
index-servers =
  mimiron

[mimiron]
repository=https://pypi.python.org/pypi
username=xxx
password=yyy
```

Register this package to the Cheeseshop:

```
$ python setup.py register -r mimiron
```

Build a distributable and upload:

```
$ python setup.py sdist upload -r mimiron
```
