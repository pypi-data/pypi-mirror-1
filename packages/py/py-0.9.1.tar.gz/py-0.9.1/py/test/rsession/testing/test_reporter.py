
""" reporter tests.

XXX there are a few disabled reporting tests because
they test for exact formatting as far as i can see.
I think it's rather better to directly invoke a
reporter and pass it some hand-prepared events to see
that running the reporter doesn't break shallowly. 

Otherwise, i suppose that some "visual" testing can usually be driven 
manually by user-input.  And when passing particular events
to a reporter it's also easier to check for one line
instead of having to know the order in which things are printed
etc. 


"""


import py, os
from py.__.test.rsession.rsession import LocalReporter, AbstractSession,\
    RemoteReporter
from py.__.test.rsession import repevent
from py.__.test.rsession.outcome import ReprOutcome, Outcome
from py.__.test.rsession.hostmanage import HostInfo
from py.__.test.rsession.box import Box
from py.__.test.rsession.testing.basetest import BasicRsessionTest
import sys
from StringIO import StringIO

class DummyGateway(object):
    def __init__(self, host):
        self.host = host

class DummyChannel(object):
    def __init__(self, host):
        self.gateway = DummyGateway(host)

class AbstractTestReporter(BasicRsessionTest):
    def prepare_outcomes(self):
        # possible outcomes
        try:
            1/0
        except:
            exc = py.code.ExceptionInfo()
        
        outcomes = [Outcome(()), 
            Outcome(skipped=True),
            Outcome(excinfo=exc),
            Outcome()]
        
        outcomes = [ReprOutcome(outcome.make_repr()) for outcome in outcomes]
        outcomes[3].signal = 11
        outcomes[0].passed = False
        
        return outcomes
    
    def report_received_item_outcome(self):
        item = self.getexample("pass")
        outcomes = self.prepare_outcomes()
        
        def boxfun(config, item, outcomes):
            hosts = [HostInfo("localhost")]
            r = self.reporter(config, hosts)
            ch = DummyChannel(hosts[0])
            for outcome in outcomes:
                r.report(repevent.ReceivedItemOutcome(ch, item, outcome))
        
        cap = py.io.StdCaptureFD()
        boxfun(self.config, item, outcomes)
        out, err = cap.reset()
        assert not err
        return out

    def _test_module(self):
        funcitem = self.getexample("pass")
        moditem = self.getmod()
        outcomes = self.prepare_outcomes()
        
        def boxfun(config, item, funcitem, outcomes):
            hosts = [HostInfo('localhost')]
            r = self.reporter(config, hosts)
            r.report(repevent.ItemStart(item))
            ch = DummyChannel(hosts[0])
            for outcome in outcomes:
                r.report(repevent.ReceivedItemOutcome(ch, funcitem, outcome))
        
        cap = py.io.StdCaptureFD()
        boxfun(self.config, moditem, funcitem, outcomes)
        out, err = cap.reset()
        assert not err
        return out

    def _test_full_module(self):
        tmpdir = py.test.ensuretemp("repmod")
        tmpdir.ensure("__init__.py")
        tmpdir.ensure("test_one.py").write(py.code.Source("""
        def test_x():
            pass
        """))
        tmpdir.ensure("test_two.py").write(py.code.Source("""
        import py
        py.test.skip("reason")
        """))
        tmpdir.ensure("test_three.py").write(py.code.Source("""
        sadsadsa
        """))
        
        def boxfun():
            config = py.test.config._reparse([str(tmpdir)])
            rootcol = py.test.collect.Directory(tmpdir)
            hosts = [HostInfo('localhost')]
            r = self.reporter(config, hosts)
            list(rootcol._tryiter(reporterror=lambda x : AbstractSession.reporterror(r.report, x)))

        cap = py.io.StdCaptureFD()
        boxfun()
        out, err = cap.reset()
        assert not err
        return out

    def test_failed_to_load(self):
        tmpdir = py.test.ensuretemp("failedtoload")
        tmpdir.ensure("__init__.py")
        tmpdir.ensure("test_three.py").write(py.code.Source("""
        sadsadsa
        """))
        def boxfun():
            config = py.test.config._reparse([str(tmpdir)])
            rootcol = py.test.collect.Directory(tmpdir)
            host = HostInfo('localhost')
            r = self.reporter(config, [host])
            r.report(repevent.TestStarted([host], config.topdir, ["a"]))
            r.report(repevent.RsyncFinished())
            list(rootcol._tryiter(reporterror=lambda x : AbstractSession.reporterror(r.report, x)))
            r.report(repevent.TestFinished())
            return r
        
        cap = py.io.StdCaptureFD()
        r = boxfun()
        out, err = cap.reset()
        assert not err
        assert out.find("1 failed in") != -1
        assert out.find("NameError: name 'sadsadsa' is not defined") != -1

    def _test_still_to_go(self):
        tmpdir = py.test.ensuretemp("stilltogo")
        tmpdir.ensure("__init__.py")
        cap = py.io.StdCaptureFD()
        config = py.test.config._reparse([str(tmpdir)])
        hosts = [HostInfo(i) for i in ["host1", "host2", "host3"]]
        r = self.reporter(config, hosts)
        r.report(repevent.TestStarted(hosts, config.topdir, ["a", "b", "c"]))
        for host in hosts:
            r.report(repevent.HostGatewayReady(host, ["a", "b", "c"]))
        for host in hosts:
            for root in ["a", "b", "c"]:
                r.report(repevent.HostRSyncRootReady(host, root))
        out, err = cap.reset()
        assert not err
        expected1 = "Test started, hosts: host1[0], host2[0], host3[0]"
        assert out.find(expected1) != -1
        for expected in py.code.Source("""
            host1[0]: READY (still 2 to go)
            host2[0]: READY (still 1 to go)
            host3[0]: READY
        """).lines:
            expected = expected.strip()
            assert out.find(expected) != -1

class TestLocalReporter(AbstractTestReporter):
    reporter = LocalReporter
    
    def test_report_received_item_outcome(self):
        assert self.report_received_item_outcome() == 'FsF.'

    def test_module(self):
        output = self._test_module()
        assert output.find("test_one") != -1
        assert output.endswith("FsF."), output
    
    def test_full_module(self):
        received = self._test_full_module()
        expected_lst = ["repmod/test_one.py", "FAILED TO LOAD MODULE",
                        "skipped", "reason"]
        for i in expected_lst:
            assert received.find(i) != -1

class TestRemoteReporter(AbstractTestReporter):
    reporter = RemoteReporter

    def test_still_to_go(self):
        self._test_still_to_go()

    def test_report_received_item_outcome(self):
        val = self.report_received_item_outcome()
        expected_lst = ["localhost", "FAILED",
                        "funcpass", "test_one",
                        "SKIPPED",
                        "PASSED"]
        for expected in expected_lst:
            assert val.find(expected) != -1
    
    def test_module(self):
        val = self._test_module()
        expected_lst = ["localhost", "FAILED",
                        "funcpass", "test_one",
                        "SKIPPED",
                        "PASSED"]
        for expected in expected_lst:
            assert val.find(expected) != -1
    
    def test_full_module(self):
        val = self._test_full_module()
        assert val.find("FAILED TO LOAD MODULE: repmod/test_three.py\n"\
        "\nSkipped ('reason') repmod/test_two.py") != -1
