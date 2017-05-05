# -*- coding: utf-8 -*-
from mimiron import __version__

import os
import shlex
from datetime import datetime

from git import Actor

from . import helpers
from .util import git_failure

from ...domain.vendor import FetchRemoteUnknownNextStep
from ...core import io
from ...core import constants as const


@git_failure
def sync_updates(repo, push=False):
    """Updates the local `repo` with origin, pulling and push when necessary.

    True is returned when any changes were made (aside fetch), otherwise False.

    Args:
        repo (git.objects.Repo): The git repository to sync updates on
        push (bool): True to push local changes, False to only pull

    Returns:
        bool: True if `repo` was sync'd, False otherwise

    """
    ref = repo.remotes.origin.refs[0].name
    repo_dir = repo.working_dir
    branch = repo.active_branch

    io.info('fetching remote for "%s"@:%s' % (os.path.split(repo_dir)[-1], branch))
    repo.remotes.origin.fetch()

    ahead, behind = helpers.get_ahead_behind_count(repo)
    is_dirty = repo.is_dirty()

    if not ahead and not behind and not is_dirty:
        return False

    io.info('(found) [ahead: %s, behind: %s] [dirty: %s]' % (ahead, behind, is_dirty))

    # possible merge conflicts
    if (ahead and behind) or (behind and is_dirty):
        raise FetchRemoteUnknownNextStep('possible merge conflict. please manually resolve')

    # we're ahead so let's push these changes up
    if ahead and push:
        io.warn('ahead, pushing local changes to %s' % ref)
        repo.remotes.origin.push()

    # we're behind so let's pull changes down
    if behind:
        io.warn('behind, pulling changes from %s' % ref)
        repo.remotes.origin.pull()
    return True


@git_failure
def generate_service_bump_commit_message(repo, service_name, env, tag, author=None):
    """Generates an appropriate service bump commit message.

    Args:
        repo (git.objects.Repo): The git repository to commit against
        service_name (str): The service/app you're bumping
        env (str): The infrastructure you're bumping against
        tag (str): The service/app artifact tag (e.g. Docker tag)
        author (Optional[git.objects.Actor]): Commit author, host user by default

    Returns:
        str: The formatted bump commit message

    """
    author = author if author else helpers.get_host_author(repo)
    return '\n'.join([
        'chore(tfvars): bump %s#%s "%s"' % (service_name, tag[:7], env),
        '\n'
        'committed-by: %s <%s>' % (author.name, author.email),
        'service-name: %s' % service_name,
        'service-tag: %s' % tag,
        'environment: %s' % env,
        '\n'
        'Committed via Mimiron v%s (https://github.com/ImageIntelligence/mimiron)' % __version__
    ])


@git_failure
def generate_commit_message(repo, env, author=None):
    """Generates a generic commit message.

    Args:
        repo (git.objects.Repo): The git repository to commit against
        env (str): The infrastructure you're bumping against
        author (Optional[git.objects.Actor]): Commit author, host user by default

    Returns:
        str: The generated generic commit message

    """
    author = author if author else helpers.get_host_author(repo)
    return '\n'.join([
        'chore(git): trigger deploy with empty commit',
        '\n'
        'committed-by: %s <%s>' % (author.name, author.email),
        'environment: %s' % env,
        '\n'
        'Committed via Mimiron v%s (https://github.com/ImageIntelligence/mimiron)' % __version__
    ])


def generate_deploy_commit_tag():
    """Generates the next deploy tag used to trigger a deploy."""
    return datetime.now().strftime('%s')


@git_failure
def commit_changes(repo, commit_message):
    """Commits all changes (staged and untracked) in a single commit.

    Args:
        repo (git.objects.Repo): The git repository to commit changes to
        commit_message (str): The commit message to use

    Returns:
        bool: True if a commit was made, False otherwise

    """
    if not repo.is_dirty():
        return False

    repo.git.add(u=True)
    actor = Actor(const.COMMIT_AUTHOR_NAME, email=const.COMMIT_AUTHOR_EMAIL)
    commit = repo.index.commit(commit_message, author=actor, committer=actor)

    io.info('commit message: "%s"' % commit_message.split('\n')[0])
    io.info('created commit: (id) %s' % commit.name_rev)
    return True


@git_failure
def commit_empty_changes(repo, commit_message):
    """Similar to `git_extensions.extensions.commit_changes` except --allow-empty.

    Args:
        repo (git.objects.Repo): The git repository to commit changes to
        commit_message (str): The commit message to use

    Returns:
        bool: True if a commit was made, False otherwise

    """
    if repo.is_dirty():
        return False

    repo.git.commit(
        *shlex.split('--allow-empty -m "%s" --author "%s"' % (commit_message, const.COMMIT_AUTHOR_NAME))
    )
    commit = repo.iter_commits().next()

    io.info('commit message: "%s"' % commit_message.split('\n')[0])
    io.info('created commit: (id) %s' % commit.name_rev)
    return True


@git_failure
def tag_commit(repo, tag_name, message, ref='HEAD'):
    """Creates a tag to the `ref` of the given git `repo`.

    Args:
        repo (git.objects.Repo): The git repository commit changes to
        tag_name (str): The name of the tag
        message (str): The tag message body
        ref (Optional[str, git.objects.Commit]): The commit to tag on

    Returns:
        bool: True if a tag was successfully created

    """
    repo.create_tag(tag_name, ref=ref, message=message)
    io.info('created tag: (name) %s' % tag_name)
    return True


@git_failure
def push_commits(repo):
    io.info('pushing changes to %s' % repo.remotes.origin.refs[0].name)
    repo.git.push('origin', 'master', tags=True)
    io.ok('successfully pushed changes to %s' % repo.remotes.origin.refs[0].name)
