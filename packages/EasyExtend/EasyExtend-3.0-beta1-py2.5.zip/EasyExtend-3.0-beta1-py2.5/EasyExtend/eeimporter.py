# URL:     http://www.fiber-space.de
# Author:  Kay Schluehr <easyextend@fiber-space.de>
# Date:    10 May 2006

#
#  Import mechanism for library packages
#
#
#  Terminology:
#
#      A file with with specified source file extension is "langletsource".
#      A file with a source extension is "source".
#      A file with a compiled extension is "compiled".
#      A file is "accepted" when accept_module returns self.
#
#  Conventions:
#      Use the prefix 'mpth_' when a dotted module path A.B. .. .M is mentioned.
#      Use the prefix 'fpth_' when an operating system path A/B/../M.ext is mentioned.
#
#  Strategy:
#     Compilation:
#         let f be a module_path returned by find_module.
#
#         If f is source, compile f.
#         If f is compiled return f.
#
#     Search:
#         let f1,f2 be module paths and s1 = stat(f1)[-2], s2 = stat(f1)[-2].
#
#         if f1 is source and compile is enforced, return f1.
#         elif f1 is source and s2 < s1, return f1
#         else return f2
#


import sys
import EasyExtend.eecompiler as eecompiler
import EasyExtend.exotools as exotools
from EasyExtend.util.path import path
import os
import imp

import ihooks

class LangletHooks(ihooks.Hooks):
    def __init__(self, langlet):
        ihooks.Hooks.__init__(self)
        self.langlet = langlet
        self._search_suffixes()

    def _search_suffixes(self):
        if self.langlet.source_ext == '.py':
            self.suffixes = list(ihooks.Hooks.get_suffixes(self))
        else:
            self.suffixes = []

        for (ext, code, prio) in self.suffixes:
            if self.langlet.compiled_ext == ext:
                break
        else:
            self.suffixes.append((self.langlet.compiled_ext, 'rb', 2))

        for (ext, code, prio) in self.suffixes:
            if self.langlet.source_ext == ext:
                break
        else:
            self.suffixes.append((self.langlet.source_ext, 'U', 1))
        # self.suffixes.append(('.pyz', 'rb', 2))

    def get_suffixes(self):
        return self.suffixes


class EEModuleLoader(ihooks.ModuleLoader):

    def is_source(self, file):
        for info in self.hooks.get_suffixes():
            if file.endswith(info[0]):
                if info[-1] == 1:
                    return True
                else:
                    return False
        return False

    def find_module_in_dir(self, name, dir, allow_packages=1):
        if dir is None:
            return self.find_builtin_module(name)
        if allow_packages:
            fullname = self.hooks.path_join(dir, name)
            if self.hooks.path_isdir(fullname):
                stuff = self.find_module_in_dir("__init__", fullname, 0)
                if stuff:
                    f = stuff[0]
                    if f:
                        f.close()
                    return None, fullname, ('', '', ihooks.PKG_DIRECTORY)
        f = ()
        for info in self.hooks.get_suffixes():
            suff, mode, typ = info
            fullname = self.hooks.path_join(dir, name+suff)
            if self.hooks.path_isfile(fullname):
                if self.hooks.langlet.options.get("re_compile"):
                    if self.is_source(fullname):
                        f = (0, fullname, mode, info )
                        break
                dt = os.stat(fullname)[-2]
                if f:
                    if f[0] < dt:
                        f = (dt, fullname, mode, info )
                else:
                    f = (dt, fullname, mode, info )
        if f:
            try:
                fp = self.hooks.openfile(f[1], f[2])
                return fp, f[1], f[-1]
            except self.hooks.openfile_error:
                pass
        return None


class Importer(object):
    no_import = []

    def __init__(self, langlet):
        '''
        Adapted importer.
        @param eecompiler: eecompiler object - parametrized with langlet
        '''
        self.langlet      = langlet
        self.eec          = self.langlet_compiler()
        self.options      = langlet.options
        self.fpth_langlet = self.langlet_path()
        self.fpth_mod     = None
        self.loader       = self.module_loader()
        self.dbg          = langlet.options.get("debug_importer")

    def pre_filter(self, fpth_mod):
        if not path(fpth_mod).ext == u".py":
            return True
        if self.__class__.no_import:
            if not fpth_mod in self.__class__.no_import:
                return True
        else:
            _files = [f for f in path(__file__).dirname().files() if f.ext == u".py"]
            _files.append("lex_nfa.py")
            _files.append("parse_nfa.py")
            self.__class__.no_import = set(_files)
            return self.pre_filter(fpth_mod)


    def langlet_path(self):
        return path(self.langlet.__file__).dirname()

    def langlet_compiler(self):
        return eecompiler.EECompiler(self.langlet)

    def module_loader(self):
        return EEModuleLoader(hooks = LangletHooks(self.langlet))

    def is_langletmodule(self, fpth_m):
        return fpth_m.endswith(self.langlet.source_ext) or fpth_m.endswith(self.langlet.compiled_ext)

    def register_importer(self):
        pth = str(self.fpth_langlet)
        if pth not in sys.path:
            sys.path.append(pth)
        sys.path_importer_cache.clear()
        if self not in sys.meta_path:
            sys.meta_path.append(self)

    def accept_module(self, fpth_mod):
        '''
        Method used to determine if a langlet accepts module for langlet-specific import.
        @param module_path: a path object specifying the complete module path.
        '''
        if not self.is_langletmodule(fpth_mod):
            return
        if self.langlet.source_ext == '.py':
            return
        if self.dbg:
            sys.stdout.write("dbg-importer: accept_module:`%s`\n"%fpth_mod)
        return self

    def find_module(self, mpth_mod, mpth_pack = None):
        idx = mpth_mod.rfind(".")  # maybe dotted package name ?
        if self.dbg:
            sys.stdout.write("dbg-importer: find_module: input: `%s`\n"%mpth_mod)
        if idx>0:
            package, mpth_mod = mpth_mod[:idx], mpth_mod[idx+1:]
            mpth_pack = sys.modules[package].__path__

        moduledata  = self.loader.find_module(mpth_mod, mpth_pack)
        if not moduledata:
            raise ImportError("No module named %s"%mpth_mod)

        if self.dbg:
            sys.stdout.write("dbg-importer: find_module: moduledata: `%s`\n"%(moduledata[1:],))
        self.fpth_mod = path(moduledata[1])
        self.mpth_mod = mpth_mod
        # sys.stdout.write("DEBUG import_path: %s, module: %s\n"%(import_path, self._module))
        if self.pre_filter(self.fpth_mod):
            mod_obj = self.accept_module(self.fpth_mod)
            return mod_obj

    def load_module(self, fullname):
        mod = self.fpth_mod
        # sys.stdout.write("DEBUG load_module: %s\n"%mod)
        if self.loader.is_source(mod):
            if self.dbg:
                sys.stdout.write("dbg-importer: %s\n"%("-"*(len(mod)+30),))
                sys.stdout.write("dbg-importer: load_module: compile source: `%s`\n"%mod)
                sys.stdout.write("dbg-importer: %s\n"%("-"*(len(mod)+30),))
            self.eec.compile_file( mod )
            compiled_module_path = mod.stripext()+self.langlet.compiled_ext
        else:
            compiled_module_path = mod
        try:
            if self.langlet.exospace.wired:
                self.langlet.exospace.dump(fullname, compiled_module_path)
                exotools.move_to_archive(compiled_module_path)
                return self.load_zipped_module(fullname, compiled_module_path)
            else:
                if self.dbg:
                    sys.stdout.write("dbg-importer: load_module: load compiled: `%s`\n\n"%compiled_module_path)
                f = open(compiled_module_path, "rb")
                return imp.load_compiled( fullname, compiled_module_path, f )
        except AttributeError:
            if compiled_module_path.endswith("pyz"):
                return self.load_zipped_module(fullname, compiled_module_path)
            if self.dbg:
                sys.stdout.write("dbg-importer: load_module: load compiled: `%s`\n\n"%compiled_module_path)
            f = open(compiled_module_path, "rb")
            return imp.load_compiled( fullname, compiled_module_path, f )

    def load_zipped_module(self, fullname, compiled_module_path):
        # not used yet
        print "MODULE", compiled_module_path, fullname
        import zipimport
        zipped_module_path = path(compiled_module_path).stripext()+".pyz"
        print "ZIPPED", zipped_module_path
        importer = zipimport.zipimporter(zipped_module_path)
        mod = importer.load_module(fullname)
        return mod




