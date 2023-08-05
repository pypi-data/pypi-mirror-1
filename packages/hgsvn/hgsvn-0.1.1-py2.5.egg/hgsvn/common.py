
import pysvn

import os
import commands
import locale
from datetime import datetime
import time


# XXX hg option -X (in add and addremove) seems very fragile,
# perhaps find a replacement?
hg_exclude_options = ["-X", ".svn", "-X", "**/.svn"]

# TODO: provide a fallback for the commands module (which is Unix-specific)
# see http://ivory.idyll.org/blog/mar-07/replacing-commands-with-subprocess


shell_encoding = locale.getpreferredencoding()

def shell_quote(s):
    return "'" + s.replace('\\', '\\\\').replace("'", "'\"'\"'") + "'"

def _run_raw_command(cmd):
    print "*", cmd
    st, out = commands.getstatusoutput(cmd)
    if st != 0:
        #f = file("cmd", "wb")
        #f.write(cmd)
        #f.write("\n")
        #f.close()
        raise RuntimeError("command failed with non-zero return code (%d): %s:\n%s" % (st, cmd, out))
    return out

def run_command(cmd, args=None, bulk_args=None, encoding=None):
    """
    Run a shell command, properly quoting and encoding arguments.
    """
    def _quote_arg(a):
        if isinstance(a, unicode):
            a = a.encode(encoding or shell_encoding)
        elif not isinstance(a, str):
            a = str(a)
        return shell_quote(a)

    max_args_num = 254
    if args:
        cmd += " " + " ".join(_quote_arg(a) for a in args)
    i = 0
    out = ""
    if not bulk_args:
        return _run_raw_command(cmd)
    while i < len(bulk_args):
        stop = i + max_args_num - len(args)
        sub_args = []
        for a in bulk_args[i:stop]:
            sub_args.append(_quote_arg(a))
        sub_cmd = cmd + " " + " ".join(sub_args)
        out += _run_raw_command(sub_cmd)
        i = stop
    return out

def run_hg(args=None, bulk_args=None):
    default_args = ["--encoding", "utf-8"]
    return run_command("hg", args=default_args + (args or []),
        bulk_args=bulk_args, encoding="utf-8")

def skip_dirs(paths, basedir="."):
    return [p for p in paths if not os.path.isdir(os.path.join(basedir, p))]

def get_first_svn_log_entry(svn_url, rev_number=None):
    """
    Get the first log entry after (or at) the given revision number in an SVN branch.
    By default the revision number is set to 0, which will give you the log
    entry corresponding to the branch creaction.

    NOTE: to know whether the branch creation corresponds to an SVN import or
    a copy from another branch, inspect elements of the 'changed_paths' entry
    in the returned dictionary.
    """
    c = pysvn.Client()
    entries = c.log(svn_url, discover_changed_paths=True, limit=1,
        revision_start=get_svn_rev_or_0(rev_number),
        revision_end=get_svn_rev_or_head())
    return entries[0]

def get_last_svn_log_entry(svn_url, rev_number=None):
    """
    Get the last log entry before (or at) the given revision number in an SVN branch.
    By default the revision number is set to HEAD, which will give you the log
    entry corresponding to the latest commit in branch.
    """
    c = pysvn.Client()
    entries = c.log(svn_url, discover_changed_paths=True, limit=1,
        revision_start=get_svn_rev_or_head(rev_number),
        revision_end=get_svn_rev_or_0())
    return entries[0]


log_duration_threshold = 10.0
log_min_chunk_length = 10

def iter_svn_log_entries(svn_url, first_rev, last_rev):
    """
    Iterate over SVN log entries between first_rev and last_rev.

    This function features chunked log fetching so that it isn't too nasty
    to the SVN server if many entries are requested.
    """
    c = pysvn.Client()
    until_end = (last_rev.kind == pysvn.opt_revision_kind.head)
    cur_rev_number = first_rev.number
    chunk_length = log_min_chunk_length
    while until_end or cur_rev_number <= last_rev.number:
        cur_rev = get_svn_rev(cur_rev_number)
        print "* SVN log from %s, getting %d entries" % (cur_rev, chunk_length)
        start_t = time.time()
        entries = c.log(svn_url, discover_changed_paths=True,
            revision_start=get_svn_rev(cur_rev_number),
            revision_end=last_rev, limit=chunk_length)
        duration = time.time() - start_t
        if not entries:
            break
        for e in entries:
            yield e
        cur_rev_number = e['revision'].number + 1
        # Adapt chunk length based on measured request duration
        if duration < log_duration_threshold:
            chunk_length = int(chunk_length * 2.0)
        elif duration > log_duration_threshold * 2:
            chunk_length = max(log_min_chunk_length, int(chunk_length / 2.0))


def hg_commit_from_svn_log_entry(entry, files=None):
    """
    Given an SVN log entry and an optional sequence of files, do an hg commit.
    """
    # This will use the local timezone for displaying commit times
    timestamp = int(entry['date'])
    hg_date = str(datetime.fromtimestamp(timestamp))
    # Uncomment this one one if you prefer UTC commit times
    #hg_date = "%d 0" % timestamp
    options = ["ci", "-m", "[svn] %s" % entry['message'],
        "-u", entry['author'], "-d", hg_date]
    if files:
        options += list(files)
    run_hg(options)
    run_hg(["tag", "-l", "svn.%d" % entry['revision'].number])

def get_svn_rev_or_head(rev_number=None):
    """
    Get an SVN revision object corresponding to the given revision number
    (if non-None and non-zero), or to HEAD.
    """
    return (rev_number is not None
        and pysvn.Revision(pysvn.opt_revision_kind.number, rev_number)
        or pysvn.Revision(pysvn.opt_revision_kind.head))

def get_svn_rev_or_0(rev_number=None):
    """
    Get an SVN revision object corresponding to the given revision number
    (if specified), or to revision 0.
    """
    return pysvn.Revision(pysvn.opt_revision_kind.number, rev_number or 0)

def get_svn_rev(rev_number):
    """
    Get an SVN revision object corresponding to the given revision number.
    """
    return pysvn.Revision(pysvn.opt_revision_kind.number, rev_number)

