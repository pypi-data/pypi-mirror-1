# URL:     http://www.fiber-space.de
# Author:  Kay Schluehr <easyextend@fiber-space.de>
# Date:    10 May 2006


import sys
import EasyExtend
import EasyExtend.util.path as path
import os
import imp

#
#  Import mechanism for library packages
#

class Importer(object):
    no_import = [u"PyGrammar.py",
                 u"fiber.py",
                 u"symbol.py",
                 u"token.py",
                 u"conf.py"]  # don't touch these modules with eecompiler

    def __init__(self, eecompiler):
        '''
        Adapted importer.
        @param eecompiler: eecompiler object - parametrized with fiber
        '''
        self._eecompiler = eecompiler
        self.options     = eecompiler.options
        self._fiberpath  = path.path(eecompiler.fiber.__file__).dirname()
        self._module     = None
        try:
            self.ext = eecompiler.fiber.ext
        except AttributeError:
            self.ext = "pyc"

    def register_importer(self):
        sys.path.append(str(self._fiberpath))
        sys.path_importer_cache.clear()
        sys.meta_path.append(self)


    def accept_module(self, module_path):
        '''
        Method used to determine if a fiber accepts module for fiber-specific import.
        @param module_path: a path object specifying the complete module path
        '''
        if module_path.isfile():
            if hasattr(self._eecompiler.fiber,"imports"):
                if "." in self._eecompiler.fiber.imports:
                    return self
            if module_path.startswith(self._fiberpath):
                if module_path.basename() not in self.no_import:
                    return self

    def find_module(self, import_path, __path__ = None):
        idx = import_path.rfind(".")  # maybe dotted package name ?
        #sys.stdout.write("DEBUG module_path: %s\n"%import_path)
        if idx>0:
            package, mod = import_path[:idx],import_path[idx+1:]
            pkg = sys.modules[package]
            __path__ = pkg.__path__
            import_path = mod
        self._module = path.path(imp.find_module(import_path, __path__)[1])
        self._import_path = import_path
        mod =  self.accept_module(self._module)
        return mod


    def load_module(self, fullname):
        #sys.stdout.write("DEBUG: load_module %s\n"%fullname)
        compiled_module_path = path.path.stripext(self._module)+"."+self.ext
        if EasyExtend.__dev__:
            self._eecompiler.eecompile_file( self._module, module = self._module)
        elif path.path(compiled_module_path).isfile() and path.path(self._module).isfile():
            if os.stat(compiled_module_path)[-2] < os.stat(self._module)[-2] or self.options["re_compile"]:
                self._eecompiler.eecompile_file( self._module, module = self._module)
        else:
            self._eecompiler.eecompile_file( self._module, module = self._module)
        f = open(compiled_module_path, "rb")
        return imp.load_compiled( fullname, compiled_module_path, f )


