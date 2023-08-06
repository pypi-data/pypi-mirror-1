"""
Display git repository information in a command prompt.

The ``Git`` class provides a very simple programmatic interface to a
non-bare ``git`` repository. It scans the file system and does not run
any ``git`` commands, since that can sometimes take a perceptible amount
of time.

"""

from __future__ import print_function
import os
import os.path as Path
import re
import sys

__all__ = 'Git GitRepositoryNotFound'.split()

def main():
    """
    Display the current ``git`` branch.

    If changes are stashed or a rebase is in progress, this will be
    indicated.

    If a non-zero exit code is passed as ``sys.argv[1]``, it will be
    displayed.

    """
    result = ''
    try:
        git = Git()
        result += ' ' + git.head
        if git.stash_count > 1:
            result += ' stashes!'
        elif git.stash_count > 0:
            result += ' stash'
        if git.rebasing:
            result += ' rebase!'
    except GitRepositoryNotFound:
        pass
    print(result)
    status = sys.argv[1] if len(sys.argv) > 1 else '0'
    if status != '0':
        print('=> {0}'.format(status), file=sys.stderr)


class Git(object):

    """Provides an interface to a non-bare ``git`` repository."""

    def __init__(self, working_dir=None):
        """
        Construct an interface to a repository.

        If ``working_dir`` is provided, it and its ancestors are scanned
        for a ``.git`` directory.

        Otherwise, if ``GIT_DIR`` is provided, it is used, and if not,
        the current working directory and its ancestors are scanned for
        a ``.git`` directory.

        Raises ``GitRepositoryNotFound`` if no ``.git`` directory is
        found.

        """
        if not working_dir:
            GIT_DIR = os.environ.get('GIT_DIR')
            if GIT_DIR:
                self.dir = GIT_DIR
                return
            working_dir = os.getcwd()
        working_dir = Path.abspath(working_dir)
        while True:
            self.dir = Path.join(working_dir, '.git')
            if Path.isdir(self.dir):
                break
            parent = Path.dirname(working_dir)
            if working_dir == parent:
                raise GitRepositoryNotFound
            working_dir = parent

    @property
    def head(self):
        """Return the name or commit hash of HEAD."""
        with open(Path.join(self.dir, 'HEAD')) as f:
            head = f.read()
        m = re.match(r'ref: refs/heads/(.*)', head)
        if m:
            return m.group(1)
        else:
            return head[:7]

    @property
    def rebasing(self):
        """Return whether a rebase is in progress."""
        return any(Path.exists(Path.join(self.dir, rebase_dir))
            for rebase_dir in 'rebase-apply rebase-merge'.split())

    @property
    def stash_count(self):
        """Return the number of commits in the stash."""
        stash_path = Path.join(self.dir, 'logs', 'refs', 'stash')
        if not Path.isfile(stash_path):
            return 0
        with open(stash_path) as f:
            stash = f.read()
        return len(stash.splitlines())


class GitRepositoryNotFound(Exception):

    """No git repository was found."""
