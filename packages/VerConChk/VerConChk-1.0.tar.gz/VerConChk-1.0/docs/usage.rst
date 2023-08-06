Usage
=====

VerConChk is easy to use. In it's simplest form, simply run the
:program:`vcc` command-line program without any arguments::

    $ vcc
    ./path/to/repository
        M file.py
        D old_file.py
    ./path/to/second_repository
    ./path/to/another

Alternatively, you may specify the directory or directories where
:program:`vcc` ought to look for version controlled files::

    $ vcc ~/src /home/user2/repositories
    ./src/repo1
        M file.py
    ../user2/repositories/repo2
