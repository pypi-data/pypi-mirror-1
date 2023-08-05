#!/usr/bin/env python

from hgsvn.common import (
    run_command, run_hg, skip_dirs,
    get_svn_rev, get_svn_rev_or_head, get_svn_rev_or_0,
    iter_svn_log_entries,
    hg_commit_from_svn_log_entry,
    hg_exclude_options,
)

import sys
import os
import shutil
import tempfile
import pysvn
from optparse import OptionParser

"""
"""

#

"""
NOTE: interesting tests:
    * http://svn.python.org/projects/python/trunk/Mac :
        - files with space characters in them just before 45000
        - file and dir renames/removes between 46701 and 46723
"""


# TODO: an option to enable/disable svn:externals (disabled by default?)


def main():
    usage = "usage: %prog [SVN working copy]"
    parser = OptionParser(usage)
    #parser.add_option("-w", "--svn-wc", dest="svn_wc", default="_svn_wc",
        #help="location of SVN working copy (default: ./_svn_wc)")
    (options, args) = parser.parse_args()
    if len(args) > 1:
        parser.error("incorrect number of arguments")

    svn_wc = "."
    #svn_wc = args and args[0] or "."
    #if not os.path.exists(svn_wc):
        #raise RuntimeError("%s doesn't exist, please provide the path to a proper SVN working copy" % svn_wc)
    #svn_wc_is_separate = os.path.abspath(svn_wc) != os.path.abspath(".")

    # Get SVN info
    svn_client = pysvn.Client()
    svn_info = svn_client.info(svn_wc)
    current_rev = svn_info.revision
    next_rev = get_svn_rev(current_rev.number + 1)
    # e.g. u'svn://svn.twistedmatrix.com/svn/Twisted'
    repos_url = svn_info.repos
    # e.g. u'svn://svn.twistedmatrix.com/svn/Twisted/branches/xmpp-subprotocols-2178-2'
    wc_url = svn_info.url
    assert wc_url.startswith(repos_url)
    # e.g. u'/branches/xmpp-subprotocols-2178-2'
    wc_base = wc_url[len(repos_url):]

    # Get greatest revision number from SVN repo
    _, info_dict = svn_client.info2(repos_url, recurse=False)[0]
    svn_greatest_rev = info_dict['rev'].number
    if svn_greatest_rev < next_rev.number:
        # Avoid exceptions with svn_client.log when next_rev doesn't exist
        print "No revisions after %s in SVN repo, nothing to do" % svn_greatest_rev
        return

    # e.g. 'xmpp-subprotocols-2178-2'
    svn_branch = wc_base.rsplit("/", 1)[1]
    orig_branch = run_hg(["branch"])
    hg_branches = [l.split()[0] for l in run_hg(["branches"]).splitlines()]
    if svn_branch in hg_branches:
        run_hg(["up", svn_branch])
    run_hg(["branch", svn_branch])

    # Load SVN log starting from current rev
    # NOTE: by passing HEAD instead of an explicit rev number, we would
    # trigger an SVN error when the requested rev number is greater than the
    # greatest one in the repository.
    it_entries = iter_svn_log_entries(svn_wc, next_rev, #get_svn_rev_or_head())
        get_svn_rev(svn_greatest_rev))

    try:
        prev_svn_rev = current_rev
        for entry in it_entries:
            svn_rev = entry['revision']

            added_paths = []
            copied_paths = []
            removed_paths = []
            changed_paths = []
            for d in entry['changed_paths']:
                # e.g. u'/branches/xmpp-subprotocols-2178-2/twisted/words/test/test_jabberxmlstream.py'
                p = d['path']
                if not p.startswith(wc_base + "/"):
                    # Ignore changed files that are not part of this subdir
                    continue
                # e.g. u'twisted/words/test/test_jabberxmlstream.py'
                p = p[len(wc_base):].strip("/")
                if not p:
                    continue
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
                        else:
                            # Extract actual copied files (hg doesn't track dirs
                            # and will refuse "hg copy -A" with dirs)
                            r = run_hg(["st", "-nc", old_p])
                            for old_f in r.splitlines():
                                f = p + old_f[len(old_p):]
                                copied_paths.append((old_f, f))
                        continue
                if d['action'] == 'A':
                    added_paths.append(p)
                elif d['action'] == 'D':
                    removed_paths.append(p)

            # Update SVN + add/remove/commit hg
            try:
                # NOTE: the ignore_externals flag to svn_client.update does not
                # seem to work, which causes problems with obsolete externals URLs
                print "* SVN update to %s" % svn_rev
                #svn_client.update(svn_wc, revision=svn_rev,
                    #ignore_externals=True)
                run_command("svn", ["up", "--ignore-externals", "-r", svn_rev.number])
                if added_paths:
                    run_hg(["add"] + hg_exclude_options, added_paths)
                for old, new in copied_paths:
                    run_hg(["copy", "-A", old, new])
                if removed_paths:
                    run_hg(["remove", "-A"], removed_paths)
                if changed_paths:
                    hg_commit_from_svn_log_entry(entry)
            except:
                if prev_svn_rev:
                    svn_client.update(svn_wc, revision=prev_svn_rev)
                run_hg(["revert", "--all"])
                raise

            prev_svn_rev = svn_rev

        # TODO: detect externals with "svn_client.status" and update them as well
        #svn_client.update(svn_wc, revision=svn_rev,
            #ignore_externals=True)

    finally:
        work_branch = orig_branch or svn_branch
        run_hg(["up", work_branch])
        run_hg(["branch", work_branch])

if __name__ == "__main__":
    main()

