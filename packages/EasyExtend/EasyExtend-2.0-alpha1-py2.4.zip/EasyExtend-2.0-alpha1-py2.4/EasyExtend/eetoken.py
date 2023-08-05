'''
This module defines the EEToken class. The EEToken class is essenially a namespace for all kinds
of token definitions and some tokenizer flags ( NoNumber, NoName ... ) that are mentioned for
so called "tiny" fibers ( small languages defined within the EasyExtend framework but not extending
Python and not defining sets of aforementioned token ). The token are defined as triples

        cls.TOKEN-NAME = (TOKEN-ID, TOKEN-VALUE, TOKEN-TYPE)

The token.py module of the std-library defines only TOKEN-NAME = TOKEN-ID correspondences whereas
in parser modules TOKEN-NAME = TOKEN-VALUE correspondences are created.

Typically parser modules like PyGen.py or DFAParser.py but also the tokenizer and cst modules access
id's directly at the module level using token names: token.NAME, token.STRING, .... In order to preserve
this interface EEToken defines the important method gen_token. A single parameter is passed to gen_token namely
the fiber specific token.py module. It generates all these token constants with the correct id's but also
dictionaries tok_name and TOKEN_MAP that where previously used for accessing token names from token id's
and token values from names.
Another important aspect of the gen_token implementation is the fiber-space support: node id's will be
automatically lifted to node id's of the range [FIBER_OFFSET, FIBER_OFFSET+512].

The EEToken class is dedicated to be extended in proper token.py modules of fibers in the following manner:

    class FiberToken(EEToken):
        def __new__(cls):
            # some token definitions...
            cls.MY_TOKEN = (100, '%$=..', SPECIAL)
            # other token definitions ...
            return cls

The residual uppercase class methods Name, Funny, StrPrefix,... are used by the eetokpattern.py.
They return a size ordered list of TOKEN-VALUEs ( sizes are ordered s.t. the longest TOKEN-VALUEs
precedes the shorter ones ) according to a TOKEN-TYPE.

'''
import re

_ = 'THIS-NAME'
SPECIAL     = "SPEC"
OPERATOR    = "OP"
LBRA        = "LBRA"
RBRA        = "RBRA"
TOKENIZE_PY = "TOK"
NUM         = "NUM"
FAT_MODE    = "FAT"
STR_PREFIX  = "STR_PREFIX"

class re_expr(str):
    def __init__(self, expr):
        str.__init__(self,expr)

class Pgen:
    MSTART = 256
    RULE   = 257
    RHS    = 258
    ALT    = 259
    ITEM   = 260
    ATOM   = 261

class EEToken(object):
    def __new__(cls):
        # --begin of default constants --
        # Warning! Do not change this section
        cls.ENDMARKER   = (0, _, TOKENIZE_PY)
        cls.NAME        = (1, _, TOKENIZE_PY)
        cls.NUMBER      = (2, _, TOKENIZE_PY)
        cls.STRING      = (3, _, TOKENIZE_PY)
        cls.NEWLINE     = (4, _, TOKENIZE_PY)
        cls.INDENT      = (5, _, TOKENIZE_PY)
        cls.DEDENT      = (6, _, TOKENIZE_PY)
        cls.LPAR        = (7, "(", LBRA)
        cls.RPAR        = (8, ")", RBRA)
        cls.LSQB        = (9, "[", LBRA)
        cls.RSQB        = (10, "]", RBRA)
        cls.COLON       = (11, ":", SPECIAL)
        cls.COMMA       = (12, ",", SPECIAL)
        cls.SEMI        = (13, ";", SPECIAL)
        cls.PLUS        = (14, "+", OPERATOR)
        cls.MINUS       = (15, "-", OPERATOR)
        cls.STAR        = (16, "*", OPERATOR)
        cls.SLASH       = (17, "/", OPERATOR)
        cls.VBAR        = (18, "|", OPERATOR)
        cls.AMPER       = (19, "&", OPERATOR)
        cls.LESS        = (20, "<", OPERATOR)
        cls.GREATER     = (21, ">", OPERATOR)
        cls.EQUAL       = (22, "=", OPERATOR)
        cls.DOT         = (23, ".", SPECIAL)
        cls.PERCENT     = (24, "%", OPERATOR)
        cls.BACKQUOTE   = (25, "`", SPECIAL)
        cls.LBRACE      = (26, "{", LBRA)
        cls.RBRACE      = (27, "}", RBRA)
        cls.EQEQUAL     = (28, "==", OPERATOR)
        cls.NOTEQUAL    = (29, "!=", OPERATOR)
        cls.LESSEQUAL   = (30, "<=", OPERATOR)
        cls.GREATEREQUAL= (31, ">=", OPERATOR)
        cls.TILDE       = (32, "~", OPERATOR)
        cls.CIRCUMFLEX  = (33, "^", OPERATOR)
        cls.LEFTSHIFT   = (34, "<<", OPERATOR)
        cls.RIGHTSHIFT  = (35, ">>", OPERATOR)
        cls.DOUBLESTAR  = (36, "**", OPERATOR)
        cls.PLUSEQUAL   = (37, "+=", OPERATOR)
        cls.MINEQUAL    = (38, "-=", OPERATOR)
        cls.STAREQUAL   = (39, "*=", OPERATOR)
        cls.SLASHEQUAL  = (40, "/=", OPERATOR)
        cls.PERCENTEQUAL= (41, "%=", OPERATOR)
        cls.AMPEREQUAL  = (42, "&=", OPERATOR)
        cls.VBAREQUAL   = (43, "|=", OPERATOR)
        cls.CIRCUMFLEXEQUAL = (44, "^=", OPERATOR)
        cls.LEFTSHIFTEQUAL  = (45, "<<=", OPERATOR)
        cls.RIGHTSHIFTEQUAL = (46, ">>=", OPERATOR)
        cls.DOUBLESTAREQUAL = (47, "**=", OPERATOR)
        cls.DOUBLESLASH = (48, "//", OPERATOR)
        cls.DOUBLESLASHEQUAL= (49, "//=", OPERATOR)
        cls.AT          = (50, "@", SPECIAL)
        cls.OP          = (51, _, TOKENIZE_PY)
        cls.ERRORTOKEN  = (52, "?ERRORTOKEN", TOKENIZE_PY)
        cls.COMMENT     = (53, _, TOKENIZE_PY)
        cls.NL          = (54, _, TOKENIZE_PY)
        cls.N_TOKENS    = (55, _, TOKENIZE_PY)
        cls.FAT         = (70, _, TOKENIZE_PY)     # new token -- not defined in Python
        cls.BACKSLASH   = (71, "\\", TOKENIZE_PY)  # new token -- not defined in Python
        cls.NT_OFFSET   = (256, _, TOKENIZE_PY)
        #--end of default constants--

        # Pgen token
        cls.Pgen = object()

        # tokenizer switches
        cls.NoNumber  = False
        cls.NoName    = False
        cls.NoString  = False
        cls.NoContStr = False
        cls.DropWhitespace = False

    @classmethod
    def select(cls, typ=None):
        pattern = []
        for name in dir(cls):
            val = getattr(cls, name)
            if type(val) == type(()) and len(val) >= 2:
                if len(val) == 3 and val[2] == typ:
                    pattern.append(val[1])
                elif typ == None and val[2]!=TOKENIZE_PY:
                    pattern.append(val[1])
        pattern.sort(lambda a,b: len(a)-len(b))
        return pattern

    @classmethod
    def Funny(cls):
        pattern = []
        funny = cls.select(LBRA)+cls.select(RBRA)+cls.select(OPERATOR)+cls.select(SPECIAL)
        for item in funny:
            if len(item) == 1:
                pattern.append(item)
            elif item[-1] == "=":
                try:
                    k = pattern.index(item[:-1])
                    pattern[k] = (item,"?")
                except ValueError:
                    pattern.append(item)
            else:
                pattern.insert(0,item)
        for i,p in enumerate(pattern):
            if type(p) == type(()):
                pattern[i] = re.escape(p[0])+p[1]
            elif isinstance(p, re_expr):
                pattern[i] = p
            else:
                pattern[i] = re.escape(p)
        return pattern

    @classmethod
    def Multiline(cls):
        return {}

    @classmethod
    def Comment(cls):
        return '#'

    @classmethod
    def Number(cls):
        return cls.select(NUM)

    @classmethod
    def StrPrefix(cls):
        return cls.select(STR_PREFIX)

    @classmethod
    def Fat(cls):
        return cls.select(FAT_MODE)

    @classmethod
    def Name(cls):
        return [r'[a-zA-Z_]\w*']

    @classmethod
    def Initial(cls):
        return map(re.escape, cls.select(LBRA))

    @classmethod
    def Final(cls):
        return map(re.escape, cls.select(RBRA))


    @classmethod
    def lift_pgen(cls, offset):
        for name in dir(Pgen):
            val = getattr(Pgen,name)
            if isinstance(val, int):
                cls.Pgen = val+offset

    @classmethod
    def gen_token(cls, token):
        tok_name  = {}
        TOKEN_MAP = {"<>":29+token.FIBER_OFFSET}
        for name in dir(cls):
            val = getattr(cls,name)
            if type(val) == type(()) and len(val) >= 2:
                setattr(token,name,val[0]+token.FIBER_OFFSET)
                if val[1] == _:
                    TOKEN_MAP[name] = val[0]+token.FIBER_OFFSET
                else:
                    TOKEN_MAP[val[1]] = val[0]+token.FIBER_OFFSET
                tok_name[val[0]+token.FIBER_OFFSET] = name
            elif name.startswith("No"):  # NoContStr etc.
                setattr(token,name,val)
        setattr(token,"tok_name",tok_name)
        setattr(token,"TOKEN_MAP",TOKEN_MAP)
        cls.lift_pgen(token.FIBER_OFFSET)


