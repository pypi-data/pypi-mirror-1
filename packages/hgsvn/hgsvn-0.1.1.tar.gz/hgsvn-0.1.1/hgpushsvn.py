#!/usr/bin/env python

import sys
import commands
import os
import shutil
import tempfile
import pysvn
import glob
from optparse import OptionParser


def shell_quote(s):
    return "'" + s.replace('\\', '\\\\').replace("'", "'\"'\"'") + "'"

def run_command(cmd, args=()):
    cmd += "".join(" " + shell_quote(a) for a in args)
    print "*", cmd
    st, out = commands.getstatusoutput(cmd)
    if st != 0:
        raise RuntimeError("command failed with non-zero return code (%d): %s:\n%s" % (st, cmd, out))
    return out

def map_svn_rev_to_hg(svn_rev, hg_rev="tip", local=False):
    """
    Record the mapping from an SVN revision number and an hg revision (default "tip").
    """
    cmd = local and "hg tag -l" or "hg tag"
    run_command(cmd + " -r %s svn.%d" % (strip_hg_rev(hg_rev), svn_rev))

def strip_hg_rev(rev_string):
    """
    Given a string identifying an hg revision, return a string identifying the
    same hg revision and suitable for revrange syntax (r1:r2).
    """
    if ":" in rev_string:
        return rev_string.rsplit(":", 1)[1]
    return rev_string

def get_hg_cset(rev_string):
    """
    Given a string identifying an hg revision, get the canonical changeset ID.
    """
    s = run_command("hg log -q -r %s" % rev_string)
    return s

def get_hg_revs(first_rev, last_rev="tip"):
    """
    Get a chronological list of revisions (changeset IDs) between the two
    revisions (included).
    """
    out = run_command("hg log -q -r %s:%s" %
        (strip_hg_rev(first_rev), strip_hg_rev(last_rev)))
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
    out = run_command("hg st -arm -X '.hg*' --rev %s" % rev_string)
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
    out = run_command("hg log -v -r %s" % rev_string)
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
    run_command("hg up -C %s" % end_rev)
    added, removed, modified = get_hg_changes(start_rev)
    # Add new files and dirs
    if added:
        run_command("svn add", get_ordered_dirs(added) + added)
    # Remove old files and empty dirs
    if removed:
        empty_dirs = [d for d in reversed(get_ordered_dirs(removed))
            if not run_command("hg st -c %s" %d)]
        run_command("svn rm", removed + empty_dirs)
    if added or removed or modified:
        details = get_hg_cset_details(end_rev)
        svn_client = pysvn.Client()
        print "*", "svn: checking in..."
        svn_rev = svn_client.checkin(".", details['description'])
        return svn_rev
    else:
        print "*", "svn: nothing to do"
        return None


def main():
    usage = "usage: %prog [-cf]"
    parser = OptionParser(usage)
    parser.add_option("-f", "--force", default=False, action="store_true",
        dest="force", help="push even if no hg tag found for current SVN rev.")
    parser.add_option("-c", "--collapse", default=False, action="store_true",
        dest="collapse", help="collapse all hg changesets in a single SVN commit")
    (options, args) = parser.parse_args()
    if len(args) != 0:
        parser.error("incorrect number of arguments")

    run_command("svn up")
    svn_client = pysvn.Client()
    svn_info = svn_client.info(".")
    svn_current_rev = svn_info.commit_revision
    # e.g. u'svn://svn.twistedmatrix.com/svn/Twisted'
    repos_url = svn_info.repos
    # e.g. u'svn://svn.twistedmatrix.com/svn/Twisted/branches/xmpp-subprotocols-2178-2'
    wc_url = svn_info.url
    assert wc_url.startswith(repos_url)
    # e.g. u'/branches/xmpp-subprotocols-2178-2'
    wc_base = wc_url[len(repos_url):]

    hg_start_rev = "svn.%d" % svn_current_rev.number
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
            hg_revs = get_hg_revs(hg_start_cset)
    if hg_revs is None:
        hg_revs = [strip_hg_rev(hg_start_cset), strip_hg_rev(get_hg_cset("tip"))]

    try:
        for prev_rev, next_rev in get_pairs(hg_revs):
            svn_rev = hg_push_svn(prev_rev, next_rev)
            if svn_rev:
                map_svn_rev_to_hg(svn_rev.number, next_rev, local=True)
    except:
        run_command("hg revert --all")
        raise

    run_command("svn up")

if __name__ == "__main__":
    main()

