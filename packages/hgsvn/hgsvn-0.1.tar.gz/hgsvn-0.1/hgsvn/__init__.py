"""
-------
Summary
-------

This set of scripts allows to work locally on Subversion-managed projects
using the Mercurial distributed version control system.

Currenly two scripts are provided:
 * ``hgimportsvn`` initializes an SVN checkout which is also a Mercurial
   repository.
 * ``hgpullsvn`` pulls the latest changes from the SVN repository, and updates
   the Mercurial repository accordingly.

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

------------
Requirements
------------

You first need to install the "pysvn" library (http://pysvn.tigris.org/).
Unfortunately it is not available as an easy_install package, so it can't
be automated in the setup script.
In Debian and Ubuntu this package is named "python-svn" (not "python-subversion"
which is a different package).
In Mandriva it is named "python-pysvn" (not "python-svn" which is a different
package).

--------
Features
--------

Named branches
--------------

These scripts encourage the use of named branches. All updates using
``hgpullsvn`` are made in the branch named from the last component of the
SVN URL (e.g., if the SVN URL is http://svn.myproj/branches/feature-ZZZ/,
``hgpullsvn`` will create and use the named branch 'feature-ZZZ').

You can thus do local development using one or several named branches,
and ``hgpullsvn`` will update to the original (pristine) branch, leaving your
local work intact (you can then merge by yourself if your want).
This means that ``hg di -r name-of-pristine-branch`` will immediately
give you a patch against the pristine branch, which you can submit to the
project maintainers.

(Note: in a non-trivial setup where you work on several features or bugfixes,
you will clone the pristine repository for each separate piece of work,
which will still give you the benefit of named branches for quickly extracting
diffs between branches).

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
at rev. 1138. It will thus created the 'new-feature' hg repository by cloning
from the 'trunk' repository at the revision immediately preceding rev. 1138:
for example rev. 1135, identified by the local tag 'svn.1135'.

This means you will have an hgsvn repository containing two named branches:
'trunk' for all the changesets in the trunk before rev. 1138, and 'new-feature'
for all the changesets in the SVN branch (therefore, after rev. 1138).
This way, you can easily track how the branch diverges from the trunk, but also
do merges, etc.

Tags
----

``hgpullsvn`` tags each new Mercurial changeset with a local tag named 'svn.123'
where 123 is the number of the corresponding SVN revision.
Local tags were chosen because they don't pollute the hg log with superfluous
entries, and also because SVN revision numbers are only meaningful for a
specific branch: there is no use propagating them (IMHO).


"""

__all__ = []

__author__ = 'Antoine Pitrou'
__license__ = 'GNU General Public License (version 2 or later)'
__versioninfo__ = (0, 1)

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
