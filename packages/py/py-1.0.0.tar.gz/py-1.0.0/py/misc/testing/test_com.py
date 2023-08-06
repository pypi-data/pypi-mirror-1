
import py
import os
from py._com import Registry, MultiCall
from py._com import Hooks

pytest_plugins = "xfail"

class TestMultiCall:
    def test_uses_copy_of_methods(self):
        l = [lambda: 42]
        mc = MultiCall(l)
        l[:] = []
        res = mc.execute()
        return res == 42

    def test_call_passing(self):
        class P1:
            def m(self, __call__, x):
                assert __call__.currentmethod == self.m 
                assert len(__call__.results) == 1
                assert not __call__.methods
                return 17

        class P2:
            def m(self, __call__, x):
                assert __call__.currentmethod == self.m 
                assert __call__.args
                assert __call__.results == []
                assert __call__.methods
                return 23 
               
        p1 = P1() 
        p2 = P2() 
        multicall = MultiCall([p1.m, p2.m], 23)
        reslist = multicall.execute()
        assert len(reslist) == 2
        # ensure reversed order 
        assert reslist == [23, 17]

    def test_optionalcallarg(self):
        class P1:
            def m(self, x):
                return x
        call = MultiCall([P1().m], 23)
        assert call.execute() == [23]
        assert call.execute(firstresult=True) == 23
 
    def test_call_subexecute(self):
        def m(__call__):
            subresult = __call__.execute(firstresult=True)
            return subresult + 1

        def n():
            return 1

        call = MultiCall([n, m])
        res = call.execute(firstresult=True)
        assert res == 2

    def test_call_exclude_other_results(self):
        def m(__call__):
            __call__.exclude_other_results()
            return 10

        def n():
            return 1

        call = MultiCall([n, n, m, n])
        res = call.execute()
        assert res == [10]
        # doesn't really make sense for firstresult-mode - because
        # we might not have had a chance to run at all. 
        #res = call.execute(firstresult=True)
        #assert res == 10

    def test_call_none_is_no_result(self):
        def m1():
            return 1
        def m2():
            return None
        mc = MultiCall([m1, m2])
        res = mc.execute(firstresult=True)
        assert res == 1

class TestRegistry:
    def test_MultiCall(self):
        plugins = Registry()
        assert hasattr(plugins, "MultiCall")

    def test_register(self):
        registry = Registry()
        class MyPlugin:
            pass
        my = MyPlugin()
        registry.register(my)
        assert list(registry) == [my]
        my2 = MyPlugin()
        registry.register(my2)
        assert list(registry) == [my, my2]

        assert registry.isregistered(my)
        assert registry.isregistered(my2)
        registry.unregister(my)
        assert not registry.isregistered(my)
        assert list(registry) == [my2]

    def test_listattr(self):
        plugins = Registry()
        class api1:
            x = 41
        class api2:
            x = 42
        class api3:
            x = 43
        plugins.register(api1())
        plugins.register(api2())
        plugins.register(api3())
        l = list(plugins.listattr('x'))
        assert l == [41, 42, 43]
        l = list(plugins.listattr('x', reverse=True))
        assert l == [43, 42, 41]

        class api4: 
            x = 44
        l = list(plugins.listattr('x', extra=(api4,)))
        assert l == range(41, 45)
        assert len(list(plugins)) == 3  # otherwise extra added

def test_api_and_defaults():
    assert isinstance(py._com.comregistry, Registry)

class TestHooks:
    def test_happypath(self):
        registry = Registry()
        class Api:
            def hello(self, arg):
                pass

        mcm = Hooks(hookspecs=Api, registry=registry)
        assert hasattr(mcm, 'hello')
        assert repr(mcm.hello).find("hello") != -1
        class Plugin:
            def hello(self, arg):
                return arg + 1
        registry.register(Plugin())
        l = mcm.hello(arg=3)
        assert l == [4]
        assert not hasattr(mcm, 'world')

    def test_needskeywordargs(self):
        registry = Registry()
        class Api:
            def hello(self, arg):
                pass
        mcm = Hooks(hookspecs=Api, registry=registry)
        excinfo = py.test.raises(TypeError, "mcm.hello(3)")
        assert str(excinfo.value).find("only keyword arguments") != -1
        assert str(excinfo.value).find("hello(self, arg)")

    def test_firstresult(self):
        registry = Registry()
        class Api:
            def hello(self, arg): pass
            hello.firstresult = True

        mcm = Hooks(hookspecs=Api, registry=registry)
        class Plugin:
            def hello(self, arg):
                return arg + 1
        registry.register(Plugin())
        res = mcm.hello(arg=3)
        assert res == 4

    def test_default_plugins(self):
        class Api: pass 
        mcm = Hooks(hookspecs=Api)
        assert mcm.registry == py._com.comregistry

    def test_hooks_extra_plugins(self):
        registry = Registry()
        class Api:
            def hello(self, arg):
                pass
        hook_hello = Hooks(hookspecs=Api, registry=registry).hello 
        class Plugin:
            def hello(self, arg):
                return arg + 1
        registry.register(Plugin())
        class Plugin2:
            def hello(self, arg):
                return arg + 2
        newhook = hook_hello.clone(extralookup=Plugin2())
        l = newhook(arg=3)
        assert l == [5, 4]
        l2 = hook_hello(arg=3)
        assert l2 == [4]
        
