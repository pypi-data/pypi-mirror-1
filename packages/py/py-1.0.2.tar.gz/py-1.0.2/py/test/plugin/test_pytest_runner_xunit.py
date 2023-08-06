#
# test correct setup/teardowns at
# module, class, and instance level

def test_module_and_function_setup(testdir):
    reprec = testdir.inline_runsource(""" 
        modlevel = []
        def setup_module(module):
            assert not modlevel
            module.modlevel.append(42)

        def teardown_module(module):
            modlevel.pop()

        def setup_function(function):
            function.answer = 17

        def teardown_function(function):
            del function.answer

        def test_modlevel():
            assert modlevel[0] == 42
            assert test_modlevel.answer == 17

        class TestFromClass: 
            def test_module(self):
                assert modlevel[0] == 42
                assert not hasattr(test_modlevel, 'answer') 
    """)
    rep = reprec.matchreport("test_modlevel") 
    assert rep.passed 
    rep = reprec.matchreport("test_module") 
    assert rep.passed 

def test_class_setup(testdir):
    reprec = testdir.inline_runsource("""
        class TestSimpleClassSetup:
            clslevel = []
            def setup_class(cls):
                cls.clslevel.append(23)

            def teardown_class(cls):
                cls.clslevel.pop()

            def test_classlevel(self):
                assert self.clslevel[0] == 23

        class TestInheritedClassSetupStillWorks(TestSimpleClassSetup):
            def test_classlevel_anothertime(self):
                assert self.clslevel == [23]

        def test_cleanup():
            assert not TestSimpleClassSetup.clslevel 
            assert not TestInheritedClassSetupStillWorks.clslevel
    """)
    reprec.assertoutcome(passed=1+2+1)


def test_method_setup(testdir):
    reprec = testdir.inline_runsource("""
        class TestSetupMethod:
            def setup_method(self, meth):
                self.methsetup = meth 
            def teardown_method(self, meth):
                del self.methsetup 

            def test_some(self):
                assert self.methsetup == self.test_some 

            def test_other(self):
                assert self.methsetup == self.test_other
    """)
    reprec.assertoutcome(passed=2)
       
def test_method_generator_setup(testdir):
    reprec = testdir.inline_runsource("""
        class TestSetupTeardownOnInstance: 
            def setup_class(cls):
                cls.classsetup = True 

            def setup_method(self, method):
                self.methsetup = method 

            def test_generate(self):
                assert self.classsetup 
                assert self.methsetup == self.test_generate 
                yield self.generated, 5
                yield self.generated, 2

            def generated(self, value):
                assert self.classsetup 
                assert self.methsetup == self.test_generate 
                assert value == 5
    """)
    reprec.assertoutcome(passed=1, failed=1)

def test_func_generator_setup(testdir):
    reprec = testdir.inline_runsource(""" 
        import sys

        def setup_module(mod):
            print "setup_module"
            mod.x = []
        
        def setup_function(fun):
            print "setup_function"
            x.append(1)

        def teardown_function(fun):
            print "teardown_function" 
            x.pop()
        
        def test_one():
            assert x == [1]
            def check():
                print "check" 
                print >>sys.stderr, "e" 
                assert x == [1]
            yield check 
            assert x == [1]
    """)
    rep = reprec.matchreport("test_one", names="pytest_runtest_logreport") 
    assert rep.passed 
        
def test_method_setup_uses_fresh_instances(testdir):
    reprec = testdir.inline_runsource("""
        class TestSelfState1: 
            memory = []
            def test_hello(self):
                self.memory.append(self)

            def test_afterhello(self):
                assert self != self.memory[0]
    """)
    reprec.assertoutcome(passed=2, failed=0)

