
import os
import locale
from datetime import datetime
import time
from subprocess import Popen, PIPE, STDOUT

try:
    import commands
except ImportError:
    commands = None

hg_commit_prefix = "[svn] "
# This seems sufficient for excluding all .svn (sub)directories
hg_exclude_options = ["-X", ".svn", "-X", "**/.svn"]


locale_encoding = locale.getpreferredencoding()

def shell_quote(s):
    return "'" + s.replace('\\', '\\\\').replace("'", "'\"'\"'") + "'"

def _run_raw_command(cmd, args):
    cmd_string = "%s %s" % (cmd,  " ".join(map(shell_quote, args)))
    print "*", cmd_string
    pipe = Popen([cmd] + args, executable=cmd, stdout=PIPE, stderr=PIPE)
    out, err = pipe.communicate()
    if pipe.returncode != 0:
        raise RuntimeError("command failed with non-zero return code (%d): %s\n%s"
            % (pipe.returncode, cmd_string, err))
    return out

def _run_raw_shell_command(cmd):
    print "*", cmd
    st, out = commands.getstatusoutput(cmd)
    if st != 0:
        raise RuntimeError("command failed with non-zero return code (%d): %s:\n%s" % (st, cmd, out))
    return out

def run_command(cmd, args=None, bulk_args=None, encoding=None):
    """
    Run a command without using the shell.
    """
    def _transform_arg(a):
        if isinstance(a, unicode):
            a = a.encode(encoding or locale_encoding)
        elif not isinstance(a, str):
            a = str(a)
        return a

    if not bulk_args:
        return _run_raw_command(cmd, map(_transform_arg, args))
    max_args_num = 254
    i = 0
    out = ""
    while i < len(bulk_args):
        stop = i + max_args_num - len(args)
        sub_args = []
        for a in bulk_args[i:stop]:
            sub_args.append(_transform_arg(a))
        out += _run_raw_command(cmd, args + sub_args)
        i = stop
    return out

def run_shell_command(cmd, args=None, bulk_args=None, encoding=None):
    """
    Run a shell command, properly quoting and encoding arguments.
    Probably only works on Un*x-like systems.
    """
    def _quote_arg(a):
        if isinstance(a, unicode):
            a = a.encode(encoding or locale_encoding)
        elif not isinstance(a, str):
            a = str(a)
        return shell_quote(a)

    if args:
        cmd += " " + " ".join(_quote_arg(a) for a in args)
    max_args_num = 254
    i = 0
    out = ""
    if not bulk_args:
        return _run_raw_shell_command(cmd)
    while i < len(bulk_args):
        stop = i + max_args_num - len(args)
        sub_args = []
        for a in bulk_args[i:stop]:
            sub_args.append(_quote_arg(a))
        sub_cmd = cmd + " " + " ".join(sub_args)
        out += _run_raw_shell_command(sub_cmd)
        i = stop
    return out

def run_hg(args=None, bulk_args=None):
    default_args = ["--encoding", "utf-8"]
    return run_command("hg", args=default_args + (args or []),
        bulk_args=bulk_args, encoding="utf-8")

def run_svn(args=None, bulk_args=None):
    return run_command("svn", args=args, bulk_args=bulk_args)

def skip_dirs(paths, basedir="."):
    return [p for p in paths if not os.path.isdir(os.path.join(basedir, p))]


def hg_commit_from_svn_log_entry(entry, files=None):
    """
    Given an SVN log entry and an optional sequence of files, do an hg commit.
    """
    # This will use the local timezone for displaying commit times
    timestamp = int(entry['date'])
    hg_date = str(datetime.fromtimestamp(timestamp))
    # Uncomment this one one if you prefer UTC commit times
    #hg_date = "%d 0" % timestamp
    options = ["ci", "-m", hg_commit_prefix + entry['message'],
        "-u", entry['author'], "-d", hg_date]
    if files:
        options += list(files)
    run_hg(options)
    hg_tag_svn_rev(entry['revision'])

def hg_tag_svn_rev(rev_number):
    """
    Put a local hg tag according to the SVN revision.
    """
    run_hg(["tag", "-l", "svn.%d" % rev_number])

def get_svn_rev_from_hg():
    """
    Get the current SVN revision as reflected by the hg working copy.
    """
    tags = run_hg(['parents', '--template', '{tags}']).strip().split()
    for tag in tags:
        if tag.startswith('svn.'):
            return int(tag.split('.')[1])
    return None

