import py
from py.__.test.outcome import Outcome, Failed, Passed, Skipped

class Session(object):
    """
        A Session gets test Items from Collectors, # executes the
        Items and sends the Outcome to the Reporter.
    """
    def __init__(self, config): 
        self._memo = []
        self.config = config 

    def shouldclose(self): 
        return False 

    def header(self, colitems):
        """ setup any neccessary resources ahead of the test run. """
        if not self.config.option.nomagic:
            py.magic.invoke(assertion=1)

    def footer(self, colitems):
        """ teardown any resources after a test run. """ 
        py.test.collect.Function._state.teardown_all()
        if not self.config.option.nomagic:
            py.magic.revoke(assertion=1)

    def fixoptions(self):
        """ check, fix and determine conflicting options. """
        option = self.config.option
        # implied options
        if option.usepdb:
            if not option.nocapture:
                option.nocapture = True
        # conflicting options
        if option.looponfailing and option.usepdb:
            raise ValueError, "--looponfailing together with --pdb not supported."
        if option.looponfailing and option.dist:
            raise ValueError, "--looponfailing together with --dist not supported."
        if option.executable and option.usepdb:
            raise ValueError, "--exec together with --pdb not supported."

    def start(self, colitem): 
        """ hook invoked before each colitem.run() invocation. """ 

    def finish(self, colitem, outcome): 
        """ hook invoked after each colitem.run() invocation. """ 
        self._memo.append((colitem, outcome))

    def startiteration(self, colitem, subitems): 
        pass 

    def getitemoutcomepairs(self, cls): 
        return [x for x in self._memo if isinstance(x[1], cls)]

    def main(self): 
        """ main loop for running tests. """
        colitems = self.config.getcolitems()
        try:
            self.header(colitems) 
            try:
                try:
                    for colitem in colitems: 
                        self.runtraced(colitem)
                except KeyboardInterrupt: 
                    raise 
            finally: 
                self.footer(colitems) 
        except Exit, ex:
            pass
        return self.getitemoutcomepairs(Failed)

    def runtraced(self, colitem):
        if self.shouldclose(): 
            raise Exit, "received external close signal" 

        outcome = None 
        colitem.startcapture() 
        try: 
            self.start(colitem)
            try: 
                try:
                    if colitem._stickyfailure: 
                        raise colitem._stickyfailure 
                    outcome = self.run(colitem) 
                except (KeyboardInterrupt, Exit): 
                    raise 
                except Outcome, outcome: 
                    if outcome.excinfo is None: 
                        outcome.excinfo = py.code.ExceptionInfo() 
                except: 
                    excinfo = py.code.ExceptionInfo() 
                    outcome = Failed(excinfo=excinfo) 
                assert (outcome is None or 
                        isinstance(outcome, (list, Outcome)))
            finally: 
                self.finish(colitem, outcome) 
            if isinstance(outcome, Failed) and self.config.option.exitfirst:
                py.test.exit("exit on first problem configured.", item=colitem)
        finally: 
            colitem.finishcapture()

    def run(self, colitem): 
        if self.config.option.collectonly and isinstance(colitem, py.test.collect.Item): 
            return 
        if isinstance(colitem, py.test.collect.Item): 
            colitem._skipbykeyword(self.config.option.keyword)
        res = colitem.run() 
        if res is None: 
            return Passed() 
        elif not isinstance(res, (list, tuple)): 
            raise TypeError("%r.run() returned neither "
                            "list, tuple nor None: %r" % (colitem, res))
        else: 
            finish = self.startiteration(colitem, res)
            try: 
                for name in res: 
                    obj = colitem.join(name) 
                    assert obj is not None 
                    self.runtraced(obj) 
            finally: 
                if finish: 
                    finish() 
        return res 

class Exit(Exception):
    """ for immediate program exits without tracebacks and reporter/summary. """
    def __init__(self, msg="unknown reason", item=None):
        self.msg = msg 
        Exception.__init__(self, msg)

def exit(msg, item=None): 
    raise Exit(msg=msg, item=item)

