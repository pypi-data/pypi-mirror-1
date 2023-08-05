"""
-------
Summary
-------

This set of scripts allows to work locally on Subversion-managed projects
using the Mercurial distributed version control system.

Why use Mercurial ? You can do local (disconnected) work, pull the latest
changes from the SVN server, manage private branches, submit patches to project
maintainers, etc. And of course you have fast local operations like "hg log",
"hg annotate"...

Currenly two scripts are provided:

* ``hgimportsvn`` initializes an SVN checkout which is also a Mercurial
  repository.
* ``hgpullsvn`` pulls the latest changes from the SVN repository, and updates
  the Mercurial repository accordingly. It can be run multiple times.

-------
Example
-------

Making a checkout of the Nose_ trunk::

    $ mkdir nose && cd nose
      # Make SVN checkout, initialize hg repository with first SVN revision
    $ hgimportsvn http://python-nose.googlecode.com/svn/trunk
    $ cd trunk
      # Pull all history from SVN, creating a new hg changeset for each SVN rev
    $ hgpullsvn

.. _Nose: http://somethingaboutorange.com/mrl/projects/nose/

-------
Install
-------

Just type ``easy_install hgsvn``. If easy_install is not available on your
computer, download and uncompress the source tarball, then type ``python
setup.py install``.

*Note:* hgsvn makes use of the ElementTree library. It is bundled by default
with Python 2.5, and the setup script should install it automatically for you
if you are using Python 2.4. However, if you get some error messages, you might
have to install it manually (at least one user reported he had to).

--------
Features
--------

Graceful operation
------------------

``hgpullsvn`` asks for SVN log entries in chunks, so that pulling history does
not put the remote server on its knees.

``hgpullsvn`` can be interrupted at any time, and run again later: you can pull
history incrementally.

Metadata
--------

hgsvn reflects commit times (using the local timezone) and commit author names.
Commit messages can contain Unicode characters. File copies and renames as
reflected as well, provided they occur inside the branch.

Tags
----

``hgpullsvn`` tags each new Mercurial changeset with a local tag named 'svn.123'
where 123 is the number of the corresponding SVN revision.
Local tags were chosen because they don't pollute the hg log with superfluous
entries, and also because SVN revision numbers are only meaningful for a
specific branch: there is no use propagating them (IMHO).

Named branches
--------------

These scripts encourage the use of named branches. All updates using
``hgpullsvn`` are made in the branch named from the last component of the
SVN URL (e.g., if the SVN URL is svn://server/myproj/branches/feature-ZZZ,
``hgpullsvn`` will create and use the named branch 'feature-ZZZ').

You can thus do local development using your own named branches. When you
want to fetch latest history from the SVN repository, simply use ``hgpullsvn``
which will update to the original (pristine) branch, leaving your local work
intact (you can then merge by yourself if your want).

This also means that ``hg di -r name-of-pristine-branch`` will immediately
give you a patch against the pristine branch, which you can submit to the
project maintainers.

(Note: in a non-trivial setup where you work on several features or bugfixes,
you will clone the pristine repository for each separate piece of work,
which will still give you the benefit of named branches for quickly generating
patches).

Detecting parent repository
---------------------------

If the SVN URL has been created by copying from another SVN URL (this is the
standard method for branch creation), ``hgimportsvn`` tries to find an hgsvn
repository corresponding to the parent SVN URL.
It then creates the new repository by cloning this repository at the revision
immediately before the creation of the SVN branch.

In other words, let's say you are operating from myworkdir/. In myworkdir/trunk,
you already have an hgsvn repository synced from svn://server/myproj/trunk.
You then ``hgimport svn://server/myproj/branches/new-feature``. It will find
that the 'new-feature' branch has been created by copying from 'trunk'
at rev. 1138. It will thus create the 'new-feature' hg repository by cloning
from the 'trunk' repository at the revision immediately preceding rev. 1138:
for example rev. 1135, identified by the local tag 'svn.1135'.

This means you will have an hgsvn repository containing two named branches:
'trunk' for all the changesets in the trunk before rev. 1138, and 'new-feature'
for all the changesets in the SVN branch (therefore, after rev. 1138).
This way, you can easily track how the branch diverges from the trunk, but also
do merges, etc.

-----------
Limitations
-----------

SVN externals are purposefully ignored and won't be added to your Mercurial
repository.

There is no straightforward way to push back changes to the SVN repository.
For now hgsvn is primarily intended at doing local mirrors, private branches,
or patch-driven development (by submitting patches to project maintainers,
which is necessary if you don't have SVN commit access anyway). However, an
``hgpushsvn`` command is in the plans that will allow one day to push all
changes to SVN automatically.

-------
History
-------

hgsvn 0.1.3
-----------

Improvements:

* Performance improvement with ``svn log`` command in ``hgpullsvn`` (suggested
  by Mads Kiilerich and Daniel Berlin).
* Less obscure error message when ``svn info`` fails while returning a
  successful return code.
* Two simplistic man pages added.

Bug fixes:

* Windows compatibility fix by Bill Baxter.
* ``hgimportsvn`` failed when used on a whole repository.
* Fix crash on empty commit message (also reported by Neil Martinsen-Burrell
  and Walter Landry).
* Handle file and directory renames properly (reported by Bill Baxter).
* SVN allows copying from a deleted file by having mixed revisions inside the
  working copy at commit time, but Mercurial doesn't accept it (reported by
  Neil Martinsen-Burrell).

hgsvn 0.1.2
-----------

Improvements:

* Automatically generate ``.hgignore`` file. Not only does it produce cleaner
  output for commands like ``hg status``, but it speeds things up as well.
* ``hgpullsvn`` is more robust in the face of errors and user interruptions.
* Try to be Windows-compatible by not using the commands module.
* Remove dependency on the pysvn library; we use the XML output option of SVN
  commands instead.

Bug fixes:

* Fix a bug in parent repository detection.
* Detect the wicked case where the SVN branch has been overwritten with
  contents of another branch (witnessed with Nose trunk and 0.10-dev branch).
  We can't properly handle this situation, so fail with an explicit message.
* ``svn info`` on base repository URL does not always succeed, use the specific
  project URL instead (reported by Larry Hastings).

hgsvn 0.1.1
-----------

Bug fixes:

* pysvn doesn't really ignore externals, so use the command line for
  ``svn update`` instead (otherwise we get failures for obsolete URLs)
* ``.svn`` directories were not always ignored.
* On large repositories, adding more than 32765 files at once failed because
  of too many arguments on the command line.
* On slow SVN servers, the chunked log fetching algorithm ended up asking for
  0 log entries.

hgsvn 0.1
---------

Initial release.


"""

__all__ = []

__author__ = 'Antoine Pitrou'
__license__ = 'GNU General Public License (version 2 or later)'
__versioninfo__ = (0, 1, 3)

base_version = '.'.join(map(str, __versioninfo__))
full_version = base_version
try:
    import pkg_resources
except ImportError:
    pass
else:
    try:
        full_version = pkg_resources.get_distribution("hgsvn").version
    except pkg_resources.DistributionNotFound:
        pass

__version__ = full_version
