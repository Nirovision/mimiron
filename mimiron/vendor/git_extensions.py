# -*- coding: utf-8 -*-
from functools import wraps

from git.exc import GitCommandError

from ..domain.vendor import UnexpectedGitError
from ..domain.vendor import FetchRemoteUnknownNextStep
from ..core.io import warn, info


def git_failure(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except GitCommandError as e:
            raise UnexpectedGitError(e)
    return wrapper


@git_failure
def get_ahead_behind(repo):
    branch = repo.active_branch

    commits_behind = repo.iter_commits('%s..origin/%s' % (branch, branch))
    commits_behind = sum(1 for _ in commits_behind)

    commits_ahead = repo.iter_commits('origin/%s..%s' % (branch, branch))
    commits_ahead = sum(1 for _ in commits_ahead)

    return commits_ahead, commits_behind


@git_failure
def sync_updates(repo):
    if repo.is_dirty():
        warn('"%s" is dirty' % repo.working_dir)

    info('fetching latest changes for "%s" @HEAD#%s' % (repo.working_dir, repo.active_branch))
    repo.remotes.origin.fetch()

    ahead, behind = get_ahead_behind(repo)
    if not ahead and not behind and not repo.is_dirty():
        info('no new changes found on local or remote')
        return False

    info('(found) [ahead: %s, behind: %s] [dirty: %s]' % (ahead, behind, repo.is_dirty()))

    # possible merge conflicts
    if ahead and behind:
        raise FetchRemoteUnknownNextStep('possible merge conflict. please manually resolve')
    if behind and repo.is_dirty():
        raise FetchRemoteUnknownNextStep('possible merge conflict. please manually resolve')

    # we're ahead so let's push these changes up
    if ahead:
        info('pushing local changes to %s#remote' % repo.working_dir)
        repo.remotes.origin.push()

    # we're behind so let's pull changes down
    if behind:
        info('pulling changes from %s#remote' % repo.working_dir)
        repo.remotes.origin.pull()
    return True


@git_failure
def commit_and_push(repo):
    if not repo.is_dirty():
        return info('nothing to commit or push. finished')

    repo.git.add(u=True)
    message = generate_commit_message(repo)
    repo.index.commit(message)
    info('created commit with message: "%s"' % message)

    info('pushing changes to remote %s#remote' % repo.working_dir)
    repo.remotes.origin.push()


def generate_commit_message(repo):
    return 'chore(variables): updated variables.tfvars file'
