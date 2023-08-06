from conf import*                  # langlet specific modules ( symbol, token ) and objects ( prompt, pprint, unparse ...)
from EasyExtend.csttools import*   # tools used to manipulate CSTs
from EasyExtend.eeimporter import Importer
from EasyExtend.eecompiler import EECompiler
import EasyExtend.eecommon as eecommon
import sys
import os
from EasyExtend.util.path import path
import re
import EasyExtend.langlets.coverage.monitor as monitor

measure_stmt = monitor.measure_stmt
measure_expr = monitor.measure_expr

def shuffle(ls1, ls2):
    res = []
    for i in range(len(ls1)):
        res.append(ls1[i])
        res.append(ls2[i])
    return res

# CLI of Ned Batchelders popular coverage.py tool (v2.78) - EE 3.1 will support this
# CLI and replace the old one
'''
coverage.py -x [-p] MODULE.py [ARG1 ARG2 ...]
    Execute module, passing the given command-line arguments, collecting
    coverage data. With the -p option, write to a temporary file containing
    the machine name and process ID.

coverage.py -e
    Erase collected coverage data.

coverage.py -c
    Collect data from multiple coverage files (as created by -p option above)
    and store it into a single file representing the union of the coverage.

coverage.py -r [-m] [-o dir1,dir2,...] FILE1 FILE2 ...
    Report on the statement coverage for the given files.  With the -m
    option, show line numbers of the statements that weren't executed.

coverage.py -a [-d dir] [-o dir1,dir2,...] FILE1 FILE2 ...
    Make annotated copies of the given files, marking statements that
    are executed with > and statements that are missed with !.  With
    the -d option, make the copies in that directory.  Without the -d
    option, make each copy in the same directory as the original.

-o dir,dir2,...
  Omit reporting or annotating files when their filename path starts with
  a directory listed in the omit list.
  e.g. python coverage.py -i -r -o c:\python23,lib\enthought\traits

Coverage data is saved in the file .coverage by default.  Set the
COVERAGE_FILE environment variable to save it somewhere else."""
'''

class LangletImporter(eeimporter.Importer):
    '''
    Specialized Importer for coverage purposes. This is delicate because not every module shall be
    covered. The basic coverage relation associates a module
    test_bla.py with a module bla.py. If for example "coverage test_all.py" is executed each test_xxx.py
    module imported by test_all is covered as well as xxx modules.
    '''
    def __init__(self, langlet):
        super(LangletImporter, self).__init__(langlet)
        sm = self.options.get("start_module")
        self._start_module       = sm.split(".")[0] if sm else None
        self._pattern_default    = re.compile(r'(?P<test>test\_(?P<mod_name>\w+))')
        self._default_groups     = []
        self._deactivate_default = self.options.get("deactivate_default")
        self.__class__.no_import.add("test_support.py")


    def accept_module(self, module_path):
        #TODO: what happens when a module m gets imported before an associated test_m
        #      module is imported? Notify this.
        module_name = (module_path.split(os.sep)[-1]).split(".")[0].lower()
        if unicode(module_name +".py") in self.no_import:
            return
        if not self._deactivate_default:
            m = self._pattern_default.match(module_name)
            if m:
                self._default_groups.append(m.group(2).lower())
                self.langlet.options["module"] = module_path
                return self
            elif module_name in self._default_groups:
                self._default_groups.remove(module_name)
                self.langlet.options["module"] = module_path
                return self
        if module_name == self._start_module:
            #sys.stdout.write("DEBUG module: %s\n"%module_name)
            self.langlet.options["module"] = module_path
            return self
        if self.langlet.options.get("main_module") == module_path:
            return self


class LangletTransformer(Transformer):
    def __init__(self, langlet, **kwd):
        super(LangletTransformer, self).__init__(langlet, **kwd)
        self._module      = langlet.options.get("module")
        self._main_module = langlet.options.get("main_module")
        # sys.stdout.write("DEBUG module: %s\n"%self._module)
        # sys.stdout.write("DEBUG main module: %s\n"%self._main_module)
        # used to be assign the 'if __main__ ...' part of the __main__ module
        self.in_main_of_not_main = False
        if self._module:
            mon = monitor.Monitor()
            mon.assign_sensors(self._module)

    @transform
    def if_stmt(self, node):
        if self._module != self._main_module:
            if self.is_main(node):
                self.in_main_of_not_main = True
        return node

    @transform
    @t_dbg("cv", cond = lambda node, **locals: locals.get("line",-1)>=0)
    def and_test(self, node, line = -1, idx = 0):
        if self.in_main_of_not_main or line == -1:
            return
        _not_tests = find_all(node, symbol.not_test, level = 1)
        for sub in _not_tests:
            if find_node(sub, symbol.test):
                self.run(sub, line = line, idx = idx)
            else:
                # find not_test nodes
                for item in find_all_gen(node, symbol.atom):
                    first_line = item[1][-1]
                    if isinstance(first_line, int):
                        break
                if first_line == line:
                    idx+=1
                else:
                    line = first_line
                    idx  = 1
                _num = Number(len(monitor.Monitor().expr_sensors))
                monitor.ExprSensor(first_line, idx)
                self.run(sub, line = line, idx = idx)
                cloned = clone_node(sub)
                node_replace(sub, any_node(CST_CallFunc("measure_expr",[cloned, _num]), symbol.not_test))


    #@t_dbg("si")
    @transform
    def or_test(self, node, line = -1, idx = 0):
        if self.in_main_of_not_main:
            return
        and_tests = find_all(node, symbol.and_test, level = 1)
        if len(and_tests)>1:
            for i, t in enumerate(and_tests):
                self.run(t, line = 0, idx = idx)
        else:
            self.run(and_tests[0], line = line, idx = idx)

    @transform
    #@t_dbg("si")
    def suite(self, node):
        # special case: no use of sensors in 'if __main__...' stmts of modules that are not __main__.
        if self.in_main_of_not_main:
            return
        _stmts = find_all(node, symbol.stmt, level = 1)
        _num = Number(len(monitor.Monitor().stmt_sensors))
        # compile a call 'measure_stmt(_num)' into each suite
        _sensor_stmt = any_stmt(any_test(CST_CallFunc("measure_stmt",[_num])))
        IDX = 0
        for i,item in enumerate(node[1:]):
            if item[0] == symbol.stmt:
                if find_node(item, symbol.flow_stmt, level=3):    # measure_stmt shall be execed before
                    IDX = i                                       # return, break, continue
                    break
                IDX = i
        if IDX:
            suite_begin = node[1][-1]
            suite_end   = node[-1][-1]-1
            # print "DEBUG place [%d %d]"%(suite_begin,suite_end)
            monitor.StmtSensor(suite_begin, suite_end)
            _small = find_node(node[i], symbol.small_stmt, level = 3)
            if _small and is_atomic(_small) and find_node(_small, token.STRING):
                node.insert(IDX+2,_sensor_stmt)
            else:
                node.insert(IDX+1,_sensor_stmt)


def run_module(py_module, langlet):
    mod_path = path(os.getcwd()).joinpath(py_module)
    sys.path.append(mod_path.dirname())
    LangletTransformer.main_module = mod_path
    langlet.options["module"]      = mod_path
    langlet.options["main_module"] = mod_path
    langlet.options["re_compile"]  = True
    # from eecommon.run_module
    eecommon.load_importer(langlet)
    _mod   = mod_path.splitext()[0].basename()
    __import__(_mod)
    Module = sys.modules[_mod]
    if hasattr(Module, "__like_main__"):
        Module.__like_main__()
    mon = monitor.Monitor()
    # end of embedding
    output = langlet.options.get("output")
    if output:
        try:
            f = file(output,"w")
        except IOError:
            sys.stdout.write("ERROR: failed to open file %s. Coverage langlet uses stdout instead!", output)
            f = sys.stdout
    else:
        f = sys.stdout
    mon.show_report(out = f)
    if langlet.options.get("erase"):
        for f in mod_path.dirname().walk():
            if f.ext == ".pycv":
                f.remove()


__publish__ = ["measure_stmt","measure_expr","monitor"]


