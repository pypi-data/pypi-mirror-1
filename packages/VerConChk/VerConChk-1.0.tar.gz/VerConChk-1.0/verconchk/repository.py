"""classes for accessing repositories and working copies"""

import os
from subprocess import Popen, STDOUT, PIPE


class VersionControl(object):
    """a version control checkout or repository

    * `path` is the path to the checkout or repository.
    * `executable` is the version control tool command (for example,
      :program:`hg` or :program:`svn`). If the tool is not in ``PATH``,
      provide the complete path to the executable.

    `path` and `executable` are both available as attributes of the
    `VersionControl` object. A list of methods on the object which
    provide version control activity, `commands`, is also available.
    """

    def __init__(self, path, executable=None):
        super(VersionControl, self).__init__()
        self.executable = executable
        self.path = os.path.abspath(os.path.expanduser(path))
        self.commands = [self.status]

    def run(self, cmd):
        """return the output from '<version control executable> <cmd>'
        as run from the repository's path
        """
        proc = Popen([self.executable, cmd],
                     stdout=PIPE,
                     stderr=STDOUT,
                     cwd=self.path)
        proc.wait()
        return proc.stdout

    def status(self):
        """return a status report

        Subclasses of VersionControl should always implement status,
        since it's the most common---and perhaps most primitive---version
        control command.
        """
        raise NotImplementedError


class Subversion(VersionControl):
    """a Subversion checkout"""

    def __init__(self, path, executable=None):
        super(Subversion, self).__init__(path, executable)
        if executable is None:
            self.executable = 'svn'

    def status(self):
        """return a status report on the Subversion checkout"""
        return self.run('status')


class Repository(VersionControl):
    """a distributed version control repository"""
    pass


class Bazaar(Repository):
    """a Bazaar repository"""
    def __init__(self, path, executable=None):
        super(Bazaar, self).__init__(path, executable)
        if self.executable is None:
            self.executable = 'bzr'

    def status(self):
        """return a status report on the Bazaar repository"""
        return self.run('status')


class Git(Repository):
    """a Git repository"""

    drop = ('#\n',
            '#   (use "git reset HEAD <file>..." to unstage',
            '#   (use "git add <file>..." to update what will be committed',
            '#   (use "git checkout -- <file>..."',
            '#   (use "git add <file>..." to include in what will be',
            'nothing added to commit but untracked files present',)

    def __init__(self, path, executable=None):
        super(Git, self).__init__(path, executable)
        if self.executable is None:
            self.executable = 'git'

    def status(self):
        """return a status report with extraneous characters and help
        text filtered out"""

        def clean(out):
            """strip leading hashes and spaces"""
            if out.startswith('# '):
                return out[2:]
            elif out.startswith('#\t'):
                return out[1:]
            else:
                return out

        result = [line for line in self.run('status')]

        if 'nothing to commit (working directory clean)\n' in result:
            return []

        return [clean(line) for line in self.run('status')
                if not line.startswith(Git.drop)]


class Mercurial(Repository):
    """a Mercurial repository"""

    drop = ('comparing with', 'searching for changes', 'no changes found')

    def __init__(self, path, executable=None):
        super(Mercurial, self).__init__(path, executable)
        self.commands += [self.incoming, self.outgoing]
        if executable is None:
            self.executable = 'hg'

    def status(self):
        """return a status report on the Mercurial repository"""
        return self.run('status')

    def _filter_ing(self, cmd):
        """filter the output from cmd, where cmd is either incoming
        or outgoing"""
        # the filtering on incoming and outgoing are the same
        header = ['%s\n' % cmd, '%s\n' % ('-' * len(cmd))]

        result = [line for line in self.run(cmd)
                  if not line.startswith(Mercurial.drop)]

        if result:
            header.extend(result)
            return header
        else:
            return []

    def incoming(self):
        """return incoming changesets report"""
        return self._filter_ing('incoming')

    def outgoing(self):
        """return outgoing changesets report"""
        return self._filter_ing('outgoing')

REPO_TYPES = {
    '.bzr': Bazaar,
    '.git': Git,
    '.hg': Mercurial,
    '.svn': Subversion,
}


def finder(path):
    """yields the next version controlled directory in path recursively"""
    for dirpath, dirnames, filenames in os.walk(path):
        for repo_type in REPO_TYPES.keys():
            if repo_type in dirnames:
                yield REPO_TYPES[repo_type](dirpath)
                dirnames = []
