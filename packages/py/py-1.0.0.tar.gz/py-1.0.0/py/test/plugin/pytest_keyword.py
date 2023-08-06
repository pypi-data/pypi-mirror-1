"""
mark test functions with keywords that may hold values. 

Marking functions and setting rich attributes
----------------------------------------------------

By default, all filename parts and class/function names of a test
function are put into the set of keywords for a given test.  You can
specify additional kewords like this::

    @py.test.mark.webtest 
    def test_send_http():
        ... 

This will set an attribute 'webtest' on the given test function
and by default all such attributes signal keywords.  You can 
also set values in this attribute which you could read from
a hook in order to do something special with respect to
the test function::

    @py.test.mark.timeout(seconds=5)
    def test_receive():
        ...

This will set the "timeout" attribute with a Marker object 
that has a 'seconds' attribute. 

"""
import py

def pytest_namespace():
    return {'mark': Mark()}


class Mark(object):
    def __getattr__(self, name):
        if name[0] == "_":
            raise AttributeError(name)
        return MarkerDecorator(name)

class MarkerDecorator:
    """ decorator for setting function attributes. """
    def __init__(self, name):
        self.markname = name

    def __repr__(self):
        d = self.__dict__.copy()
        name = d.pop('markname')
        return "<MarkerDecorator %r %r>" %(name, d)

    def __call__(self, *args, **kwargs):
        if not args:
            if hasattr(self, 'kwargs'):
                raise TypeError("double mark-keywords?") 
            self.kwargs = kwargs.copy()
            return self 
        else:
            if not len(args) == 1 or not hasattr(args[0], 'func_dict'):
                raise TypeError("need exactly one function to decorate, "
                                "got %r" %(args,))
            func = args[0]
            mh = MarkHolder(getattr(self, 'kwargs', {}))
            setattr(func, self.markname, mh)
            return func

class MarkHolder:
    def __init__(self, kwargs):
        self.__dict__.update(kwargs)

def test_pytest_mark_api():
    mark = Mark()
    py.test.raises(TypeError, "mark(x=3)")

    def f(): pass
    mark.hello(f)
    assert f.hello

    mark.world(x=3, y=4)(f)
    assert f.world 
    assert f.world.x == 3
    assert f.world.y == 4

    py.test.raises(TypeError, "mark.some(x=3)(f=5)")

def test_mark_plugin(testdir):
    p = testdir.makepyfile("""
        import py
        pytest_plugins = "keyword" 
        @py.test.mark.hello
        def test_hello():
            assert hasattr(test_hello, 'hello')
    """)
    result = testdir.runpytest(p)
    assert result.stdout.fnmatch_lines(["*passed*"])
