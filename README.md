# Mimiron

[![Build Status](https://travis-ci.org/ImageIntelligence/mimiron.svg?branch=master)](https://travis-ci.org/ImageIntelligence/mimiron)
[![PyPI version](https://badge.fury.io/py/mimiron.svg)](https://badge.fury.io/py/mimiron)

**Welcome to mimiron!**

> [Mimiron](http://www.wowhead.com/npc=33350/mimiron) is one of the Titanic Watchers. He once resided at the Temple of Invention, but is absent during the time of Loken's rebellion.

Mimiron is a CLI tool that aims provide a better workflow when manging Terraform variables.

When all of your Terraform config is completely modular, the only sane way to manage variables is to store them inside a `variables.json` file and pass that along when you run `terraform apply -var-file=variables.json`... but where do you store `variables.json` and how can you easily make changes?

Our approach is to store non-sensitive variables inside the same repository as our Terraform config. Sensitive variables like your AWS secret and master db password are stored elsewhere then accessed later whether it be via AWS KMS or Hashicorp Vault. The purpose of this project is to manage non-sensitive variables.

We want to make simple tasks such as bumping an image version simple and Mimiron is a small CLI tool that does that. Mimiron provides a few commands to help automate the cumbersome tasks away.

## Installation

```bash
pip install mimiron --upgrade
```

... or if you're using a Mac (see [here](https://github.com/pypa/pip/issues/3165) why):

```bash
sudo pip install mimiron --ignore-installed six
```

`mim` requires a configuration file at `~/.mimiron.json` before it can work. Take a look at [./data/example_config.json](./data/example_config.json) for an example.

| Root Key | Sub Key | Description
|-|-|-|
| terraformRepositories(array<object>) | | |
| | path(string) | The path to a Terraform repository (cannot be relative but may contain ~). |
| | defaultEnvironment(string) | Projects representing multiple environments have a default (e.g. staging, production). |
| | tagEnvironment(string) | Usually the production environment (tags can trigger production `terraform apply`). |
| | defaultGitBranch(string) | Some `mim` commands will check if the current branch is this before running. |
| dockerhub(object) | | |
| | username(string) | The username to your DockerHub account. |
| | password(string) | The password to your DockerHub account. |
| | organization(string) | The organization your DockerHub belongs to (username if none). |

## Assumptions

* `mim` requires that you store your Docker image aritfacts on DockerHub. No support for other registries exist at this time.
* Terraform configuration is expected to exist at `/project/terraform/`.
* Terraform variables (tfvars) are stored in JSON files inside a directory named `/project/terraform/tfvars/`.
* Docker image artifacts are named `service_name_image` e.g. `web_marketing_image`.

## Usage

```
>>> mim --help
mimiron.py

usage:
    mim (bump|b) <service> [--env=<env>] [-t] [--no-push] [--show-all]
    mim (status|st) [--env=<env>]
    mim (deploy|d) [--show-last=<n>] [--no-push] [-t] [--empty-commit]

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
    -t --tag         creates a git tag (git tag -a) on a chosen commit or [--empty-commit]

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
repository:https://upload.pypi.org/legacy/
username:xxx
password:yyy
```

Register this package to the Cheeseshop:

```
$ python setup.py register -r mimiron
```

Build a distributable and upload:

```
$ python setup.py sdist upload -r mimiron
```
