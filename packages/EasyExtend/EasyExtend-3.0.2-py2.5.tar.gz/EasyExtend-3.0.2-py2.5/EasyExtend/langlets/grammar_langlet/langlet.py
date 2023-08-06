from conf import*
import EasyExtend
import EasyExtend.cst2source as cst2source
from EasyExtend.csttools import*
from EasyExtend.eetransformer import Transformer, transform
from EasyExtend.util.path import path
import pprint


class LangletTransformer(Transformer):
    '''
    Defines fiber specific transformations
    '''

__publish__ = []

def _load_grammar_source(langlet, grammar_type):
    try:
        if grammar_type == "Grammar":
            return path(langlet.__file__).dirname().joinpath("parsedef", grammar_type).open().read()
        else:
            return path(langlet.__file__).dirname().joinpath("lexdef", grammar_type).open().read()

    except IOError:
        return path(EasyExtend.__file__).dirname().joinpath(grammar_type).open().read()
    except AttributeError:
        return F.get_grammar_source()


def load_grammar_cst(langlet, grammar_type = "Grammar"):
    import EasyExtend.langlets.grammar_langlet.langlet as grammar_langlet
    from EasyExtend.trail.nfaparser import NFAParser, TokenStream

    source = _load_grammar_source(langlet, grammar_type)

    # tokenize grammar file
    stream = grammar_langlet.tokenize(source)
    assert stream

    # parse grammar file
    parser = NFAParser(grammar_langlet)
    tokenstream = TokenStream(stream)
    tokenstream.position = 0
    cst = parser.parse(tokenstream, grammar_langlet.symbol.file_input)
    return cst


def selftest():
    import EasyExtend.langlets.grammar_langlet.langlet as grammar_langlet
    load_grammar_cst(grammar_langlet)


