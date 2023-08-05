'''
Module used to define compiled token for the eetokenizer. This module is based
on definitions made in std-libs tokenize.py
'''

import re

def quote_single(prefix):
    """
    For some string s this method defines: s -> s'
    """
    all = []
    for p in prefix:
        all+=[p+"'",p+'"']
    return tuple(all)

def quote_triple(prefix):
    """
    For some string s this method defines: s -> s'''
    """
    all = []
    for p in prefix:
        all+=[p+"'''",p+'"""']
    return tuple(all)

def gettoken(fibertoken):
    '''
    Creates compiled token values used by the tokenizer. These token values depend on
    specific FiberToken classes defined for fibers.

    @param fibertoken: token module instance of fiber.
    '''
    used_defs = {}

    def group(*choices): return '(' + '|'.join(choices) + ')'
    def any(*choices): return group(*choices) + '*'
    def maybe(*choices): return group(*choices) + '?'

    Whitespace = r'[ \f\t]*'
    CommentToken = fibertoken.FiberToken.Comment()
    Comment = CommentToken+r'[^\r\n]*'
    Ignore = Whitespace + any(r'\\\r?\n' + Whitespace) + maybe(Comment)
    Fat = fibertoken.FiberToken.Fat()
    if Fat:
        Fat = group(*fibertoken.FiberToken.Fat())

    Name = group(*(fibertoken.FiberToken.Name()))

    Hexnumber = r'0[xX][\da-fA-F]*[lL]?'
    Octnumber = r'0[0-7]*[lL]?'
    Decnumber = r'[1-9]\d*[lL]?'
    Intnumber = group(Hexnumber, Octnumber, Decnumber)
    Exponent = r'[eE][-+]?\d+'
    Pointfloat = group(r'\d+\.\d*', r'\.\d+') + maybe(Exponent)
    Expfloat = r'\d+' + Exponent
    Floatnumber = group(Pointfloat, Expfloat)
    Imagnumber = group(r'\d+[jJ]', Floatnumber + r'[jJ]')
    Number = group(Imagnumber, Floatnumber, Intnumber,*(fibertoken.FiberToken.Number()))

    # Tail end of ' string.
    Single = r"[^'\\]*(?:\\.[^'\\]*)*'"
    # Tail end of " string.
    Double = r'[^"\\]*(?:\\.[^"\\]*)*"'
    # Tail end of ''' string.
    Single3 = r"[^'\\]*(?:(?:\\.|'(?!''))[^'\\]*)*'''"
    # Tail end of """ string.
    Double3 = r'[^"\\]*(?:(?:\\.|"(?!""))[^"\\]*)*"""'
    Triple = group("[uU]?[rR]?'''", '[uU]?[rR]?"""')
    # Single-line ' or " string.
    STR_PREFIX = fibertoken.FiberToken.StrPrefix()
    str_prefix = ""
    if STR_PREFIX:
        str_prefix = "["+"".join(STR_PREFIX)+"]?"
    String = group(str_prefix+r"[uU]?[rR]?'[^\n'\\]*(?:\\.[^\n'\\]*)*'",
                   str_prefix+r'[uU]?[rR]?"[^\n"\\]*(?:\\.[^\n"\\]*)*"')
    # Because of leftmost-then-longest match semantics, be sure to put the
    # longest operators first (e.g., if = came before ==, == would get
    # recognized as two instances of =).
    INITIAL = re.compile(group(*fibertoken.FiberToken.Initial()))
    FINAL   = re.compile(group(*fibertoken.FiberToken.Final()))
    Bracket = group(*(fibertoken.EEToken.Initial()+fibertoken.FiberToken.Final())) #'[][(){}]'
    #Special = group(r'\r?\n', r'[:;.,`@]')
    Special = group(r'\r?\n')
    Funny = group(Special,*(fibertoken.FiberToken.Funny()) )

    pFunny = re.compile(Funny)
    token_classes = []
    if Fat:
        token_classes = [Fat]
    if fibertoken.FiberToken.NoNumber is False:
        token_classes.append(Number)
    token_classes.append(Funny)
    if fibertoken.FiberToken.NoString is False:
        token_classes.append(String)
    if fibertoken.FiberToken.NoName is False:
        token_classes.append(Name)

    PlainToken = group(*token_classes)

    Token = Ignore + PlainToken


    # First (or only) line of ' or " string.
    ContStr = group(str_prefix+r"[uU]?[rR]?'[^\n'\\]*(?:\\.[^\n'\\]*)*" +
                    group("'", r'\\\r?\n'),
                    str_prefix+r'[uU]?[rR]?"[^\n"\\]*(?:\\.[^\n"\\]*)*' +
                    group('"', r'\\\r?\n'))
    PseudoExtras = group(r'\\\r?\n', Comment, Triple)

    if Fat:
        PseudoToken = Whitespace + group(Fat, PseudoExtras, PlainToken, ContStr)
    else:
        PseudoToken = Whitespace + group(PseudoExtras, PlainToken, ContStr)

    tokenprog   = re.compile(Token)
    pseudoprog  = re.compile(PseudoToken)
    single3prog = re.compile(Single3)
    double3prog = re.compile(Double3)

    endprogs = {"'": re.compile(Single), '"': re.compile(Double),
                "'''": single3prog, '"""': double3prog,
                "r'''": single3prog, 'r"""': double3prog,
                "u'''": single3prog, 'u"""': double3prog,
                "ur'''": single3prog, 'ur"""': double3prog,
                "R'''": single3prog, 'R"""': double3prog,
                "U'''": single3prog, 'U"""': double3prog,
                "uR'''": single3prog, 'uR"""': double3prog,
                "Ur'''": single3prog, 'Ur"""': double3prog,
                "UR'''": single3prog, 'UR"""': double3prog,
                'r': None, 'R': None, 'u': None, 'U': None}

    triple_quoted = {}
    for t in ("'''", '"""',
              "r'''", 'r"""', "R'''", 'R"""',
              "u'''", 'u"""', "U'''", 'U"""',
              "ur'''", 'ur"""', "Ur'''", 'Ur"""',
              "uR'''", 'uR"""', "UR'''", 'UR"""')+quote_triple(STR_PREFIX):
        triple_quoted[t] = t

    single_quoted = {}

    for t in ("'", '"',
              "r'", 'r"', "R'", 'R"',
              "u'", 'u"', "U'", 'U"',
              "ur'", 'ur"', "Ur'", 'Ur"',
              "uR'", 'uR"', "UR'", 'UR"' )+quote_single(STR_PREFIX):
        single_quoted[t] = t

    multiline = {}
    for k,v in fibertoken.FiberToken.Multiline().items():
        multiline[k] = re.compile('(.|[\n\r])*?%s'%re.escape(v), re.M)
    used_defs["INITIAL"]  = INITIAL
    used_defs["FINAL"]    = FINAL
    used_defs["pFunny"]   = pFunny
    used_defs["endprogs"] = endprogs
    used_defs["pseudoprog"]    = pseudoprog
    used_defs["single_quoted"] = single_quoted
    used_defs["triple_quoted"] = triple_quoted
    used_defs["linecomment"]   = CommentToken
    used_defs["multiline"]     = multiline  # covered by ''' or """ in pure Python
    return used_defs


if __name__ == '__main__':
    import EasyExtend.fibers.gallery.fibermod.token as fibertoken
    fibertoken.FiberToken()
    gettoken(fibertoken)


