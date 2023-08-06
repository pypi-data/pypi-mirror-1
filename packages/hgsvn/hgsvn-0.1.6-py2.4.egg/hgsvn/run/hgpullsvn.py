"""hgpullsvn must be run in a repository created by hgimportsvn. It pulls
new revisions one by one from the SVN repository and converts them into local
Mercurial changesets.

"""

from hgsvn.common import (
    run_command, run_hg, run_svn, skip_dirs,
    hg_commit_from_svn_log_entry, hg_tag_svn_rev, hg_exclude_options,
    hg_commit_prefix, get_svn_rev_from_hg, get_hgsvn_lock, LockHeld,
    fixup_hgsvn_dir,
)
from hgsvn.svnclient import (
    get_svn_info, get_svn_versioned_files,
    iter_svn_log_entries,
)
from hgsvn.errors import (
    HgSVNError, ExternalCommandFailed, OverwrittenSVNBranch, UnsupportedSVNAction,
)
from hgsvn.run.common import run_parser, display_parser_error

import sys
import os
import shutil
import tempfile
import time
import traceback
from optparse import OptionParser

"""
NOTE: interesting tests:
    * http://svn.python.org/projects/python/trunk/Mac :
        - files with space characters in them just before 45000
        - file and dir renames/removes between 46701 and 46723
"""


# TODO: an option to enable/disable svn:externals (disabled by default?)


def detect_overwritten_svn_branch(wc_url, svn_rev):
    """
    Detect whether the current SVN branch was in a different location at
    the given revision. This means the current branch was later overwritten
    by another one.
    """
    remote_url = get_svn_info(wc_url, svn_rev)['url']
    if remote_url != wc_url:
        msg = ("The current branch (%s) has been\noverwritten with contents from %s.\n"
            + "hgsvn is unable to fetch history of the original branch.\n"
            + "Also, you will have to do a separate 'hgsvnimport' to pull recent history.\n"
            ) % (wc_url, remote_url)
        raise OverwrittenSVNBranch(msg)


def pull_svn_rev(log_entry, current_rev, svn_wc, wc_url, wc_base):
    """
    Pull SVN changes from the given log entry.
    Returns the new SVN revision. If an exception occurs, it will rollback
    to revision 'current_rev'.
    """
    svn_rev = log_entry['revision']

    added_paths = []
    copied_paths = []
    removed_paths = []
    changed_paths = []
    unrelated_paths = []
    replaced_paths = {}
    for d in log_entry['changed_paths']:
        # e.g. u'/branches/xmpp-subprotocols-2178-2/twisted/words/test/test_jabberxmlstream.py'
        p = d['path']
        if not p.startswith(wc_base + "/"):
            # Ignore changed files that are not part of this subdir
            if p != wc_base:
                unrelated_paths.append(p)
            continue
        action = d['action']
        if action not in 'MARD':
            raise UnsupportedSVNAction("In SVN rev. %d: action '%s' not supported. Please report a bug!"
                % (svn_rev, action))
        # e.g. u'twisted/words/test/test_jabberxmlstream.py'
        p = p[len(wc_base):].strip("/")
        # Record for commit
        changed_paths.append(p)
        # Detect special cases
        old_p = d['copyfrom_path']
        if old_p and old_p.startswith(wc_base + "/"):
            old_p = old_p[len(wc_base):].strip("/")
            # Both paths can be identical if copied from an old rev.
            # We treat like it a normal change.
            if old_p != p:
                # Try to hint hg about file and dir copies
                if not os.path.isdir(old_p):
                    copied_paths.append((old_p, p))
                    if action == 'R':
                        removed_paths.append(old_p)
                else:
                    # Extract actual copied files (hg doesn't track dirs
                    # and will refuse "hg copy -A" with dirs)
                    r = run_hg(["st", "-nc"], [old_p])
                    for old_f in r.splitlines():
                        f = p + old_f[len(old_p):]
                        copied_paths.append((old_f, f))
                        if action == 'R':
                            removed_paths.append(old_f)
                continue
        if d['action'] == 'A':
            added_paths.append(p)
        elif d['action'] == 'D':
            removed_paths.append(p)
        elif d['action'] == 'R':
            # (R)eplaced directories can have added and removed files without
            # them being mentioned in the SVN log => we must detect those files
            # ourselves.
            # (http://svn.python.org/projects/python/branches/py3k, rev 59625)
            if os.path.isdir(p):
                replaced_paths[p] = get_svn_versioned_files(
                    os.path.join(svn_wc, p))
            else:
                # We never know what twisty semantics (R) can have. addremove
                # is safest.
                added_paths.append(p)

    # Update SVN + add/remove/commit hg
    try:
        if changed_paths:
            run_svn(["up", "--ignore-externals", "-r", svn_rev, svn_wc])
            for p, old_contents in replaced_paths.items():
                old_contents = set(old_contents)
                new_contents = set(get_svn_versioned_files(
                    os.path.join(svn_wc, p)))
                added_paths.extend(p + '/' + f for f in new_contents - old_contents)
                removed_paths.extend(p + '/' + f for f in old_contents - new_contents)
            if added_paths:
                # Use 'addremove' because an added SVN directory may
                # overwrite a previous directory with the same name.
                # XXX what about untracked files in those directories?
                run_hg(["addremove"] + hg_exclude_options, added_paths)
            for old, new in copied_paths:
                try:
                    run_hg(["copy", "-A"], [old, new])
                except ExternalCommandFailed:
                    # Maybe the "old" path is obsolete, i.e. it comes from an
                    # old SVN revision and was later removed.
                    s = run_hg(['st', '-nd'], [old])
                    if s.strip():
                        # The old path is known by hg, something else happened.
                        raise
                    run_hg(["add"], [new])
            if removed_paths:
                run_hg(["remove", "-A"], removed_paths)
            hg_commit_from_svn_log_entry(log_entry)
        elif unrelated_paths:
            detect_overwritten_svn_branch(wc_url, svn_rev)
    # NOTE: in Python 2.5, KeyboardInterrupt isn't a subclass of Exception anymore
    except (Exception, KeyboardInterrupt), e:
        print "\nInterrupted, please wait for cleanup!\n"
        # NOTE: at this point, running SVN sometimes gives "write lock failures"
        # which leave the WC in a weird state.
        time.sleep(0.3)
        run_svn(["cleanup"])
        hgsvn_rev = get_svn_rev_from_hg()
        if hgsvn_rev != svn_rev:
            # Unless the tag is there, revert to the last stable state
            run_svn(["up", "--ignore-externals", "-r", current_rev, svn_wc])
            run_hg(["revert", "--all"])
        raise

    return svn_rev


def locked_main():
    usage = "usage: %prog [-p SVN peg rev] [--help]"
    parser = OptionParser(usage)
    parser.add_option("-p", "--svn-peg", type="int", dest="svn_peg",
       help="SVN peg revision to locate checkout URL")
    (options, args) = run_parser(parser, __doc__)
    if args:
        display_parser_error(parser, "incorrect number of arguments")

    svn_wc = "."
    svn_peg_wc = svn_wc
    if options.svn_peg:
       svn_peg_wc += "@" + str(options.svn_peg)

    # Get SVN info
    svn_info = get_svn_info('.')
    current_rev = svn_info['revision']
    next_rev = current_rev + 1
    # e.g. u'svn://svn.twistedmatrix.com/svn/Twisted'
    repos_url = svn_info['repos_url']
    # e.g. u'svn://svn.twistedmatrix.com/svn/Twisted/branches/xmpp-subprotocols-2178-2'
    wc_url = svn_info['url']
    assert wc_url.startswith(repos_url)
    # e.g. u'/branches/xmpp-subprotocols-2178-2'
    wc_base = wc_url[len(repos_url):]
    # e.g. 'xmpp-subprotocols-2178-2'
    svn_branch = wc_url.split("/")[-1]
    if options.svn_peg:
       wc_url += "@" + str(options.svn_peg)

    # Get remove SVN info
    svn_greatest_rev = get_svn_info(wc_url)['last_changed_rev']
    if svn_greatest_rev < next_rev:
        print "No revisions after %s in SVN repo, nothing to do" % svn_greatest_rev
        return

    # Prepare and/or switch named branches
    orig_branch = run_hg(["branch"]).strip()
    if orig_branch != svn_branch:
        # Update to or create the "pristine" branch
        hg_branches = [l.split()[0] for l in run_hg(["branches"]).splitlines()]
        if svn_branch in hg_branches:
            # We want to run "hg up -C" (to force changing branches) but we
            # don't want to erase uncommitted changes.
            if run_hg(['st', '-mard']).strip():
                print ("\nThe Mercurial working copy contains pending changes in branch '%s'!\n"
                    + "Please either commit or discard them before running 'hgpullsvn' again."
                    ) % orig_branch
                return 1
            run_hg(['up', '-C', svn_branch])
        run_hg(["branch", svn_branch])

    # Detect that a previously aborted hgpullsvn retrieved an SVN revision
    # without committing it to hg.
    # If there is no SVN tag in current head, we may have been interrupted
    # during the previous "hg tag".
    hgsvn_rev = get_svn_rev_from_hg()
    if hgsvn_rev is not None and hgsvn_rev != current_rev:
        print ("\nNote: hgsvn repository is in an unclean state "
            + "(probably because of an aborted hgpullsvn). \n"
            + "Let's first update to the last good SVN rev.")
        run_svn(["revert", "-R", "."])
        run_svn(["up", "--ignore-externals", "-r", hgsvn_rev, svn_wc])
        next_rev = hgsvn_rev + 1

    # Load SVN log starting from current rev
    it_log_entries = iter_svn_log_entries(svn_peg_wc, next_rev, svn_greatest_rev)

    try:
        try:
            for log_entry in it_log_entries:
                current_rev = pull_svn_rev(log_entry, current_rev, svn_wc, wc_url, wc_base)
        # TODO: detect externals with "svn status" and update them as well

        finally:
            work_branch = orig_branch or svn_branch
            if work_branch != svn_branch:
                run_hg(["up", '-C', work_branch])
                run_hg(["branch", work_branch])

    except KeyboardInterrupt:
        print "\nStopped by user."
    except ExternalCommandFailed, e:
        print str(e)
    except:
        print "\nCommand failed with following error:\n"
        traceback.print_exc()


def main():
    # We must do this before trying to take the lock file
    fixup_hgsvn_dir('.')
    try:
        l = get_hgsvn_lock()
    except LockHeld, e:
        print "Aborting:", e
        return 1
    try:
        return locked_main()
    finally:
        l.release()


if __name__ == "__main__":
    sys.exit(main() or 0)
