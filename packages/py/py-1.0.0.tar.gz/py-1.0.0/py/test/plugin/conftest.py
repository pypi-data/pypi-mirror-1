import py

pytest_plugins = "pytester"

def pytest_collect_file(path, parent):
    if path.basename.startswith("pytest_") and path.ext == ".py":
        mod = parent.Module(path, parent=parent)
        return mod

# decorate testdir to contain plugin under test 
def pytest_funcarg__testdir(request):
    testdir = request.getfuncargvalue("testdir")
    #for obj in (request.cls, request.module):
    #    if hasattr(obj, 'testplugin'): 
    #        testdir.plugins.append(obj.testplugin)
    #        break
    #else:
    basename = request.module.__name__.split(".")[-1] 
    if basename.startswith("pytest_"):
        testdir.plugins.append(vars(request.module))
        testdir.plugins.append(basename) 
    else:
        pass # raise ValueError("need better support code")
    return testdir

