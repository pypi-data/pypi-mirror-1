Internals
=========

VerConChk uses a hierarchy of classes to provide version control activity.
All version control objects are derived from the `VersionControl` class.

.. autoclass:: verconchk.repository.VersionControl
    :members: run

Individual repositories and working copies are then found with `finder`
generator:

.. autofunction:: verconchk.repository.finder

Version Control Objects
-----------------------

Subsequently, the various individual version control tools are implemented
in their own classes:

.. autoclass:: verconchk.repository.Bazaar
    :members: status

.. autoclass:: verconchk.repository.Git
    :members: status

.. autoclass:: verconchk.repository.Mercurial
    :members: status, incoming, outgoing

.. autoclass:: verconchk.repository.Subversion
    :members: status