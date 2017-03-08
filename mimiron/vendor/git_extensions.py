# -*- coding: utf-8 -*-
from mimiron import __version__

from functools import wraps

import os

from git import Actor
from git.exc import GitCommandError

from ..domain.vendor import UnexpectedGitError
from ..domain.vendor import FetchRemoteUnknownNextStep
from ..core import io


def git_failure(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except GitCommandError as e:
            raise UnexpectedGitError(e)
    return wrapper


@git_failure
def get_ahead_behind_count(repo):
    branch = repo.active_branch

    commits_behind = repo.iter_commits('%s..origin/%s' % (branch, branch))
    commits_behind = sum(1 for _ in commits_behind)

    commits_ahead = repo.iter_commits('origin/%s..%s' % (branch, branch))
    commits_ahead = sum(1 for _ in commits_ahead)

    return commits_ahead, commits_behind


@git_failure
def sync_updates(repo, push=False):
    """Updates the local `repo` with origin, pulling and push when necessary.

    True is returned when any changes were made (aside fetch), otherwise False.
    """
    ref = repo.remotes.origin.refs[0].name
    repo_dir = repo.working_dir
    branch = repo.active_branch

    io.info('fetching remote for "%s"@:%s' % (os.path.split(repo_dir)[-1], branch))
    repo.remotes.origin.fetch()

    ahead, behind = get_ahead_behind_count(repo)
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
def generate_service_bump_commit_message(repo, service_name, env, tag):
    author = Actor.author(repo.config_reader())
    return '\n'.join([
        'chore(tfvars): bump %s#%s "%s"' % (service_name, tag[:7], env),
        '\n'
        'committed-by: %s <%s>' % (author.name, author.email),
        'service-tag: %s' % tag,
        'environment: %s' % env,
        '\n'
        'Committed via Mimiron v%s (https://github.com/ImageIntelligence/mimiron)' % __version__
    ])


@git_failure
def get_recent_commits(repo, limit=10):
    return list(repo.iter_commits(max_count=limit))


@git_failure
def commit_changes(repo, commit_message):
    if not repo.is_dirty():
        return False

    repo.git.add(u=True)

    actor = Actor('Mimiron', email='')
    commit = repo.index.commit(commit_message, author=actor, committer=actor)
    io.info('commit message: "%s"' % commit_message.split('\n')[0])
    io.info('created commit: (id) %s' % commit.name_rev)
    return True


@git_failure
def push_commits(repo):
    io.info('pushing changes to %s' % repo.remotes.origin.refs[0].name)
    repo.remotes.origin.push()
    io.ok('successfully pushed changes to %s' % repo.remotes.origin.refs[0].name)
