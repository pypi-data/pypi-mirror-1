import EasyExtend
from EasyExtend.util.minicommands import*
from EasyExtend.util.path import path

def collect(basedir):
    for f in basedir.walk():
        if f.isdir() and f.basename() in ( "reports", ):
            for g in f.files():
                gbase = g.basename()
                if g.ext == ".ees" and "_test" in gbase or "test_" in gbase:
                    yield f.dirname(), g


def run_tests(basedir = path(EasyExtend.__file__).dirname()):
    for f,g in list(collect(basedir)):
        d, p = f.splitpath()
        py_driver = d.joinpath(p, "run_"+p+".py")
        pth = g.splitext()[0]
        pycmd = PythonCmd()
        pycmd.prefix_args = [str(py_driver),"--rep", "+"+pth.basename().split(p+"_")[1]]
        pycmd()

        #print pycmd.prefix

if __name__ == '__main__':
    run_tests()




