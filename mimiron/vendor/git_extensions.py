# -*- coding: utf-8 -*-
from functools import wraps

import os

from git import Repo
from git.exc import GitCommandError

from ..domain.vendor import UnexpectedGitError
from ..domain.vendor import FetchRemoteUnknownNextStep
from ..domain.vendor import NoChangesEmptyCommit
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
def sync_updates(repo):
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
    if ahead:
        io.warn('ahead, pushing local changes to %s' % ref)
        repo.remotes.origin.push()

    # we're behind so let's pull changes down
    if behind:
        io.warn('behind, pulling changes from %s' % ref)
        repo.remotes.origin.pull()
    return True


@git_failure
def sync_submodule_updates(repo):
    for sm in repo.submodules:
        sm.update()


@git_failure
def update_submodule(repo, submodule_name, commit):
    io.info('updating submodule "%s:%s"' % (submodule_name, commit))
    target_sm = None
    for sm in repo.submodules:
        sm.update()
        sm_repo_name = os.path.splitext(os.path.split(sm.url)[-1])[0]
        if sm_repo_name == submodule_name:
            target_sm = sm
            break
    if target_sm is None:
        return io.err("couldn't find submodule to sync updates")

    current_commit = target_sm.branch.commit.name_rev
    current_commit = current_commit.split(' ')[0]

    # selected commit same as current, give up
    if current_commit == commit:
        io.info('"%s" is the same as HEAD')
        return False

    sm_abs_path = os.path.join(repo.working_dir, target_sm.path)
    sm_repo = Repo(sm_abs_path)
    sm_repo.git.checkout(commit)

    return True


@git_failure
def commit_changes(repo, commit_message):
    if not repo.is_dirty():
        return False

    repo.git.add(u=True)
    commit = repo.index.commit(commit_message)
    io.info('created commit with message: "%s"' % commit_message)
    io.info('commit id: %s' % commit.name_rev)
    return True


@git_failure
def push_commits(repo):
    io.info('pushing changes to %s' % repo.remotes.origin.refs[0].name)
    repo.remotes.origin.push()
    io.ok('successfully pushed changes to %s' % repo.remotes.origin.refs[0].name)


@git_failure
def commit_and_push(repo, commit_message):
    if not commit_changes(repo, commit_message):
        raise NoChangesEmptyCommit('"%s" has nothing to commit' % repo.working_dir)
    push_commits(repo)


@git_failure
def get_recent_commits(repo, limit=10):
    return list(repo.iter_commits(max_count=limit))
