"""user interface elements for verconchk"""

import itertools
import os
import sys

import verconchk.repository


def main():
    """find Bazaar-, Git-, Mercurial-, and Subversion-tracked files
    get some useful information about their current status
    """
    args = sys.argv[1:]

    if not args:
        args = ['.']

    finders = (verconchk.repository.finder(arg) for arg in args)
    repos = (repo for repo in itertools.chain.from_iterable(finders))

    for repo in repos:
        print os.path.relpath(repo.path)
        for command in repo.commands:
            for line in command():
                print "\t", line,
