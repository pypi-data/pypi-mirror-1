import EasyExtend                # EasyExtend package
from conf import*                # defines some fiber properties e.g. the console prompt, paths etc.
                                 # import this module first if it imports symbol, token and tokenize modules!
import PyGrammar                 # contains fiber specific DFA tables used by the parser
from EasyExtend.csttools import*
from EasyExtend.eetransformer import Transformer, transform
from EasyExtend.util.path import path
from EasyExtend.util.py import from_os_path
import os
import types
import sets


from EasyExtend.util.minicommands import PythonCmd

own_path    = path(EasyExtend.__file__).dirname().joinpath("fibers","transit")
fibers_path = path(EasyExtend.__file__).dirname().joinpath("fibers")

def get_all_fibers():
    fiber_dirs = fibers_path.dirs()
    fibers = []
    for d in fiber_dirs:
        f = d.joinpath("fiber.py")
        if f.isfile():
            fibers.append([str(d.basename()),d])
    return fibers



def transit_command(transit_cmd_name, *args, **parameters):
    import fiber
    name = "".join(transit_cmd_name.split("-"))
    try:
        cmd_cls = globals()["TransitCommand_"+name]
    except KeyError:
        raise ValueError("No command with name :%s available"%transit_cmd_name)
    TrCmd = cmd_cls(*args, **parameters)
    return TrCmd.execute()


class AbstractTransitCommand(object):
    options = {}
    def __init__(self, *args, **kwds):
        self.args = args
        self.make_opt(kwds)

    def execute(self):
        raise NotImplementedError

    def make_opt(self,kwds):
        keys = sets.Set(kwds.keys()+self.__class__.options.keys())
        for key in keys:
            if key in kwds:
                setattr(self, key, kwds[key])
            else:
                setattr(self, key, None)


class TransitCommand_FiberCall(AbstractTransitCommand):

    def execute(self):
        cmd = PythonCmd()
        fibers = get_all_fibers()
        for name, pth in fibers:
            if name == "gallery":
                cmd(pth.joinpath("fiber.py"),"-t")


class TransitCommand__help(AbstractTransitCommand):
    def execute(self):
        import fiber
        cmds = []
        for key, val in fiber.__dict__.items():
            if isinstance(val, (types.ClassType, type)):
                if issubclass(val, fiber.AbstractTransitCommand):
                    s = key.split("_")
                    if len(s)>1:
                        if val.__doc__:
                            doc = "".join([line.strip() for line in val.__doc__.split("\n")])
                            cmds.append((s[1],doc))
        cmds.sort()
        print
        for (cmd,doc) in cmds:
            print doc


class TransitCommand_newfiber(AbstractTransitCommand):
    options = {"prompt":"fiber prompt [default = '>>>']",
               "loc":"fiber directory [default = EasyExtend/fibers]"}

    def __init__(self, *args, **kwds):
        self.make_opt(kwds)
        try:
            self.name   = args[0]
        except IndexError:
            raise ValueError("Name of fiber not found. Please insert name as first argument.")
        if not self.loc:
            self.loc = fibers_path
        else:
            self.loc = path(self.loc)

    def execute(self):
        self.create_files()
        self.print_status()

    def create_files(self):
        if not self.name:
            raise ValueError, "Fiber needs a name"
        if self.name.startswith('"'):
           self.name = self.name[1:-1]
        _fiber_path = fibers_path.joinpath(self.name)
        _fiber_path.mkdir(0)
        _template_dir = own_path.joinpath("fiber_template")
        # insert fiber name
        fiber_py = open(_template_dir.joinpath("fiber.py")).readlines()
        for i,line in enumerate(fiber_py):
            if line.find("%FIBER_NAME%")>0:
                fiber_py[i] = line.replace("%FIBER_NAME%", '"'+self.name+'"')
                break
        f_fiber = open(_fiber_path.joinpath("fiber.py"),"w")
        f_fiber.write("".join(fiber_py))
        f_fiber.close()
        # insert prompt name
        conf_py = open(_template_dir.joinpath("conf.py")).readlines()
        for i,line in enumerate(conf_py):
            if line.find("%PROMPT%")>0:
                if self.prompt:
                    if self.prompt.startswith('"'):
                        conf_py[i] = line.replace("%PROMPT%", self.prompt)
                    else:
                        conf_py[i] = line.replace("%PROMPT%", '"'+self.prompt+'"')
                else:
                    conf_py[i] = line.replace("%PROMPT%", '">>> "')

            elif line.find("%FIBER_NAME%")>0:
                conf_py[i] = line.replace("%FIBER_NAME%", '"'+self.name+'"')
                break

        f_conf = open(_fiber_path.joinpath("conf.py"),"w")
        f_conf.write("".join(conf_py))
        f_conf.close()
        Grammar = _template_dir.joinpath("Grammar")
        Grammar.copy2(_fiber_path.joinpath("Grammar"))
        PyGrammar = _template_dir.joinpath("PyGrammar.py")
        PyGrammar.copy2(_fiber_path.joinpath("PyGrammar.py"))
        __init__ = _template_dir.joinpath("__init__.py")
        __init__.copy2(_fiber_path.joinpath("__init__.py"))
        fibermod = _template_dir.joinpath("fibermod")
        fibermod.copytree(_fiber_path.joinpath("fibermod"))
        fibercon = _template_dir.joinpath("fibercon")
        fibercon.copytree(_fiber_path.joinpath("fibercon"))

        # initialize fiber
        pth, module = from_os_path(f_fiber.name)
        f_import_args = str(pth+"."+module), None, None, ["FiberTransformer"]
        fiber_mod = __import__(*f_import_args)
        EasyExtend.eecommon.init_fiber(fiber_mod)
        path(f_conf.name+"c").remove()  # remove compiled conf file ( with FIBER_OFFSET = 0 )


    def print_status(self):
        print "New fiber '%s' created:"%self.name
        print
        f_1, f_2 = self.loc.splitall()[-2:]
        s = "... [%s]+-[%s]"%(f_1,f_2)
        print s
        white = " "*(s.find("+-")+3)
        print white+"+- [%s]"%self.name
        print white+"    +- __init__.py"
        print white+"    +- conf.py"
        print white+"    +- fiber.py"
        print white+"    +- PyGrammar.py"
        print white+"    +- Grammar"
        print white+"    +- [fiber_mod]"
        print white+"        +- __init__.py"
        print white+"        +- symbol.py"
        print white+"        +- token.py"


class FiberTransformer(Transformer):
    '''
    Defines fiber specific transformations
    '''
    @transform
    def FAT_TOKEN(self, node):
        return CST_Sub(*node[1].split("-"))

    @transform
    def STRING(self, node):
        if node[1] and node[1][0] == 'p':
            pth = "r"+node[1][1:]
            return atomize(CST_CallFunc("path",[pth]))
        return node

    @transform
    def transit_command(self, node):
        '''
        transit_command: ':' ( '?' | tr_variable | NAME | FAT_TOKEN ) [tr_argument (',' tr_argument)*]
                             [ unix_style_options | ('with' python_style_options)]
        '''
        _cmd_name = node[2]
        if _cmd_name[0] == token.QUESTIONMARK:
            return any_node(CST_CallFunc("transit_command",["'_help'"]), symbol.small_stmt)
        if _cmd_name[0] in (token.FAT_TOKEN, token.NAME):
            cmd_name = String(_cmd_name[1])
        else:
            cmd_name = _cmd_name[2]
        kwd  = CST_Dict()
        args = CST_Tuple(*[self.tr_argument(arg) for arg in find_all(node, symbol.tr_argument, level = 1)])
        _uopts = find_node(node, symbol.unix_style_options)
        if _uopts:
            kwd = self.unix_style_options(_uopts)
        else:
            _popts = find_node(node, symbol.python_style_options)
            if _popts:
                kwd = self.python_style_options(_popts)
        return any_node(CST_CallFunc("transit_command",[cmd_name],star_args=args,dstar_args = kwd), symbol.small_stmt)

    def tr_argument(self, node):
        "'(' testlist ')' | STRING | NUMBER | NAME ('.' NAME)* | tr_variable"
        n = node[1]
        if n[0] in (token.LPAR, token.NUMBER):
            return any_test(node[1])
        elif n[0] == token.STRING:
            return any_test(self.STRING(n))
        elif n[0] == symbol.tr_variable:
            return any_test(find_node(node, token.NAME))
        return any_test(String(unparse(node).strip()))


    def python_style_options(self, node):
        "python_style_options: NAME ['=' ( expr | tr_variable )] (',' NAME ['=' (expr | tr_variable)])* | '**' NAME"
        if find_node(node, token.DOUBLESTAR):
            return node[2]
        i = 1
        options = {}
        while i<len(node):
            if node[i][0] == token.COMMA:
                i+=1
            name = "'"+node[i][1]+"'"
            i+=1
            if node[i][0] == token.EQUAL:
                i+=1
                if node[i][0] == symbol.expr:
                    options[name] = String(unparse(node[i]).strip())
                else:
                    options[name] = node[i][2]
            else:
                options[name] = Name("True")
            i+=1
        return CST_Dict(**options)

    def unix_style_options(self, node):
        "unix_style_options: ('-' NAME [tr_argument] )+"
        args = []
        options = {}
        i = 1
        while i<len(node):
            item = node[i]
            if item[0] == token.MINUS:
                i+=1
                name = "'"+node[i][1]+"'"
                options[name] = Name("True")
                i+=1
                if i<len(node) and node[i][0] == symbol.tr_argument:
                    options[name] = self.tr_argument(node[i])
                    i+=1
                else:
                    options[name] = Name("True")
        return CST_Dict(**options)


__publish__ = ["path","transit_command"]

def open_session(**options):
    import sys
    import fiber              # import this fiber
    from TransitConsole import TransitConsole
    import EasyExtend.eecompiler as eecompiler
    import EasyExtend.eeimporter as eeimporter
    import EasyExtend.eecommon as eecommon
    eecommon.publish_as_builtin(fiber)
    eec = eecompiler.EECompiler(fiber)
    importer = eeimporter.Importer(eec)
    importer.register_importer()
    console = TransitConsole(fiber, "TransitConsole", **options)
    return console

if __name__ == '__main__':
    (options,args) = opt.parse_args()
    import fiber
    EasyExtend.init_fiber(fiber)
    session = open_session(**options.__dict__)
    session.interact()


