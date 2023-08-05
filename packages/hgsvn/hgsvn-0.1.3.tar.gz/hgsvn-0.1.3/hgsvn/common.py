
from hgsvn.errors import ExternalCommandFailed

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


# Windows compatibility code by Bill Baxter
if os.name == "nt":
    def find_program(name):
        """
        Find the name of the program for Popen.
        Windows is finnicky about having the complete file name. Popen
        won't search the %PATH% for you automatically.
        (Adapted from ctypes.find_library)
        """
        # See MSDN for the REAL search order.
        base, ext = os.path.splitext(name)
        if ext:
            exts = [ext]
        else:
            exts = ['.bat', '.exe']
        for directory in os.environ['PATH'].split(os.pathsep):
            for e in exts:
                fname = os.path.join(directory, base + e)
                if os.path.exists(fname):
                    return fname
        return None
else:
    def find_program(name):
        """
        Find the name of the program for Popen.
        On Unix, popen isn't picky about having absolute paths.
        """
        return name


locale_encoding = locale.getpreferredencoding()

def shell_quote(s):
    if os.name == "nt":
        q = '"'
    else:
        q = "'"
    return q + s.replace('\\', '\\\\').replace("'", "'\"'\"'") + q

def _run_raw_command(cmd, args, fail_if_stderr=False):
    cmd_string = "%s %s" % (cmd,  " ".join(map(shell_quote, args)))
    print "*", cmd_string
    pipe = Popen([cmd] + args, executable=cmd, stdout=PIPE, stderr=PIPE)
    out, err = pipe.communicate()
    if pipe.returncode != 0 or (fail_if_stderr and err.strip()):
        raise ExternalCommandFailed(
            "External program failed (return code %d): %s\n%s"
            % (pipe.returncode, cmd_string, err))
    return out

def _run_raw_shell_command(cmd):
    print "*", cmd
    st, out = commands.getstatusoutput(cmd)
    if st != 0:
        raise ExternalCommandFailed(
            "External program failed with non-zero return code (%d): %s\n%s"
            % (st, cmd, out))
    return out

def run_command(cmd, args=None, bulk_args=None, encoding=None, fail_if_stderr=False):
    """
    Run a command without using the shell.
    """
    args = args or []
    def _transform_arg(a):
        if isinstance(a, unicode):
            a = a.encode(encoding or locale_encoding)
        elif not isinstance(a, str):
            a = str(a)
        return a

    cmd = find_program(cmd)
    if not bulk_args:
        return _run_raw_command(cmd, map(_transform_arg, args), fail_if_stderr)
    max_args_num = 254
    i = 0
    out = ""
    while i < len(bulk_args):
        stop = i + max_args_num - len(args)
        sub_args = []
        for a in bulk_args[i:stop]:
            sub_args.append(_transform_arg(a))
        out += _run_raw_command(cmd, args + sub_args, fail_if_stderr)
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
    """
    Run a Mercurial command.
    """
    default_args = ["--encoding", "utf-8"]
    return run_command("hg", args=default_args + (args or []),
        bulk_args=bulk_args, encoding="utf-8")

def run_svn(args=None, bulk_args=None, fail_if_stderr=False):
    """
    Run an SVN command.
    """
    return run_command("svn",
        args=args, bulk_args=bulk_args, fail_if_stderr=fail_if_stderr)

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

