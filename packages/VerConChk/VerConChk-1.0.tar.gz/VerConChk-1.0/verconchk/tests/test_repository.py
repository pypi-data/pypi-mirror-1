import os
import StringIO
import unittest

import nose.tools

import verconchk


def fake_run(repository, output):
    def run(cmd):
        return StringIO.StringIO(output)
    repository.run = run


class TestVersionControl(unittest.TestCase):
    def test_init_without_exec(self):
        assert verconchk.repository.VersionControl('/some/path')

    def test_init_with_exec(self):
        path = '/path/to/vcbin'
        repo = verconchk.repository.VersionControl('/some/path', path)
        assert repo
        assert repo.executable == path

    @nose.tools.raises(NotImplementedError)
    def test_status(self):
        verconchk.repository.VersionControl('/').status()

    def test_run(self):
        out = 'testable\noutput'
        repo = verconchk.repository.VersionControl('/', 'echo')
        assert repo.run(out).read().startswith(out)


class TestSubversion(unittest.TestCase):
    def test_init_without_exec(self):
        repo = verconchk.repository.Subversion('/')
        assert repo
        assert repo.executable == 'svn'

    def test_init_with_exec(self):
        path = 'path/to/svn'
        repo = verconchk.repository.Subversion('/', path)
        assert repo
        assert repo.executable == path

    def test_status(self):
        expected = [
            "A       path/to/file1\n",
            "!       path/to/file2.txt\n",
            "?       path/to/file3.py\n",
        ]
        svn = verconchk.repository.Subversion('/')
        fake_run(svn, ''.join(expected))

        assert svn.status().readlines() == expected


class TestGit(unittest.TestCase):
    def test_init_without_exec(self):
        repo = verconchk.repository.Git('/')
        assert repo
        assert repo.executable == 'git'

    def test_init_with_exec(self):
        path = '/path/to/git'
        repo = verconchk.repository.Git('/', path)
        assert repo
        assert repo.executable == path

    def test_status_drops_extra_stuff(self):
        fake_status = [
            "# On branch master\n",
            "# Changes to be committed:\n",
            '#   (use "git reset HEAD <file>..." to unstage)\n',
            "#\n",
            "#	new file:   something.txt\n",
            "#\n",
            "# Changed but not updated:\n",
            '#   (use "git add <file>..." to update what will be committed)\n',
            '#   (use "git checkout -- <file>..." to discard changes in \
working directory)\n',
            "#\n",
            "#	modified:   script.py\n",
            "#\n",
            "# Untracked files:\n",
            '#   (use "git add <file>..." to include in what will be \
committed)\n',
            "#\n",
            "#	fabfile.py\n",
        ]

        repo = verconchk.repository.Git('/')
        fake_run(repo, ''.join(fake_status))

        expected = [
            "On branch master\n",
            "Changes to be committed:\n",
            "\tnew file:   something.txt\n",
            "Changed but not updated:\n",
            "\tmodified:   script.py\n",
            "Untracked files:\n",
            "\tfabfile.py\n",
        ]

        assert repo.status() == expected


class TestMercurial(unittest.TestCase):
    def test_init_without_exec(self):
        assert verconchk.repository.Mercurial('/')
        assert verconchk.repository.Mercurial('/').executable == 'hg'

    def test_init_with_exec(self):
        path = '/path/to/hg'
        repo = verconchk.repository.Mercurial('/', path)
        assert repo
        assert repo.executable == path

    def test_status(self):
        repo = verconchk.repository.Mercurial('/')
        fake_status = ['M verconchk/repository.py\n',
                       'M verconchk/ui.py\n',
                       '? .coverage\n']
        fake_run(repo, ''.join(fake_status))

        assert repo.status().readlines() == fake_status

    def test_incoming(self):
        fake_changeset = ["changeset:   123:456abc\n",
                          "branch:      stable\n",
                          "tag:         tip\n",
                          "user:        Joe Guy <his@email_address.com>\n",
                          "date:        Sun Feb 1 5:01:03 2010 +0900\n",
                          "summary:     a short log message here\n"]

        repo = verconchk.repository.Mercurial('/')
        fake_run(repo, ''.join(fake_changeset))

        expected = ['incoming\n', '--------\n']
        expected.extend(fake_changeset)

        assert expected == repo.incoming()

    def test_outgoing(self):
        fake_changeset = ["changeset:   123:456abc\n",
                          "branch:      stable\n",
                          "tag:         tip\n",
                          "user:        Joe Guy <his@email_address.com>\n",
                          "date:        Sun Feb 1 5:01:03 2010 +0900\n",
                          "summary:     a short log message here\n"]

        repo = verconchk.repository.Mercurial('/')
        fake_run(repo, ''.join(fake_changeset))

        expected = ['outgoing\n', '--------\n']
        expected.extend(fake_changeset)

        assert expected == repo.outgoing()

    def test_outgoing_nochanges(self):
        repo = verconchk.repository.Mercurial('/')
        fake_run(repo, '')

        expected = []
        assert expected == repo.outgoing()

    def test_incoming_nochanges(self):
        repo = verconchk.repository.Mercurial('/')
        fake_run(repo, '')

        expected = []
        assert expected == repo.incoming()


class TestBazaar(unittest.TestCase):
    def test_init_without_exec(self):
        repo = verconchk.repository.Bazaar('/')
        assert repo
        assert repo.executable == 'bzr'

    def test_init_with_exec(self):
        path = '/path/to/bzr'
        repo = verconchk.repository.Bazaar('/', path)
        assert repo
        assert repo.executable == path

    def test_status(self):
        fake_status = [
            "added:\n",
            "  something-else.txt\n",
            "unknown:\n",
            "  something.txt\n",
        ]

        repo = verconchk.repository.Bazaar('/')
        fake_run(repo, ''.join(fake_status))

        assert repo.status().readlines() == fake_status


def fake_walker(subdir):
    def walk(path):
        return [
            (
                '/path/to/some/dir',
                ['subdir1', subdir, 'subdir3'],
                ['f1', 'f2', 'f3']),
        ]
    verconchk.ui.os.walk = walk


class TestFinder(unittest.TestCase):
    def test_no_repo_in_finder(self):
        fake_walker('subdir')
        fin = verconchk.repository.finder('')

        repos_found = []
        for x in fin:
            repos_found.append(x)

        assert repos_found == []

    def test_repos_in_finder(self):
        repo_types = [
            ('.bzr', verconchk.repository.Bazaar),
            ('.git', verconchk.repository.Git),
            ('.hg', verconchk.repository.Mercurial),
            ('.svn', verconchk.repository.Subversion),
        ]

        for dir_name, type in repo_types:
            fake_walker(dir_name)
            fin = verconchk.repository.finder('')

            repos_found = []
            for x in fin:
                assert isinstance(x, type)
