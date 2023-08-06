"""hgimportsvn checks out the given Subversion URL, either from the specified
revision or from the first revision in the branch. The SVN checkout is then
augmented with a Mercurial repository containing the same files.

The SVN checkout and the Mercurial repository are created either in the
specified directory, or in a directory named after the last component of the
SVN URL (for example 'trunk').
"""

from hgsvn.common import (
    run_hg, run_svn, skip_dirs, rmtree,
    hg_commit_from_svn_log_entry, hg_exclude_options,
    svn_private_dir, hgsvn_private_dir, fixup_hgsvn_dir,
)
from hgsvn.svnclient import (
    get_first_svn_log_entry, get_last_svn_log_entry,
    get_svn_info, get_svn_status, svn_checkout, get_svn_versioned_files,
)
from hgsvn.run.common import run_parser, display_parser_error

import sys
import os
import tempfile
import urllib # for unquoting URLs
from itertools import chain
from optparse import OptionParser


# XXX add an option to enable/disable svn:externals?


def main():
    usage = "usage: %prog [-r SVN rev] [-p SVN peg rev] <SVN URL> [local checkout]"
    parser = OptionParser(usage)
    parser.add_option("-r", "--svn-rev", type="int", dest="svn_rev",
        help="SVN revision to checkout from")
    parser.add_option("-p", "--svn-peg", type="int", dest="svn_peg",
        help="SVN peg revision to locate checkout URL")
    parser.add_option("--no-hgignore", dest="hgignore", action="store_false",
        default=True, help="Don't autogenerate .hgignore")
    (options, args) = run_parser(parser, __doc__)
    if not 1 <= len(args) <= 2:
        display_parser_error(parser, "incorrect number of arguments")

    svn_url = args.pop(0).rstrip("/")
    local_repo = args and args.pop(0) or None
    if options.svn_peg:
       svn_url += "@" + str(options.svn_peg)

    # Get SVN info
    svn_info = get_svn_info(svn_url, options.svn_rev)
    # e.g. u'svn://svn.twistedmatrix.com/svn/Twisted'
    repos_url = svn_info['repos_url']
    # e.g. u'svn://svn.twistedmatrix.com/svn/Twisted/branches/xmpp-subprotocols-2178-2'
    svn_url = svn_info['url']
    assert svn_url.startswith(repos_url)
    # e.g. u'/branches/xmpp-subprotocols-2178-2'
    svn_path = svn_url[len(repos_url):]
    # e.g. 'xmpp-subprotocols-2178-2'
    svn_branch = svn_url.split("/")[-1]
    svn_greatest_rev = svn_info['last_changed_rev']
    if options.svn_peg:
       svn_url += "@" + str(options.svn_peg)

    if not local_repo:
        local_repo = svn_branch
    if os.path.exists(local_repo):
        if not os.path.isdir(local_repo):
            raise ValueError("%s is not a directory" % local_repo)
    else:
        os.mkdir(local_repo)
    fixup_hgsvn_dir(local_repo)
    os.chdir(local_repo)

    # Get log entry for the SVN revision we will check out
    svn_copyfrom_path = None
    svn_copyfrom_revision = None
    if options.svn_rev:
        # If a specific rev was requested, get log entry just before or at rev
        svn_start_log = get_last_svn_log_entry(svn_url, 1, options.svn_rev)
    else:
        # Otherwise, get log entry of branch creation
        svn_start_log = get_first_svn_log_entry(svn_url, 1, svn_greatest_rev)
        for p in svn_start_log['changed_paths']:
            if p['path'] == svn_path:
                svn_copyfrom_path = p['copyfrom_path']
                svn_copyfrom_revision = p['copyfrom_revision']
                break
        if svn_copyfrom_path:
            print "SVN branch was copied from '%s' at rev %s" % (
                svn_copyfrom_path, svn_copyfrom_revision)
        else:
            print "SVN branch isn't a copy"
    # This is the revision we will checkout from
    svn_rev = svn_start_log['revision']

    # Initialize hg repo
    if not os.path.exists(".hg"):
        run_hg(["init"])
    if svn_copyfrom_path:
        # Try to find an hg repo tracking the SVN branch which was copied
        copyfrom_branch = svn_copyfrom_path.split("/")[-1]
        hg_copyfrom = os.path.join("..", copyfrom_branch)
        if (os.path.exists(os.path.join(hg_copyfrom, ".hg")) and
            os.path.exists(os.path.join(hg_copyfrom, svn_private_dir))):
            u = get_svn_info(hg_copyfrom)['url']
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
                    if tag_num <= svn_copyfrom_revision and (not best_tag or best_tag < tag_num):
                        best_tag = tag_num
                if not best_tag:
                    print "No hg tag matching rev %s in %s" % (svn_rev, hg_copyfrom)
                else:
                    # Don't use "pull -u" because it fails with hg 0.9.5
                    # ("branch default not found")
                    run_hg(["pull", "-r", "svn.%d" % best_tag, hg_copyfrom])
                    # Not specifying "tip" fails with hg 0.9.5
                    # ("branch default not found")
                    run_hg(["up", "tip"])
    run_hg(["branch", svn_branch])

    svn_ignores = filter(None, [s.strip()
        for s in run_svn(['propget', 'svn:ignore', svn_url]).splitlines()])

    if options.hgignore:
        # Generate .hgignore file to ignore .svn and .hgsvn directories
        f = open(".hgignore", "a")
        try:
            f.write("\n# Automatically generated by `hgimportsvn`\n")
            f.write("syntax:glob\n%s\n" %
                "\n".join([svn_private_dir, hgsvn_private_dir]))
            f.write("\n# These lines are suggested according to the svn:ignore property")
            f.write("\n# Feel free to enable them by uncommenting them")
            f.write("\nsyntax:glob\n")
            f.write("".join("#%s\n" % s for s in svn_ignores))
        finally:
            f.close()

    # Stay on the same filesystem so as to have fast moves
    checkout_dir = tempfile.mkdtemp(dir=".")

    try:
        # Get SVN manifest and checkout
        svn_checkout(svn_url, checkout_dir, svn_rev)
        svn_manifest = get_svn_versioned_files(checkout_dir)

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
            run_hg(["revert", "--all"])
            raise

        # Move SVN working copy here (don't forget base directory)
        for d in chain([""], svn_dirs):
            os.rename(os.path.join(checkout_dir, d, svn_private_dir), os.path.join(d, svn_private_dir))

    finally:
        rmtree(checkout_dir)
        pass

    print "Finished! You can now pull all SVN history with 'hgpullsvn'."


if __name__ == "__main__":
    main()

