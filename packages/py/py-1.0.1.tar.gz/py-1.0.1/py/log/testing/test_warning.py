import py
mypath = py.magic.autopath()

def test_forwarding_to_warnings_module():
    py.test.deprecated_call(py.log._apiwarn, "1.3", "..")

def test_apiwarn_functional():
    capture = py.io.StdCapture()
    py.log._apiwarn("x.y.z", "something")
    out, err = capture.reset()
    print "out", out
    print "err", err
    assert err.find("x.y.z") != -1
    lno = test_apiwarn_functional.func_code.co_firstlineno + 2
    exp = "%s:%s" % (mypath, lno)
    assert err.find(exp) != -1

def test_stacklevel():
    def f():
        py.log._apiwarn("x", "some", stacklevel=2)
    # 3
    # 4
    capture = py.io.StdCapture()
    f()
    out, err = capture.reset()
    lno = test_stacklevel.func_code.co_firstlineno + 6
    warning = str(err)
    assert warning.find(":%s" % lno) != -1

def test_function():
    capture = py.io.StdCapture()
    py.log._apiwarn("x.y.z", "something", function=test_function)
    out, err = capture.reset()
    print "out", out
    print "err", err
    assert err.find("x.y.z") != -1
    lno = test_function.func_code.co_firstlineno 
    exp = "%s:%s" % (mypath, lno)
    assert err.find(exp) != -1

