# URL:     http://www.fiber-space.de
# Author:  Kay Schluehr <easyextend@fiber-space.de>
# Date:    10 May 2006

'''
Defines functions and classes that are commonly used by all langlets.
'''

import sys

def load_symbols(f):
    import EasyExtend.eegrammar as eegrammar
    need_lex_nfa   = eegrammar.EETokenGrammar(f).load_grammar()
    need_parse_nfa = eegrammar.EEGrammar(f).load_grammar()
    return need_lex_nfa, need_parse_nfa

def load_nfas(langlet, *qual):
    need_lex, need_parse = qual
    from EasyExtend.trail.nfagen import create_lex_nfa, create_parse_nfa
    if need_parse:
        create_parse_nfa(langlet)
    if need_lex:
        create_lex_nfa(langlet)

def load_tokenizer(langlet):
    if hasattr(langlet, "LangletTokenizer"):
        return langlet.LangletTokenizer(langlet)
    else:
        from EasyExtend.eetokenizer import Tokenizer
        return Tokenizer(langlet)

def load_importer(langlet):
    if hasattr(langlet, "LangletImporter"):
        importer = langlet.LangletImporter(langlet)
    else:
        import eeimporter
        importer = eeimporter.Importer(langlet)
    langlet.importer = importer
    importer.register_importer()
    return importer

def tokenize(langlet, source):
    '''
    Tokenize source string and return token stream.
    '''
    from EasyExtend.eetokenizer import Tokenizer
    tokenizer = Tokenizer(langlet)
    return tokenizer.tokenize_string(source)

def parse(langlet, source, start_symbol = None):
    '''
    Parse source string and return CST.
    '''
    from   EasyExtend.trail.nfaparser import TokenStream, NFAParser
    parser = NFAParser(langlet)
    stream = tokenize(langlet, source)
    if source.endswith("\n") or start_symbol:
        parseTree = parser.parse(TokenStream(stream), start_symbol = start_symbol)
    else:
        parseTree = parser.parse(TokenStream(stream), langlet.parse_symbol.eval_input)
    return parseTree


def publish_as_builtin(langlet):
    '''
    @param langlet: used langlet.
    '''
    import __builtin__
    if hasattr(langlet,"__publish__"):
        for name in langlet.__publish__:
            __builtin__.__dict__[name] = langlet.__dict__[name]

def new_langlet(name, prompt = ">>> ", loc = "", source_ext = ".py", compiled_ext = ".pyc"):
    import fstools
    cmd = fstools.LangletGenerator(name, prompt = prompt, loc = loc, source_ext = source_ext, compiled_ext = compiled_ext)
    cmd.execute()

def run(langlet_name, args = None):
    '''
    Executes langlet specific console.

    @param: langlet_name. langlet will be looked up in directory EasyExtend.langlets
    '''
    exec "from EasyExtend.langlets.%s import langlet as running_langlet"%langlet_name
    if args:
        (options,args) = running_langlet.opt.parse_args(args.split())
        running_langlet.options  = options.__dict__
    import __main__
    __main__.__dict__["langlet"] = running_langlet
    console = create_console(langlet_name, running_langlet)
    console.interact()

def _check_langlet(langlet):
    if not hasattr(langlet, "LangletTransformer"):
        raise AttributeError, "LangletTransformer missing in langlet"
    if not hasattr(langlet, "symbol"):
        raise AttributeError, "symbol missing in langlet"
    if not hasattr(langlet, "__publish__"):
        raise AttributeError, "__publish__ missing in langlet"
    if langlet.compiled_ext in (".pyz", "pyz") or langlet.source_ext in (".pyz", "pyz"):
        raise ValueError("The file extension '*.pyz' is a reserved zip-archive extension in EE. Please select another extension!")

def create_console(console_name, langlet):
    '''
    Creates interactive console object.
    @param console_name: name of the new console object.
    @param langlet: langlet module.
    '''
    import eeconsole
    from   exotools import Exospace
    import __builtin__
    __builtin__.__dict__["exospace"] = Exospace(0)
    init_langlet(langlet)
    load_importer(langlet)
    session   = langlet.options.get("session")
    recording = langlet.options.get("recording")
    if session:
        if recording:
            interp = eeconsole.EERecordedReplayConsole(langlet, console_name, session = session, recording = recording)
        else:
            interp = eeconsole.EEReplayConsoleTest(langlet, console_name, session = session)
    elif recording:
        interp = eeconsole.EERecordedConsole(langlet, console_name, recording = recording)
    else:
        interp = eeconsole.EEConsole(langlet, console_name)
    return interp

def init_langlet(langlet):
    import csttools
    if hasattr(langlet, "is_initialized"):
        return
    _check_langlet(langlet)
    langlet.check_node = lambda node, strict=True: csttools.check_node(node, langlet, strict)
    publish_as_builtin(langlet)
    langlet.is_initialized = True

def import_and_init_langlet(langlet_name):
    langlet = __import__("EasyExtend.langlets."+langlet_name+".langlet", globals(), locals(), ["EasyExtend"])
    init_langlet(langlet)
    return langlet

def run_module(module_name, langlet):
    '''
    @param py_module: python module name ( may include extension ).
    @param langlet: langlet module.
    '''
    init_langlet(langlet)
    load_importer(langlet)
    import os
    _mod   = module_name.split(".")[0]
    _mod   = _mod.replace(os.sep,".")
    __import__(_mod)
    Module = sys.modules[_mod]
    if hasattr(Module, "__like_main__"):
        Module.__like_main__()



