#!/usr/bin/env python

import sys
import commands
import os
import shutil
import tempfile
from itertools import chain
from optparse import OptionParser

def run_command(cmd):
    print "*", cmd
    st, out = commands.getstatusoutput(cmd)
    if st != 0:
        raise RuntimeError("command failed with non-zero return code (%d): %s:\n%s" % (st, cmd, out))
    return out


def main():
    usage = "usage: %prog <SVN URL> [SVN working copy]"
    parser = OptionParser(usage)
    (options, args) = parser.parse_args()
    if len(args) < 1 or len(args) > 2:
        parser.error("incorrect number of arguments")
    svn_url = args[0].rstrip("/")
    svn_wc = len(args) > 1 and args[1] or "."
    branch_name = svn_url.rsplit("/", 1)[1]

    # TODO: check that svn_wc isn't already an SVN working copy
    if not os.path.exists(svn_wc):
        os.mkdir(svn_wc)

    # Load hg manifest
    hg_manifest = run_command("hg manifest")
    hg_files = set(hg_manifest.splitlines())

    # Load SVN manifest
    svn_manifest = run_command("svn ls -R %s" % svn_url).splitlines()
    svn_dirs = [s for s in svn_manifest if s.endswith("/")]
    svn_files = set(svn_manifest) - set(svn_dirs)

    new_files = svn_files - hg_files
    old_files = hg_files - svn_files

    # Stay on the same filesystem so as to have fast moves
    checkout_dir = tempfile.mkdtemp(dir=".")

    try:
        # Create SVN working copy
        run_command("svn co '%s' %s" % (svn_url, checkout_dir))

        # All directories must exist, including empty ones
        # (both for hg and for moving .svn dirs later)
        for d in svn_dirs:
            if not os.path.exists(d):
                os.mkdir(d)
        # Replace checked out files
        for f in svn_files:
            if os.path.exists(f):
                os.remove(f)
            os.rename(os.path.join(checkout_dir, f), f)

        try:
            # Add/remove new/old files
            if new_files:
                run_command("hg add %s" % " ".join(new_files))
            if old_files:
                run_command("hg remove %s" % " ".join(old_files))
            # Create named branch
            run_command("hg branch %s" % branch_name)
            hg_message = "Updating to SVN branch %s" % branch_name
            run_command("hg ci -m '%s'" % hg_message)
        except RuntimeError:
            run_command("hg revert --all")
            raise

        # Move SVN working copy here
        for d in chain([""], svn_dirs):
            os.rename(os.path.join(checkout_dir, d, ".svn"), os.path.join(d, ".svn"))

    finally:
        shutil.rmtree(checkout_dir)

if __name__ == "__main__":
    main()

