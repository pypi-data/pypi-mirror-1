import py
import sys


def setup_module(mod):
    mod.binpath = py._impldir.dirpath('bin')
    if not mod.binpath.check():
        py.test.skip("bin-source scripts not installed")
    mod.binwinpath = binpath.join("win32")
    mod.tmpdir = py.test.ensuretemp(__name__)
    mod.iswin32 = sys.platform == "win32"

def checkmain(name):
    main = getattr(py.cmdline, name)
    assert py.builtin.callable(main)
    assert name[:2] == "py"
    scriptname = "py." + name[2:]
    assert binpath.join(scriptname).check()
    assert binwinpath.join(scriptname + ".cmd").check()

def checkprocess(script):
    assert script.check()
    old = tmpdir.ensure(script.basename, dir=1).chdir()
    try:
        if iswin32:
            cmd = script.basename
        else:
            cmd = "%s" %(script, )
            # XXX distributed testing's rsync does not support
            # syncing executable bits 
            script.chmod(int("777", 8))

        if script.basename.startswith("py.lookup") or \
           script.basename.startswith("py.which"):
            cmd += " sys"
        py.builtin.print_("executing", script)
        try:
            old = script.dirpath().chdir()
            try:
                py.process.cmdexec(cmd)
            finally:
                old.chdir()
        except py.process.cmdexec.Error:
            e = sys.exc_info()[1]
            if cmd.find("py.rest") != -1 and \
               e.out.find("module named") != -1:
                return
            raise
                
    finally:
        old.chdir()

def test_cmdline_namespace():
    for name in dir(py.cmdline):
        if name[0] != "_":
            yield checkmain, name
       
def test_script_invocation():
    if iswin32:
        scripts = binwinpath.listdir("py.*")
    else:
        scripts = binpath.listdir("py.*")
    scripts = [x for x in scripts 
                if not x.basename.startswith("py.svnwcrevert")]
    for script in scripts:
        yield checkprocess, script 
