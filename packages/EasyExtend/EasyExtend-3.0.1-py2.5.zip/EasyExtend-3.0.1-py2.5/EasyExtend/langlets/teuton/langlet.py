# -*- coding: UTF-8 -*-
from conf import*                  # langlet specific modules ( symbol, token ) and objects ( prompt, pprint, unparse ...)
from EasyExtend.csttools import*   # tools used to manipulate CSTs
from teuton_def import*
import new
import sys
import types


def _wrapper(func):
    def f(*args, **kwd):
        return func(*args, **kwd)
    return f

def replaced_by_teuton():
    t_builtin_function, t_instancemethod = type(range), type(input)
    import __builtin__
    for key, val in teuton_std_lib.items():
        item = __builtin__.__dict__[val]
        try:
            item = __builtin__.__dict__[val]
        except KeyError:
            # builtin not available in this version of Python
            continue
        if isinstance(item, (types.ClassType, type)):
            try:
                if not issubclass(item, Exception):
                    __builtin__.__dict__[key] = type(key, (item,),{})
                else:
                    __builtin__.__dict__[key] = item
            except TypeError:
                __builtin__.__dict__[key] = item

        elif isinstance(item,(types.FunctionType)):
            __builtin__.__dict__[key] = new.function(item.func_code,{},key)
        elif isinstance(item, (t_builtin_function, t_instancemethod)):
            f = _wrapper(item)
            f.__name__ = key
            __builtin__.__dict__[key] = f
        else:
            __builtin__.__dict__[key] = item


__publish__ = ["Wahr", "Falsch", "Nichts"]

teuton_kw = {
    "ausfuehren":"exec",
    "ausf\x81hren":"exec",
    "loesche":"del",
    "l\x94sche":"del",
    "drucke":"print",
    "weiter":"continue",
    "zurueck":"return",
    "zur\x81ck":"return",
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
    "f\x81r":"for",
    "f\xfcr":"for",
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

def replace_umlaut(s):
    for u,r in (('\x84', 'ae'), ('\x8e', 'Ae'), ('\x94', 'oe'), ('\x99', 'Oe'), ('\x81', 'ue'), ('\x9a', 'Ue'), ('\xe1', 'ss'),
                ('\xe4', 'ae'), ('\xc4', 'Ae'), ('\xf6', 'oe'), ('\xd6', 'Oe'), ('\xfc', 'ue'), ('\xdc', 'Ue'), ('\xdf', 'ss')):
        s = s.replace(u,r)
    return s


class LangletTransformer(Transformer):
    '''
    Defines langlet specific CST transformations.
    '''
    @transform
    def stmt(self, node):
        for name in find_all(node, token.NAME):
            py_name = teuton_kw.get(name[1])
            if py_name:
                name[1] = replace_umlaut(py_name)
            else:
                name[1] = replace_umlaut(name[1])


    @transform
    def FUER(self, node):
        return Name('for')

    @transform
    def ZURUECK(self, node):
        return Name('return')

