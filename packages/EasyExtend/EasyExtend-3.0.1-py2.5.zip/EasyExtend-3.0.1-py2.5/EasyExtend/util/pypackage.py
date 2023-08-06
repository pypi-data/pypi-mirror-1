import sys
from path import path
import test
import os
import imp

suffixes = ("py","pyc", "pyo")

_lib = imp.find_module("os", [path(os.__file__).dirname()])

class package(object):
    def __init__(self, name, package_descr, maybe_builtin = False):
        self._maybe_builtin = maybe_builtin
        self.name = name
        self.importer = imp
        package = self.importer.load_module(name, *package_descr)
        self.__dict__.update(package.__dict__)
        self.__path__ = path(package_descr[1]).dirname()


    def __getattr__(self, name):
        try:
            module_descr = self.importer.find_module(name, [self.__path__])
            if module_descr == self.importer:
                return self.importer.load_module(name)
            elif module_descr is None:
                module_descr = imp.find_module(name, [self.__path__])
        except ImportError:
            cls, msg, tb = sys.exc_info()
            if self._maybe_builtin:
                module = __import__(name)
                if hasattr(module, "__file__"):
                    raise cls, msg, tb
                return module
            raise cls, msg, tb

        if module_descr[0] is not None:
            mod_name = path(module_descr[1]).basename().split(".")[0]
            return imp.load_module(mod_name,*module_descr)
        else:
            __path__ = path(module_descr[1])
            if path(__path__).isdir():
                package_init = path(__path__).joinpath("__init__.py")
                if package_init.isfile():
                    return package(name, self.importer.find_module("__init__",[path(__path__)]))
            raise ImportError, "no module or package name '%s'"%name

    def __repr__(self):
        print self.__path__
        return "<%s package from '%s'>"%(self.name, str(self.__path__))

stdlib  = package("stdlib",_lib, maybe_builtin = True)
stdtest = stdlib.test

def from_os_path(pth):
    '''
    Converts os path information of a Python module into importable Python path fragments.

    Example:
        "C:\Python24\lib\site-packages\EasyExtend\langlets\Blub\langlet.py"

                        ====>

        ("EasyExtend.langlets.Blub","langlet")

    The function yields an exception when the start section cannot be found in sys.path
    '''
    import sys
    sys_path = sys.path
    path_fragments = pth.split(os.sep)
    mod = path_fragments[-1].split(".")
    n = len(path_fragments)
    mod_path = None
    for i in range(n):
        if os.sep.join(path_fragments[0:i+1]) in sys_path:
            mod_path = ".".join(path_fragments[i+1:-1])
    if not mod_path:
        raise ValueError("Pythonpath must be start-section")
    return mod_path,mod[0]


if __name__ == '__main__':
    print stdtest.test_random


