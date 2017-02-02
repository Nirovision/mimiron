# Mimiron

**Welcome to mimiron!**

> [Mimiron](http://www.wowhead.com/npc=33350/mimiron) is one of the Titanic Watchers. He once resided at the Temple of Invention, but is absent during the time of Loken's rebellion.

Mimiron a CLI tool whose purpose is to be the glue between your tfvars and Terraform config.

When all of your Terraform config is completely modular, the only sane way to manage variables is to store them inside a `variables.tfvars` file and pass that along when you run `terraform apply -var-file=variables.tf`... but where do you store `variables.tfvars`?

Our MVP approach is to store variables inside a separate git repository. Then, inside the Terraform deployments repo, create a link between the two via `git submodules`, making sure specifying the commit SHA.

This approach is super simple and works but it can be quite cumbersome to when you want to make updates. Mimiron provides a few commands to help automate the cumbersome tasks away.

## Installation

```
$ pip install mimiron
```

You also need to specify a few environment variables to let Mimiron know where your terraform and tfvar repos are located:

```bash
export TF_REPO_PATH=~/worksapce/terraform-deployments/
export TF_VAR_REPO_PATH=~/workspace/tfvars/
```

## Usage

```
>>> mim --help
mimiron.py

usage:
  mim commit [--no-push]
  mim up sha [<sha>] [--no-push]
  mim up app <namespace> <environment [--no-push]

commands:
  commit        looks for all changes made, creates a commit and pushes to remote
  up            updates a service/app or git submodule sha

arguments:
  sha           git commit sha
  namespace     namespace name you want to update
  environment   environment make changes against

options:
  --no-push     avoids pushing changes to remote

  -h --help     shows this
  -v --version  shows version
```

Example workflow:

```
$ mim update service website staging
$ mim update sha
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
