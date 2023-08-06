"""
interactive debugging with the Python Debugger.
"""
import py
import pdb, sys, linecache
from py.__.test.outcome import Skipped

def pytest_addoption(parser):
    group = parser.getgroup("general") 
    group._addoption('--pdb',
               action="store_true", dest="usepdb", default=False,
               help="start pdb (the Python debugger) on errors.")


def pytest_configure(config):
    if config.option.usepdb:
        if config.getvalue("looponfail"):
            raise config.Error("--pdb incompatible with --looponfail.")
        if config.option.dist != "no":
            raise config.Error("--pdb incomptaible with distributing tests.")
        config.pluginmanager.register(PdbInvoke())

class PdbInvoke:
    def pytest_runtest_makereport(self, item, call):
        if call.excinfo and not call.excinfo.errisinstance(Skipped): 
            # XXX hack hack hack to play well with capturing
            capman = item.config.pluginmanager.impname2plugin['capturemanager']
            capman.suspendcapture() 

            tw = py.io.TerminalWriter()
            repr = call.excinfo.getrepr()
            repr.toterminal(tw) 
            post_mortem(call.excinfo._excinfo[2])

            # XXX hack end 
            capman.resumecapture_item(item)

class Pdb(py.std.pdb.Pdb):
    def do_list(self, arg):
        self.lastcmd = 'list'
        last = None
        if arg:
            try:
                x = eval(arg, {}, {})
                if type(x) == type(()):
                    first, last = x
                    first = int(first)
                    last = int(last)
                    if last < first:
                        # Assume it's a count
                        last = first + last
                else:
                    first = max(1, int(x) - 5)
            except:
                print '*** Error in argument:', repr(arg)
                return
        elif self.lineno is None:
            first = max(1, self.curframe.f_lineno - 5)
        else:
            first = self.lineno + 1
        if last is None:
            last = first + 10
        filename = self.curframe.f_code.co_filename
        breaklist = self.get_file_breaks(filename)
        try:
            for lineno in range(first, last+1):
                # start difference from normal do_line
                line = self._getline(filename, lineno)
                # end difference from normal do_line
                if not line:
                    print '[EOF]'
                    break
                else:
                    s = repr(lineno).rjust(3)
                    if len(s) < 4: s = s + ' '
                    if lineno in breaklist: s = s + 'B'
                    else: s = s + ' '
                    if lineno == self.curframe.f_lineno:
                        s = s + '->'
                    print s + '\t' + line,
                    self.lineno = lineno
        except KeyboardInterrupt:
            pass
    do_l = do_list

    def _getline(self, filename, lineno):
        if hasattr(filename, "__source__"):
            try:
                return filename.__source__.lines[lineno - 1] + "\n"
            except IndexError:
                return None
        return linecache.getline(filename, lineno)

    def get_stack(self, f, t):
        # Modified from bdb.py to be able to walk the stack beyond generators,
        # which does not work in the normal pdb :-(
        stack, i = pdb.Pdb.get_stack(self, f, t)
        if f is None:
            i = max(0, len(stack) - 1)
        return stack, i

def post_mortem(t):
    # modified from pdb.py for the new get_stack() implementation
    p = Pdb()
    p.reset()
    p.interaction(None, t)

def set_trace():
    # again, a copy of the version in pdb.py
    Pdb().set_trace(sys._getframe().f_back)


class TestPDB: 
    def pytest_funcarg__pdblist(self, request):
        monkeypatch = request.getfuncargvalue("monkeypatch")
        pdblist = []
        def mypdb(*args):
            pdblist.append(args)
        monkeypatch.setitem(globals(), 'post_mortem', mypdb)
        return pdblist 

    def test_incompatibility_messages(self, testdir):
        Error = py.test.config.Error
        py.test.raises(Error, "testdir.parseconfigure('--pdb', '--looponfail')")
        py.test.raises(Error, "testdir.parseconfigure('--pdb', '-n 3')")
        py.test.raises(Error, "testdir.parseconfigure('--pdb', '-d')")
         
    def test_pdb_on_fail(self, testdir, pdblist):
        rep = testdir.inline_runsource1('--pdb', """
            def test_func(): 
                assert 0
        """)
        assert rep.failed
        assert len(pdblist) == 1
        tb = py.code.Traceback(pdblist[0][0])
        assert tb[-1].name == "test_func"

    def test_pdb_on_skip(self, testdir, pdblist):
        rep = testdir.inline_runsource1('--pdb', """
            import py
            def test_func():
                py.test.skip("hello")
        """)
        assert rep.skipped 
        assert len(pdblist) == 0

    def test_pdb_interaction(self, testdir):
        p1 = testdir.makepyfile("""
            def test_1():
                i = 0
                assert i == 1
        """)
        child = testdir.spawn_pytest("--pdb %s" % p1)
        #child.expect(".*def test_1.*")
        child.expect(".*i = 0.*")
        child.expect("(Pdb)")
        child.sendeof()
        child.expect("1 failed")
        if child.isalive(): 
            child.wait()

