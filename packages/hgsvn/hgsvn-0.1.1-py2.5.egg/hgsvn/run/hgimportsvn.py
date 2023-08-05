#!/usr/bin/env python

from hgsvn.common import (
    run_command, run_hg, skip_dirs,
    get_svn_rev, get_svn_rev_or_head, get_svn_rev_or_0,
    get_first_svn_log_entry, get_last_svn_log_entry,
    hg_commit_from_svn_log_entry,
    hg_exclude_options,
)

import sys
import os
import shutil
import tempfile
import pysvn
import urllib # for unquoting URLs
from itertools import chain
from optparse import OptionParser


# TODO: an option to enable/disable svn:externals (disabled by default?)


def main():
    usage = "usage: %prog [-r SVN rev] <SVN URL> [local hg repo]"
    parser = OptionParser(usage)
    parser.add_option("-r", "--svn-rev", type="int", dest="svn_rev",
        help="SVN revision to checkout from")
    #parser.add_option("-w", "--svn-wc", dest="svn_wc", default="_svn_wc",
        #help="location of SVN working copy (default: ./_svn_wc)")
    (options, args) = parser.parse_args()
    if not 1 <= len(args) <= 2:
        parser.error("incorrect number of arguments")

    svn_url = args.pop(0).rstrip("/")
    local_repo = args and args.pop(0) or None

    # Get SVN info
    svn_client = pysvn.Client()
    if options.svn_rev:
        l = svn_client.info2(svn_url, recurse=False,
            revision=get_svn_rev(options.svn_rev))
    else:
        l = svn_client.info2(svn_url, recurse=False)
    _, svn_info = l[0]
    # e.g. u'svn://svn.twistedmatrix.com/svn/Twisted'
    repos_url = svn_info['repos_root_URL']
    # e.g. u'svn://svn.twistedmatrix.com/svn/Twisted/branches/xmpp-subprotocols-2178-2'
    svn_url = svn_info['URL']
    assert svn_url.startswith(repos_url)
    # e.g. u'/branches/xmpp-subprotocols-2178-2'
    svn_path = svn_url[len(repos_url):]
    # e.g. 'xmpp-subprotocols-2178-2'
    svn_branch = svn_path.rsplit("/", 1)[1]

    if not local_repo:
        local_repo = svn_branch
    if os.path.exists(local_repo):
        if not os.path.isdir(local_repo):
            raise ValueError("%s is not a directory" % local_repo)
    else:
        os.mkdir(local_repo)
    os.chdir(local_repo)

    # Get log entry for the SVN revision we will check out
    svn_copyfrom_path = None
    svn_copyfrom_revision = None
    if options.svn_rev:
        # If a specific rev was requested, get log entry just before or at rev
        svn_start_log = get_last_svn_log_entry(svn_url, options.svn_rev)
    else:
        # Otherwise, get log entry of branch creation
        svn_start_log = get_first_svn_log_entry(svn_url)
        for p in svn_start_log['changed_paths']:
            if p['path'] == svn_path:
                svn_copyfrom_path = p['copyfrom_path']
                svn_copyfrom_revision = p['copyfrom_revision']
                break
        if svn_copyfrom_path:
            print "SVN branch was copied from '%s' at rev %s" % (
                svn_copyfrom_path, svn_copyfrom_revision.number)
        else:
            print "SVN branch isn't a copy"
    # This is the revision we will checkout from
    svn_rev = get_svn_rev(svn_start_log['revision'].number)

    # Initialize hg repo
    if not os.path.exists(".hg"):
        run_hg(["init"])
    if svn_copyfrom_path:
        # Try to find an hg repo tracking the SVN branch which was copied
        copyfrom_branch = svn_copyfrom_path.lstrip("/")
        hg_copyfrom = os.path.join("..", copyfrom_branch)
        if (os.path.exists(os.path.join(hg_copyfrom, ".hg")) and
            os.path.exists(os.path.join(hg_copyfrom, ".svn"))):
            u = svn_client.info(hg_copyfrom).url
            if u != repos_url + svn_copyfrom_path:
                print "SVN URL %s in working copy %s doesn't match, ignoring" % (u, hg_copyfrom)
            else:
                # Find closest hg tag before requested SVN rev
                best_tag = None
                for line in run_hg(["tags", "-R", hg_copyfrom]).splitlines():
                    if not line.startswith("svn."):
                        continue
                    tag = line.split(None, 1)[0]
                    tag_num = int(tag.split(".")[1])
                    if tag_num <= svn_rev.number and (not best_tag or best_tag < tag_num):
                        best_tag = tag_num
                if not best_tag:
                    print "No hg tag matching rev %s in %s" % (svn_rev, hg_copyfrom)
                else:
                    run_hg(["pull", "-u", "-r", "svn.%d" % best_tag, hg_copyfrom])
    run_hg(["branch", svn_branch])

    # Stay on the same filesystem so as to have fast moves
    checkout_dir = tempfile.mkdtemp(dir=".")

    try:
        # Get SVN manifest and checkout
        print "* SVN checkout from rev %s" % svn_rev
        svn_client.checkout(svn_url, checkout_dir, revision=svn_rev)
        svn_manifest = []
        for st in svn_client.status(checkout_dir, ignore_externals=True):
            # NOTE: st.is_versioned is unreliable because it is also set for
            # ignored files not tracked by SVN
            if st.entry:
                u = st.entry.url
                assert u.startswith(svn_url)
                u = u[len(svn_url):].lstrip("/")
                if u:
                    svn_manifest.append(urllib.unquote(u))
        svn_files = set(skip_dirs(svn_manifest, checkout_dir))
        svn_dirs = sorted(set(svn_manifest) - svn_files)
        svn_files = list(svn_files)

        # All directories must exist, including empty ones
        # (both for hg and for moving .svn dirs later)
        for d in svn_dirs:
            if not os.path.isdir(d):
                if os.path.exists(d):
                    os.remove(d)
                os.mkdir(d)
        # Replace checked out files
        for f in svn_files:
            if os.path.exists(f):
                os.remove(f)
            os.rename(os.path.join(checkout_dir, f), f)

        try:
            # Add/remove new/old files
            if svn_files:
                run_hg(["addremove"] + hg_exclude_options, svn_files)
            hg_commit_from_svn_log_entry(svn_start_log)
            #hg_commit_from_svn_log_entry(svn_start_log, svn_files)
        except:
            run_command("hg revert --all")
            raise

        # Move SVN working copy here (don't forget base directory)
        for d in chain([""], svn_dirs):
            os.rename(os.path.join(checkout_dir, d, ".svn"), os.path.join(d, ".svn"))

    finally:
        shutil.rmtree(checkout_dir)
        pass

    print "Finished! You can pull all SVN history with 'hgpullsvn'."
    print "Also, you may have to run 'hg update'."


if __name__ == "__main__":
    main()

