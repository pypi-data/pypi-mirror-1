from conf import*       # fiber specific modules ( symbol, token ) and objects ( prompt, pprint, unparse ...)
import EasyExtend       # EasyExtend package
import PyGrammar        # contains fiber specific DFA tables used by the parser
from EasyExtend.csttools import*   # tools used to manipulate CSTs
from EasyExtend.eetransformer import Transformer, transform
from EasyExtend.eeimporter import Importer
from EasyExtend.eecompiler import EECompiler
import EasyExtend.eecommon as eecommon
import sys
import os
import EasyExtend.util.path as path
import re
import EasyExtend.fibers.coverage.monitor as monitor

measurement = monitor.measurement

class FiberImporter(Importer):
    '''
    Specialized Importer for coverage purposes. This is delicate because not every module shall be
    covered. The basic coverage relation associates a module
    test_bla.py with a module bla.py. If for example "coverage test_all.py" is executed each test_xxx.py
    module imported by test_all is covered as well as xxx modules.
    '''
    def __init__(self, eecompiler):
        super(FiberImporter, self).__init__(eecompiler)
        self.no_import.append("test_support.py")
        if self.options.get("pattern"):
            self._pattern = re.compile(self.options.get("pattern"))
        else:
            self._pattern = None
        self._pattern_default    = re.compile(r'(?P<test>test\_(?P<mod_name>\w+))')
        self._pattern_groups     = []
        self._default_groups     = []
        self._deactivate_default = self.options.get("deactivate_default")
        self._start_module = self.options.get("start_module")
        if self._start_module:
            self._start_module = self._start_module.split(".")[0]

    def accept_module(self, module_path):
        #TODO: what happens when a module m gets imported before an associated test_m
        #      module is imported? Notify this.
        import fiber
        module_name = (module_path.split(os.sep)[-1]).split(".")[0].lower()
        if unicode(module_name +".py") in self.no_import:
            return
        if not self._deactivate_default:
            m = self._pattern_default.match(module_name)
            if m:
                self._default_groups.append(m.group(2).lower())
                fiber.options["module"] = module_path
                return self
            elif module_name in self._default_groups:
                self._default_groups.remove(module_name)
                fiber.options["module"] = module_path
                return self
        # pattern from command line
        if self._pattern:
            m = self._pattern.match(module)
            if m:
                self._pattern_groups+=m.groups()
                return self
            elif module in self._pattern_groups:
                return self
        if module_name == self._start_module:
            #sys.stdout.write("DEBUG module: %s\n"%module_name)
            fiber.options["module"] = module_path
            return self

class FiberTransformer(Transformer):
    def __init__(self, fiber, **kwd):
        super(FiberTransformer, self).__init__(fiber, **kwd)
        self._module      = fiber.options.get("module")
        self._main_module = fiber.options.get("main_module")
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

    @transform
    def suite(self, node):
        # special case: no use of sensors in 'if __main__...' stmts of modules that are not __main__.
        if self.in_main_of_not_main:
            return
        _num = Number(len(monitor.Monitor().sensors))
        # compile a call 'measurement(_num)' into each suite
        _sensor_stmt = any_stmt(any_test(CST_CallFunc("measurement",[_num])))

        IDX = 0
        for i,item in enumerate(node[1:]):
            if item[0] == symbol.stmt:
                if find_node(item, symbol.flow_stmt, level=2):    # measurement shall be execed before
                    IDX = i                                       # return, break, continue
                    break
                IDX = i
        if IDX:
            suite_begin = node[1][-1]
            suite_end   = node[-1][-1]-1
            # print "DEBUG place [%d %d]"%(suite_begin,suite_end)
            monitor.Sensor(suite_begin, suite_end)
            node.insert(IDX+1,_sensor_stmt)


def cover(py_module, options):
    import fiber
    mod_path = path.path(os.getcwd()+os.sep+py_module)
    FiberTransformer.main_module = mod_path
    fiber.options["module"] = mod_path
    fiber.options["main_module"] = mod_path
    fiber.options["re_compile"] = True
    EasyExtend.run_module(py_module, fiber)
    mon = monitor.Monitor()
    if options.output:
        try:
            f = file(options.output,"w")
        except IOError:
            sys.stdout.write("ERROR: failed to open file %s. Use stdout instead",options.output)
            f = sys.stdout
    else:
        f = sys.stdout
    mon.show_report(out = f)


__publish__ = ["measurement","monitor"]

if __name__ == '__main__':
    import fiber
    (options, args) = opt.parse_args()
    fiber.options   = options.__dict__
    if args:
        py_module = args[-1]
        fiber.options["start_module"] = py_module
        cover(py_module, options)
    else:
        console = EasyExtend.create_console("Python -- with coverage facility", fiber)
        console.interact()

