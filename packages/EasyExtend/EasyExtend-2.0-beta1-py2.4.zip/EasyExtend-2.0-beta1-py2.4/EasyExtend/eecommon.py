# URL:     http://www.fiber-space.de
# Author:  Kay Schluehr <easyextend@fiber-space.de>
# Date:    10 May 2006

'''
Defines functions and classes that are commonly used by all fibers.
'''

import sys
import os
import util.py

def publish_as_builtin(fiber):
    '''
    @param fiber: used fiber.
    '''
    import __builtin__
    if hasattr(fiber,"__publish__"):
        for name in fiber.__publish__:
            __builtin__.__dict__[name] = fiber.__dict__[name]

def printnode(node):
    import eetransformer
    csttools.pprint(node, fs = eetransformer.fs)


class EEShow(object):

    def maybe_show_token(self, source, filename = None):
        """
        Used to show token-stream created by tokenizer. Call depends on show_token option -t.
        @param source_or_file: source or file to be tokenized.
        """
        if self.options.get("show_token"):
            class Report:
                Line = " %-6s|"
                Columns = " %-8s|"
                TokenClass = " %-12s|"
                ClassId = " %-11s|"
                TokenValue = " %-12s|"
                TokenId = " %-12s|"
                TokenIdName = " %-14s|"

                def __init__(self):
                    self.items = {"Line":" ",
                                  "Columns":" ",
                                  "TokenClass": " ",
                                  "ClassId":" ",
                                  "TokenValue":" ",
                                  "TokenId":" ",
                                  "TokenIdName":" "}

                def insert(self, name, value):
                    self.items[name] = value

                def write(self):
                    print "".join([Report.Line%self.items["Line"],
                            Report.Columns%self.items["Columns"],
                            Report.TokenValue%self.items["TokenValue"],
                            Report.TokenIdName%self.items["TokenIdName"],
                            Report.TokenId%self.items["TokenId"],
                            Report.TokenClass%self.items["TokenClass"],
                            Report.ClassId%self.items["ClassId"]])

            from eetokenizer import StdTokenizer
            import cst2source

            if filename:
                source = file(filename).read()
            deb_tokenizer   = StdTokenizer(self.fiber.token)
            deb_tokenizer.tokenize_input(cst2source.SourceCode(source).readline)
            print "[token>"
            print "----------------------------------------------------------------------------------------."
            print " Line  | Columns | Token Value | Token Name    | Token Id    | Token class | Class Id   |"
            print "-------+---------+-------------+---------------+-------------+-------------+------------+"

            for item in list(deb_tokenizer.tokenGenerator):
                r = Report()
                r.insert("ClassId",str(item[0])+" -- "+str(item[0]%512))
                token_class = None
                try:
                    token_class = self.fiber.token.tok_name[item[0]]
                    r.insert("TokenClass",self.fiber.token.tok_name[item[0]])
                except KeyError:
                    pass
                try:
                    tid = self.fiber.token.TOKEN_MAP.get(item[1])
                    if not tid:
                        if token_class:
                            tid = self.fiber.token.TOKEN_MAP.get(token_class)
                    if tid:
                        r.insert("TokenId", str(tid)+" -- "+str(tid%512))
                        r.insert("TokenIdName", self.fiber.token.tok_name[tid])
                except KeyError:
                    pass

                if item[1] == "\n":
                    r.insert("TokenValue","\\n")
                elif item[1] == "\t":
                    r.insert("TokenValue","\\t")
                elif item[1] == "\r":
                    r.insert("TokenValue","\\r")
                else:
                    r.insert("TokenValue",r"'%s'"%item[1])
                r.insert("Line",item[2][0])
                r.insert("Columns",str(item[2][1])+"-"+str(item[3][1]))
                r.write()
            print "----------------------------------------------------------------------------------------'"
            print "<token]"
            print

    def maybe_show_cst_before(self, cst):
        """
        Used to show CST created by the parser *before* transformation. Call depends on show_cst_before option -b.
        @param cst: cst to be printed.
        """
        if self.options.get("show_cst_before"):
            marked = []
            marked_nodes = self.options.get("show_marked_node")
            if marked_nodes:
                marked = marked_nodes.split(",")
            print "[cst-before>"
            self.fiber.pprint(cst, mark = marked, stop = False, short_form = True)
            print "<cst-before]"

    def maybe_show_cst_after(self, cst):
        """
        Used to show CST created by the parser *after* transformation. Call depends on show_cst_after option -a.
        @param cst: cst to be printed.
        """
        if self.options.get("show_cst_after"):
            marked = []
            marked_nodes = self.options.get("show_marked_node")
            if marked_nodes:
                marked = marked_nodes.split(",")
            print "[cst-after>"
            self.fiber.pprint(cst, mark = marked+["> MAX_PY_SYMBOL"], stop = False)
            print "<cst-after]"


    def maybe_show_python(self, cst):
        """
        Used to show Python source code generated transformed cst. Call depends on show_token option -p.
        @param cst: cst to be unparsed.
        """
        if self.options.get("show_python"):
            print "[python-source>"
            if isinstance(cst, basestring):
                print cst
            else:
                print self.fiber.unparse(cst)
            print "<python-source]"

def new_fiber(name, prompt = ">>> ", loc = ""):
    import fibers.transit.fiber as transit
    init_fiber(transit)
    cmd = transit.TransitCommand_newfiber(name, prompt = prompt, loc = loc)
    cmd.execute()

def run(fiber_name, **options):
    '''
    Executes fiber specific console.

    @param: fiber_name. fiber will be looked up in directory EasyExtend.fibers
    '''
    exec "from EasyExtend.fibers.%s import fiber as running_fiber"%fiber_name
    console = create_console(fiber_name, running_fiber, **options)
    console.interact()

def _check_fiber(fiber):
    if not hasattr(fiber, "FiberTransformer"):
        raise AttributeError, "FiberTransformer missing in fiber"
    if not hasattr(fiber, "symbol"):
        raise AttributeError, "symbol missing in fiber"
    if not hasattr(fiber, "__publish__"):
        raise AttributeError, "__publish__ missing in fiber"

def create_console(console_name, fiber):
    '''
    Creates interactive console object.
    @param console_name: name of the new console object.
    @param fiber: fiber module.
    '''
    import eeconsole
    import eecompiler
    import eeimporter
    init_fiber(fiber)
    global __dev__
    __dev__ = fiber.options.get("dev")
    eec = eecompiler.EECompiler(fiber)
    if hasattr(fiber, "FiberImporter"):
        importer = fiber.FiberImporter(eec)
    else:
        importer = eeimporter.Importer(eec)
    fiber.importer = importer
    importer.register_importer()
    interp   = eeconsole.EEConsole(fiber, name = console_name)
    return interp

def init_fiber(fiber):
    if hasattr(fiber, "is_initialized"):
        return
    import fs
    _check_fiber(fiber)
    publish_as_builtin(fiber)
    fs.create_new_fiber_offset(fiber)
    fiber.is_initialized = True

def import_and_init_fiber(fiber_name):
    fiber = __import__("EasyExtend.fibers."+fiber_name+".fiber", globals(), locals(), ["EasyExtend"])
    init_fiber(fiber)
    return fiber

def run_module(py_module, fiber):
    '''
    @param py_module: python module name ( may include extension ).
    @param fiber: fiber module.
    '''
    import eecompiler
    import eeimporter
    init_fiber(fiber)
    global __dev__
    __dev__ = fiber.options.get("dev")
    eec = eecompiler.EECompiler(fiber)
    if hasattr(fiber, "FiberImporter"):
        importer = fiber.FiberImporter(eec)
    else:
        importer = eeimporter.Importer(eec)
    fiber.importer = importer
    importer.register_importer()
    import imp
    import os
    _mod   = py_module.split(".")[0]
    _mod   = _mod.replace(os.sep,".")
    __import__(_mod)
    Module = sys.modules[_mod]
    if hasattr(Module, "__like_main__"):
        Module.__like_main__()


def getoptions():
    from optparse import OptionParser
    opt = OptionParser()
    # debug options
    opt.add_option("-b","--show_cst_before" ,dest="show_cst_before" ,help="show CST before transformation", action="store_true" )
    opt.add_option("-a","--show_cst_after" ,dest="show_cst_after" ,help="show CST after transformation",action="store_true")
    opt.add_option("-m","--show_marked_node" ,dest="show_marked_node" ,help="mark one or more different kind of nodes in CST",action="store", type = "string")
    opt.add_option("-t","--show_token",dest="show_token", help="show token stream of tokenized expression", action="store_true" )
    opt.add_option("-p","--show_python",dest="show_python", help="show translated Python code", action="store_true" )
    opt.add_option("--dev",dest="dev", help="development specific settings and logging code", action="store_true" )
    opt.add_option("--re-compile",dest="re_compile", help="re compilation even if *.pyc is newer than source", action="store_true" )
    opt.add_option("--parse-only",dest="parse_only", help="terminate after parsing file", action="store_true" )
    return opt



