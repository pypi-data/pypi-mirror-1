
from _test import *

from hgsvn import common


class TestCommands(object):
    def test_hg(self):
        s = common.run_hg(['version'], ['-q'])
        s = s.split()[0]
        eq_(s.lower(), 'mercurial')

    def test_svn(self):
        s = common.run_svn(['--version'], ['-q'])
        eq_(s.split('.')[0], '1')

class CommandsBase(object):
    def test_echo(self):
        echo_string = 'foo'
        s = self.command_func('echo', [echo_string])
        eq_(s.rstrip(), echo_string)

    def test_echo_with_escapes(self):
        echo_string = 'foo \n"\' baz'
        s = self.command_func('echo', [echo_string])
        eq_(s.rstrip(), echo_string)

    def test_bulk_args(self):
        sep = '-'
        args = ['a', 'b', 'c']
        n_args = len(args)
        bulk_args = ['%d' % i for i in xrange(3000)]
        out = self.command_func('echo', [sep] + args, bulk_args)
        sub_results = out.split(sep)
        eq_(sub_results.pop(0).strip(), "")
        bulk_pos = 0
        for s in sub_results:
            l = s.split()
            eq_(l[:n_args], args)
            n_bulk = len(l) - n_args
            assert n_bulk < 256
            eq_(l[n_args:], bulk_args[bulk_pos:bulk_pos + n_bulk])
            bulk_pos += n_bulk
        eq_(bulk_pos, len(bulk_args))


class TestShellCommands(CommandsBase):
    command_func = staticmethod(common.run_shell_command)

class TestNonShellCommands(CommandsBase):
    command_func = staticmethod(common.run_command)

