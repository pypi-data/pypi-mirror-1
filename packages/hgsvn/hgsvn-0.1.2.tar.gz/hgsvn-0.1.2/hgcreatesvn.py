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
    details = get_hg_cset_details(end_rev)
    # Add new files and dirs
    if added:
        run_command("svn -q add", get_ordered_dirs(added) + added)
    # Remove old files and empty dirs
    if removed:
        empty_dirs = [d for d in reversed(get_ordered_dirs(removed))
            if not run_command("hg st -c %s" %d)]
        run_command("svn rm", removed + empty_dirs)
    if added or removed or modified:
        svn_client = pysvn.Client()
        svn_rev = svn_client.checkin(".", details['description'])
        return svn_rev
    else:
        return None

def get_svn_repos_info(svn_url):
    """
    Get the info dict for an SVN repository (rather than a working copy).
    """
    svn_client = pysvn.Client()
    _, info_dict = svn_client.info2(svn_url, recurse=False)[0]
    return info_dict


def main():
    usage = "usage: %prog [-r revision] <SVN URL>"
    parser = OptionParser(usage)
    parser.add_option("-r", "--rev", dest="start_rev", default="tip",
            help="hg revision to start SVN branch from")
    (options, args) = parser.parse_args()
    if len(args) != 1:
        parser.error("incorrect number of arguments")

    # TODO: check that current dir isn't already an SVN working copy

    hg_start_rev = options.start_rev
    hg_start_cset = get_hg_cset(hg_start_rev)
    svn_url = args[0].rstrip("/")
    branch_name = svn_url.rsplit("/", 1)[1]

    import_dir = tempfile.mkdtemp()
    # Stay on the same filesystem so as to have fast moves
    checkout_dir = tempfile.mkdtemp(dir=".")

    try:
        run_command("hg archive -r %s %s" % (hg_start_rev, import_dir))
        # Remove special files created by 'hg archive'
        for f in glob.glob(os.path.join(import_dir, ".hg*")):
            if os.path.isdir(f):
                shutil.rmtree(f)
            else:
                os.remove(f)
        svn_client = pysvn.Client()
        # TODO: check that svn_url doesn't exist yet, otherwise mistakes can be painful
        try:
            get_svn_repos_info(svn_url)
        except pysvn.ClientError, e:
            pass
        else:
            raise RuntimeError("%s already exists, refusing to create" % svn_url)
        svn_start_rev = svn_client.import_(import_dir, svn_url,
            "Initial import from Mercurial rev '%s'" % hg_start_cset)
        map_svn_rev_to_hg(svn_start_rev.number, hg_start_cset)

        # Create temporary hg clone and checkout newly-created SVN branch
        os.rmdir(checkout_dir)
        run_command("hg clone -U . %s" % checkout_dir)
        run_command("svn co '%s' %s" % (svn_url, checkout_dir))

        # Iterate hg changesets and commit them to SVN
        old_dir = os.path.abspath(os.getcwd())
        try:
            os.chdir(checkout_dir)
            for prev_rev, next_rev in get_pairs(get_hg_revs(hg_start_cset)):
                svn_rev = hg_push_svn(prev_rev, next_rev)
                if svn_rev is not None:
                    os.chdir(old_dir)
                    map_svn_rev_to_hg(svn_rev.number, next_rev, local=True)
                    os.chdir(checkout_dir)
        finally:
            os.chdir(old_dir)

        #run_command("hg branch %s" % branch_name)
        run_command("hg ci", ["-m", "set branch and tags"])

        # Create SVN working copy in hg repository, by moving .svn dirs here
        for d in get_svn_subdirs(checkout_dir):
            os.rename(os.path.join(checkout_dir, d, ".svn"), os.path.join(d, ".svn"))
        run_command("svn up")

    finally:
        shutil.rmtree(checkout_dir)
        shutil.rmtree(import_dir)

if __name__ == "__main__":
    main()

