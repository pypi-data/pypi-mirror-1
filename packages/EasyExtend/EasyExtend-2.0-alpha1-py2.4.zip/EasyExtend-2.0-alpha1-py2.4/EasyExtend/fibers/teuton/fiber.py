# minimal fiber that provides EE framework interface
from conf import*
import EasyExtend   # EasyExtend package
import PyGrammar    # contains fiber specific DFA tables used by the parser
from EasyExtend.csttools import*
import __builtin__
from EasyExtend.eetransformer import Transformer, transform

from teuton_def import*
import new
import sys
import types

def replaced_by_teuton():
    d = {}
    def wrapper(func):
        def f(*args, **kwd):
            return func(*args, **kwd)
        return f

    t_builtin_function, t_instancemethod = type(range), type(input)
    for key,val in teuton_std_lib.items():
        if key == val:
            continue
        try:
            F = __builtin__.__dict__[val]
            if isinstance(F,(types.FunctionType)):
                d[key] = new.function(F.func_code,{},key)
            elif isinstance(F, (t_builtin_function, t_instancemethod)):
                f = wrapper(F)
                f.__name__ = key
                d[key] = f
            elif hasattr(F, "__name__"):
                try:
                    F.__name__ = key
                    d[key] = F
                except TypeError:
                    pass
        except KeyError:
            pass
        except AttributeError:
            raise AttributeError( (key,val) )
    for key,val in d.items():
        __builtin__.__dict__[key] = val


__publish__ = ["Wahr", "Falsch", "Nichts"]

teuton_kw = {
    "loesche":"del",
    "drucke":"print",
    "weiter":"continue",
    "zurueck":"return",
    "erledige":"exec",
    "ergibt":"yield",
    "importiere":"import",
    "behandle":"raise",
    "von":"from",
    "behaupte":"assert",
    "wenn":"if",
    "wennsonst":"elif",
    "versuche":"try",
    "ausser":"except",
    "schliesslich":"finally",
    "sonst":"else",
    "solange":"while",
    "fuer":"for",
    "ausser":"except",
    "klasse":"class",
    "and":"und",
    "or":"oder",
    "nicht":"not",
    "im":"in"
}


class File:
    def __init__(self, f):
        self.f = f
    def __getattr__(self, name):
        return getattr(self.f, name)

    def write(self, s):
        s = s.replace("True","Wahr")
        return self.f.write(s)




class FiberTransformer(Transformer):
    '''
    Defines fiber specific transformations
    '''
    @transform
    def stmt(self, node):
        for name in find_all(node, token.NAME):
            py_name = teuton_kw.get(name[1])
            if py_name:
                name[1] = py_name

if __name__ == '__main__':
    import fiber
    replaced_by_teuton()
    sys.stdout = File(sys.stdout)
    (options, args) = opt.parse_args()
    fiber.options   = options.__dict__
    if args:
        py_module = args[-1]
        EasyExtend.run_module(py_module, fiber)
    else:
        console = EasyExtend.create_console("Teuton", fiber)
        console.interact()

