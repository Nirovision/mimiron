# Mimiron

[![Build Status](https://travis-ci.org/ImageIntelligence/mimiron.svg?branch=master)](https://travis-ci.org/ImageIntelligence/mimiron)
[![PyPI version](https://badge.fury.io/py/mimiron.svg)](https://badge.fury.io/py/mimiron)

**Welcome to mimiron!**

> [Mimiron](http://www.wowhead.com/npc=33350/mimiron) is one of the Titanic Watchers. He once resided at the Temple of Invention, but is absent during the time of Loken's rebellion.

Mimiron is a CLI tool whose purpose is to provide a better workflow when manging tfvars.

When all of your Terraform config is completely modular, the only sane way to manage variables is to store them inside a `variables.json` file and pass that along when you run `terraform apply -var-file=variables.json`... but where do you store `variables.json`?

Our approach is to store non-critical variables inside the same repository as our Terraform config. Critical variables like AWS secrets, database master password are stored elsewhere and pulled in via environment variables e.g. `TF_VAR_AWS_ACCESS_KEY`.

We want to make simple tasks such as bumping an image version simple and Mimiron is a small CLI tool that does that. Mimiron provides a few commands to help automate the cumbersome tasks away.

## Installation

```
$ pip install mimiron
```

You also need to specify a few environment variables to let Mimiron know where your terraform and tfvar repos are located:

```bash
export TF_DEPLOYMENT_PATH="~/workspace/terraform"
export DOCKER_USERNAME=""
export DOCKER_PASSWORD=""
export DOCKER_ORG=""
```

## Assumptions

* Your Terraform config repo has a dir `/terraform/tfvars/` with your tfvars in a JSON file e.g. `/terraform/tfvars/staging.json`
* Docker image artifacts are stored in the DockerHub registry
* Docker image artifacts are named `service_name_image` e.g. `web_marketing_image`
* AMI artifacts are named `service_name_ami_id` e.g. `web_marketing_ami_id`

## Usage

```
>>> mim --help
mimiron.py

usage:
    mim bump <service> <env> [--latest] [--no-push]
    mim status <env>

commands:
    bump          bumps the <service> with an image <artifact>
    status        shows the currently used artifact id for <env>

arguments:
    <artifact>    the deployment artifact we are pushing (e.g. Docker image/AMI)
    <service>     the application we're targeting
    <env>         the environment we want to change

options:
    --no-push     make local changes without pushing to remote
    --latest      use the latest artifact when updating a service

    -h --help     shows this
    -v --version  shows version
```

## Development

Clone the project:

```
$ git clone git@github.com:ImageIntelligence/mimiron.git
```

Setup your virtualenv:

```
$ mkvirtualenv mimiron
```

Attach mim to your shell:

```
$ python setup.py develop
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
