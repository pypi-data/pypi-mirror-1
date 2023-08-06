"""hgpushsvn must be run in a repository created by hgimportsvn. It pushes
local Mercurial changesets one by one or optionally collapsed into a single
commit back to the SVN repository.

"""

import codecs
import os
import sys
import tempfile
from optparse import OptionParser

from hgsvn import ui
from hgsvn.common import run_hg, run_svn, hg_switch_branch
from hgsvn.run.common import run_parser, display_parser_error
from hgsvn.run.common import locked_main
from hgsvn.svnclient import get_svn_info, get_svn_status


def map_svn_rev_to_hg(svn_rev, hg_rev="tip", local=False):
    """
    Record the mapping from an SVN revision number and an hg revision (default "tip").
    """
    args = ["tag"]
    if local:
        args.append("-l")
    args.extend(["-r", strip_hg_rev(hg_rev), "svn.%d" % svn_rev])
    run_hg(args)

def strip_hg_rev(rev_string):
    """
    Given a string identifying an hg revision, return a string identifying the
    same hg revision and suitable for revrange syntax (r1:r2).
    """
    if ":" in rev_string:
        return rev_string.rsplit(":", 1)[1].strip()
    return rev_string.strip()

def get_hg_cset(rev_string):
    """
    Given a string identifying an hg revision, get the canonical changeset ID.
    """
    args = ["log", "-q", "-r", rev_string]
    return run_hg(args)

def get_hg_revs(first_rev, svn_branch, last_rev="tip"):
    """
    Get a chronological list of revisions (changeset IDs) between the two
    revisions (included).
    """
    args = ["log", "-q", "-b", svn_branch,
            "-r", "%s:%s" % (strip_hg_rev(first_rev),
                             strip_hg_rev(last_rev))]
    out = run_hg(args)
    return [strip_hg_rev(s) for s in out.splitlines()]

def get_pairs(l):
    """
    Given a list, return a list of consecutive pairs of values.
    """
    return [(l[i], l[i+1]) for i in xrange(len(l) - 1)]

def get_hg_changes(rev_string):
    """
    Get paths of changed files from a previous revision.
    Returns a tuple of (added files, removed files, modified files).
    """
    args = ["st", "-arm", "--rev", rev_string]
    out = run_hg(args)
    added = []
    removed = []
    modified = []
    for line in out.splitlines():
        st, path = line.split(None, 1)
        if st == 'A':
            added.append(path)
        elif st == 'R':
            removed.append(path)
        elif st == 'M':
            modified.append(path)
    #print "added:", added
    #print "removed:", removed
    #print "modified:", modified
    return added, removed, modified

def get_ordered_dirs(l):
    """
    Given a list of relative file paths, return an ordered list of dirs such that
    creating those dirs creates the directory structure necessary to hold those files.
    """
    dirs = set()
    for path in l:
        while True:
            path = os.path.dirname(path)
            if not path or path in dirs:
                break
            dirs.add(path)
    return list(sorted(dirs))

def get_hg_cset_details(rev_string):
    """
    Get details of a given changeset.
    Returns a dictionary created from the "hg log" information.
    """
    old_lc_all = os.environ.get('LC_ALL')
    os.environ['LC_ALL'] = 'C'
    args = ["log", "-v", "-r", rev_string]
    out = run_hg(args)
    if old_lc_all is None:
        del os.environ['LC_ALL']
    else:
        os.environ['LC_ALL'] = old_lc_all
    it = iter(out.splitlines())
    multiple_value_keys = set('tag')
    d = {}
    for line in it:
        key, value = line.split(":", 1)
        value = value.lstrip()
        if key == 'description':
            d[key] = "\n".join(it)
            break
        if key in multiple_value_keys:
            d.setdefault(key, []).append(value)
        else:
            d[key] = value
    return d

def get_svn_subdirs(top_dir):
    """
    Given the top directory of a working copy, get the list of subdirectories
    (relative to the top directory) tracked by SVN.
    """
    subdirs = []
    def _walk_subdir(d):
        svn_dir = os.path.join(top_dir, d, ".svn")
        if os.path.exists(svn_dir) and os.path.isdir(svn_dir):
            subdirs.append(d)
            for f in os.listdir(os.path.join(top_dir, d)):
                d2 = os.path.join(d, f)
                if f != ".svn" and os.path.isdir(os.path.join(top_dir, d2)):
                    _walk_subdir(d2)
    _walk_subdir(".")
    return subdirs

def hg_push_svn(start_rev, end_rev):
    """
    Commit the changes between two hg revisions into the SVN repository.
    Returns the SVN revision object, or None if nothing needed checking in.
    """
    run_hg(["up", "-C", end_rev])
    added, removed, modified = get_hg_changes(start_rev)
    # Add new files and dirs
    if added:
        bulk_args = get_ordered_dirs(added) + added
        run_svn(["add"], bulk_args)
    # Remove old files and empty dirs
    if removed:
        empty_dirs = [d for d in reversed(get_ordered_dirs(removed))
                      if not run_hg(["st", "-c", "%s" %d])]
        run_svn(["rm"], removed + empty_dirs)
    if added or removed or modified:
        details = get_hg_cset_details(end_rev)
        fp, fname = tempfile.mkstemp()
        f = codecs.open(fname, "wb", "utf-8")
        f.write(details["description"])
        f.close()
        try:
            out = run_svn(["commit", "-F", fname])
            last_line = out.splitlines()[-1]  # last line holds revision.
            svn_rev = int(''.join(x for x in last_line if x.isdigit()))
            return svn_rev
        finally:
            # Exceptions are handled by main().
            os.remove(fname)
    else:
        print "*", "svn: nothing to do"
        return None


def real_main(options, args):
    svn_info = get_svn_info(".")
    svn_current_rev = svn_info["last_changed_rev"]
    # e.g. u'svn://svn.twistedmatrix.com/svn/Twisted'
    repos_url = svn_info["repos_url"]
    # e.g. u'svn://svn.twistedmatrix.com/svn/Twisted/branches/xmpp-subprotocols-2178-2'
    wc_url = svn_info["url"]
    assert wc_url.startswith(repos_url)
    # e.g. u'/branches/xmpp-subprotocols-2178-2'
    wc_base = wc_url[len(repos_url):]

    svn_branch = wc_url.split("/")[-1]

    # Get remote SVN info
    svn_greatest_rev = get_svn_info(wc_url)['last_changed_rev']

    if svn_greatest_rev != svn_current_rev:
        # We can't go on if the pristine branch isn't up to date.
        # If the pristine branch lacks some revisions from SVN we are not
        # able to pull them afterwards.
        # For example, if the last SVN revision in out hgsvn repository is
        # r100 and the latest SVN revision is r101, hgpushsvn would create
        # a tag svn.102 on top of svn.100, but svn.101 isn't in hg history.
        print ("Branch '%s' out of date. Run 'hgpullsvn' first."
               % svn_branch)
        return 1

    # Switch branches if necessary.
    orig_branch = run_hg(["branch"]).strip()
    if orig_branch != svn_branch:
        if not hg_switch_branch(orig_branch, svn_branch):
            return 1

    hg_start_rev = "svn.%d" % svn_current_rev
    hg_revs = None
    try:
        hg_start_cset = get_hg_cset(hg_start_rev)
    except RuntimeError:
        if not options.force:
            raise
        hg_start_cset = get_hg_cset("0")
        print "Warning: revision '%s' not found, forcing to first rev '%s'" % (
            hg_start_rev, hg_start_cset)
    else:
        if not options.collapse:
            hg_revs = get_hg_revs(hg_start_cset, svn_branch)
    if hg_revs is None:
        hg_revs = [strip_hg_rev(hg_start_cset), strip_hg_rev(get_hg_cset("tip"))]

    pushed_svn_revs = []
    try:
        if options.dryrun:
            print "Outgoing revisions that would be pushed to SVN:"
        for prev_rev, next_rev in get_pairs(hg_revs):
            if not options.dryrun:
                svn_rev = hg_push_svn(prev_rev, next_rev)
                if svn_rev:
                    map_svn_rev_to_hg(svn_rev, next_rev, local=True)
                    pushed_svn_revs.append(svn_rev)
            else:
                print run_hg(["log", "-r", next_rev,
                              "--template", "{rev}:{node|short} {desc}"])
    except:
        # TODO: Add --no-backup to leave a "clean" repo behind if something
        #   fails?
        run_hg(["revert", "--all"])
        raise

    finally:
        work_branch = orig_branch or svn_branch
        if work_branch != svn_branch:
            run_hg(["up", "-C", work_branch])
            run_hg(["branch", work_branch])

    if pushed_svn_revs:
        if len(pushed_svn_revs) == 1:
            msg = "Pushed one revision to SVN: "
        else:
            msg = "Pushed %d revisions to SVN: " % len(pushed_svn_revs)
        run_svn(["up"])
        ui.status("%s %s", msg, ", ".join(str(x) for x in pushed_svn_revs))
        for line in run_hg(["st"]).splitlines():
            if line.startswith("M"):
                ui.status(("Mercurial repository has local changes after "
                           "SVN update."))
                ui.status(("This may happen with SVN keyword expansions."))
                break
    elif not options.dryrun:
        ui.status("Nothing to do.")

def main():
    # Defined as entry point. Must be callable without arguments.
    usage = "usage: %prog [-cf]"
    parser = OptionParser(usage)
    parser.add_option("-f", "--force", default=False, action="store_true",
                      dest="force",
                      help="push even if no hg tag found for current SVN rev.")
    parser.add_option("-c", "--collapse", default=False, action="store_true",
                      dest="collapse",
                      help="collapse all hg changesets in a single SVN commit")
    parser.add_option("-n", "--dry-run", default=False, action="store_true",
                      dest="dryrun",
                      help="show outgoing changes to SVN without pushing them")
    (options, args) = run_parser(parser, __doc__)
    if args:
        display_parser_error(parser, "incorrect number of arguments")
    return locked_main(real_main, options, args)

if __name__ == "__main__":
    sys.exit(main() or 0)

