import EasyExtend
import EasyExtend.util
import EasyExtend.eecommon
from EasyExtend.cst import py_symbol, py_token
from EasyExtend.csttools import rule_error
from nfagen import*
from nfatools import*
import pprint
import copy
import string


def get_name(langlet, nid):
    if isinstance(nid, str):
        return nid
    else:
        return langlet.lex_token.tok_name.get(nid,"")+langlet.lex_symbol.sym_name.get(nid,"")


class AbstractTokenStream(object):
    '''
    TokenStream class objects encapsulate iterator functionality over a token stream for a parser.
    '''
    def __init__(self, stream, ignored = []):
        self._ignored = ignored

    def __iter__(self):
        return self

    def is_ignored(self, tok):
        '''
        Returns True when input token is in ignore list otherwise False
        '''
        raise NotImplementedError

    def shift_read_position(self):
        '''
        Shifts read position of token stream without returning token.
        '''
        raise NotImplementedError

    def next(self):
        '''
        returns next token in token stream. Using a previous shift_read_position it is actually the current
        token. Raises StopIteration when the token stream is exhausted.
        '''
        raise NotImplementedError


class TokenStream(AbstractTokenStream):
    def __init__(self, stream, ignored = [], fileinfo = ""):
        self.tokstream = stream
        self.position = 0
        self.size = len(stream)
        self.ignored = ignored
        self.fileinfo = ""

    def current_pos(self):
        line = self.tokstream[:self.position].count('\n')+1
        col = self.position - self.tokstream[:self.position].rfind("\n")
        return (line, col)

    def __iter__(self):
        return self

    def is_ignored(self, tok):
        return tok[0] in self.ignored

    def shift_read_position(self):
        self.position+=1

    def next(self):
        while 1:
            try:
                tok = self.tokstream[self.position]
                return tok
            except IndexError:
                raise StopIteration

    def __len__(self):
        return self.size

def strip_line_info(lst):
    if len(lst)>2:
        if isinstance(lst[-1],int):
            del lst[-1]
    for item in lst:
        if isinstance(item, list):
            strip_line_info(item)
    if lst[0] == 4:
        lst[-1] = '\n'
    if lst[0] == 5:
        lst[-1] = ''
    return lst

class LiteralSet(object):
    def __init__(self, langlet):
        self.langlet  = langlet
        self.lex_nfa  = langlet.lex_nfa
        self.token    = langlet.lex_token
        self.litset = {}
        self.read_litset()
        self.ids = set(self.litset.keys())

    def read_litset(self):
        self.litset = self.lex_nfa.pseudo_token
        """
        self.litset[token.A_CHAR]    = string.letters+'_'
        self.litset[token.A_WHITE]   = string.whitespace
        self.litset[token.HEX_DIGIT] = string.hexdigits
        self.litset[token.OCT_DIGIT] = string.octdigits
        self.litset[token.NON_NULL_DIGIT] = '123456789'
        self.litset[token.DIGIT]     = string.digits
        """

    def __setitem__(self, nid, s):
        self.token.tok_name[nid]
        self.litset[nid] = s
        self.ids.update(nid)

    def __getitem__(self, nid):
        return self.litset.get(nid,"")

    def __contains__(self, nid):
        return (True if self.litset.get(nid) else False)


class Lexer(object):
    def __init__(self, langlet):
        self.langlet    = langlet
        self.debug      = langlet.options.get("debug_lexer", False)
        self.tabwidth   = 8
        self.offset     = langlet.lex_nfa.LANGLET_OFFSET
        self.rules      = langlet.lex_nfa.nfas
        self.reach      = langlet.lex_nfa.reachables
        self.keywords   = langlet.lex_nfa.keywords
        self.symbols_of = langlet.lex_nfa.symbols_of
        self.expanded   = langlet.lex_nfa.expanded
        self.graphs     = {}
        self.litset     = LiteralSet(langlet)
        self.pseudo_reachable = {}
        self.create_graph()
        self.T_ANY     = self.langlet.lex_token.abstract.ANY
        self.ENDMARKER = self.langlet.lex_symbol.ENDMARKER
        try:
            self.INTRON    = self.langlet.lex_symbol.INTRON
        except AttributeError:
            self.INTRON    = -1

    def create_graph(self):
        for r in self.rules:
            if r in self.expanded:
                continue
            g = SyntaxGraph(r, self.rules)
            g.create_connections()
            self.graphs[r] = g

    def matches(self, tok, s):
        if tok[0]%512 == 1 and isinstance(s, str):
            return s == tok[1]
        else:
            return s == tok[0]

    def is_token(self, s):
        try:
            return s%512<256
        except TypeError:
            return True

    def is_pseudotoken(self, s):
        return s in self.litset

    def get_token_type(self, tok):
        if tok[0]%512 == 1 and tok[1] in self.keywords:
            return tok[1]
        return tok[0]


#
#
#
#  NFALexer  --  general form of NFA trace parser
#
#
#

class NFALexer(Lexer):

    def _init_subtrees(self, sym):
        if sym in self.expanded:
            return []
        else:
            return [sym]

    def _new_cursor(self, sym):
        if sym in self.expanded:
            cursor = NFACursor(self.rules, sym)
            cursor.set_parsemode(True)
            return cursor
        else:
            return Cursor(self.graphs[sym])

    def _store_token(self, sym, cursor, sub_trees, tok):
        if sym in self.expanded:
            cursor.set_token(tok)
        else:
            sub_trees.append(list(tok[:-1]))

    def _derive_tree(self, sym, cursor, sub_trees):
        if sym in self.expanded:
            return cursor.derive_tree(sub_trees)
        else:
            return sub_trees

    def handle_error(self, sym, cursor, sub_trees, tok, selection):
        try:
            cst = self._derive_tree(sym, cursor, sub_trees)
        except RuntimeError:
            cst = sub_trees
        if cst:
            if isinstance(cst[0],list):
                rule = rule_error(self.langlet, cst[-1], selection, self.keywords, type = "lex")
            else:
                rule = rule_error(self.langlet, cst, selection, self.keywords, type = "lex")
        else:
            rule = ""
        word = tok[1]
        if tok[1] == '\n':
            word = r"\n"
        s = "Failed to scan input '%s' at (line %d , column %d). \n"%(word,tok[2],tok[3][1])
        raise LexerError(s+rule, **{"token": tok, "selection": selection})

    def parse(self, tokstream, start_symbol = None):
        if start_symbol is None:
            start_symbol = self.langlet.lex_symbol.token_input
        tok = tokstream.next()
        return self._parse(tokstream, start_symbol, tok)

    def is_pseudo_reachable(self, c, s):
        pseudo_token = self.pseudo_reachable.get(s)
        if pseudo_token is None:
            reach = self.reach.get(s,[])
            pseudo_token = [t for t in reach if self.is_pseudotoken(t)]
            self.pseudo_reachable[s] = pseudo_token
        for t in pseudo_token:
            if c in self.litset[t]:
                return True
        return False

    def _dbg_info(self, selection, char, T, move):
        if char in '\n':
            char = '\\n'
        if move == "step":
            if isinstance(T, str):
                print "char: %s -- rule: %s"%char
            else:
                name = get_name(self.langlet, T)
                print "char: %s -- rule: %s = "%(char, T)+name
            print "                   "+" "*(len(char)-2)+"next selection: %s"%(selection,)
        else:
            sym, s = T
            name_sym = get_name(self.langlet, sym)
            if isinstance(s, str):
                print "char: %s -- rule: %s "%(char,"'"+s+"'")+" (shift: %s)"%name_sym
            else:
                name_s = get_name(self.langlet, s)
                print "char: %s -- rule: %s = "%(char, s)+name_s+" (shift: %s)"%name_sym
            print "                   "+" "*(len(char)-2)+"next selection: %s"%(selection,)


    def __dbg_info(self, selection, char, sym):
        if char in '\n':
            char = '\\n'
        print "char: `%s` -- rule: %s -- next selection: %s"%(char, sym, selection)
        name = get_name(self.langlet, sym)
        print "                   %s"%name

    @EasyExtend.util.psyco_optimized
    def _parse(self, tokstream, sym, c):
        cursor = self._new_cursor(sym)
        selection = cursor.move(sym)
        if self.debug:
            self._dbg_info(selection, c, sym, "step")
        sub_trees = self._init_subtrees(sym)
        while c:
            for s in selection:
                if s is not None:
                    if s == self.T_ANY:
                        continue
                    if self.is_pseudotoken(s):
                        if c in self.litset[s]:
                            tokstream.shift_read_position()
                            self._store_token(sym, cursor, sub_trees, [s, c, 0, [0,0]] )
                            break
                        continue
                    elif c == s:
                        tokstream.shift_read_position()
                        self._store_token(sym, cursor, sub_trees, [self.T_ANY, c, 0, [0,0]] )
                        break
                    else:
                        reach = self.reach.get(s,[])
                        if reach:
                            if c in reach or self.is_pseudo_reachable(c,s):
                                res = self._parse(tokstream, s, c)
                                if res:
                                    sub_trees.append(res)
                                    break
            else:
                if self.T_ANY in selection:
                    line, col = tokstream.current_pos()
                    tokstream.shift_read_position()
                    self._store_token(sym, cursor, sub_trees, [self.T_ANY, c, line, [col,col]] )
                    s = self.T_ANY
                elif None in selection:
                    return self._derive_tree(sym, cursor, sub_trees)
                else:
                    line, col = tokstream.current_pos()
                    self.handle_error(sym, cursor, sub_trees, [self.T_ANY, c, line, [col,col]], selection)
            selection = cursor.move(s)
            if self.debug:
                self._dbg_info(selection, c, (sym, s), "shift")
            try:
                c = tokstream.next()
            except StopIteration:
                if None in selection:
                    return self._derive_tree(sym, cursor, sub_trees)
                elif self.ENDMARKER in selection:
                    return self._derive_tree(sym, cursor, sub_trees)
                else:
                    line, col = tokstream.current_pos()
                    self.handle_error(sym, cursor, sub_trees, [self.T_ANY, c, line, [col,col]], selection)
                c = None
        return sub_trees

    def _scan(self, tokstream):
        '''
        Scanning is considered as an action that mediates an input stream of characters ( original token-stream )
        and a partitioned output stream.

        The partitioning takes the set nfamodule.terminals into consideration because those are actually required
        by the parser.

        If no corresponding node id could be found take the first node subsequent to unit.

        '''
        cst = self.parse(tokstream)
        # pprint.pprint(cst)
        lex_nfa = self.langlet.lex_nfa
        parse_nfa = self.langlet.parse_nfa
        tok = [0,'',(1,1),(0,0)]
        terminals = parse_nfa.terminals
        pseudo_token = lex_nfa.pseudo_token
        for unit in cst[1:]:
            token = self.handle_unit(unit, terminals, pseudo_token, tok)
            for tok in token:
                yield tok

    def scan(self, tokstream):
        return [s for s in self._scan(tokstream)]

    @EasyExtend.util.psyco_optimized
    def _tostr_lst(self, node):
        l_s = []
        for item in node:
            if isinstance(item, str):
                l_s.append(item)
                break
            elif isinstance(item, list):
                l_s.extend(self._tostr_lst(item))
        return l_s

    @EasyExtend.util.psyco_optimized
    def handle_unit(self, unit, terminals, pseudo_token, last_token):
        sub_unit = unit
        nid = unit[1][0]
        while True:
            if sub_unit[0]-256 in terminals:
                if sub_unit[0] not in pseudo_token:
                    nid = sub_unit[0]
            if len(sub_unit) == 2:
                sub_unit = sub_unit[1]
            else:
                break
        try:
            node = (nid, self.langlet.lex_token.tok_name.get(nid,"")+self.langlet.lex_symbol.tok_name.get(nid,""))
        except KeyError:
            node = (nid, '')

        (line_begin_old, line_end_old) = last_token[2]
        (col_begin_old, col_end_old)   = last_token[-1]
        col_begin  = col_end_old
        line_begin = line_end_old
        s = ''.join(self._tostr_lst(unit))
        if nid == self.INTRON:
            intron = []
            for item in unit[1]:
                if isinstance(item, list):
                    nd = item[0]
                    item_nd = (nd, self.langlet.lex_token.tok_name.get(nd,"")+self.langlet.lex_symbol.tok_name.get(nd,""))
                    item_s  = ''.join(self._tostr_lst(item))
                    intron.append((item_nd, item_s))
                #else:
                #    intron.append(item)
            s = s.replace("\t", " "*self.tabwidth)
            line_breaks = s.count("\n")
            if line_breaks:
                col_end = len(s) - s.rfind("\n")-1
            else:
                col_end = col_begin+len(s)
            line_end = line_end_old+line_breaks
            return [[node, intron, (line_begin, line_end), (col_begin, col_end)]]
        else:
            return [[node, s, (line_begin, line_begin), (col_begin, col_begin+len(s))]]

class token_langlet(object):
    def __init__(self, langlet):
        self.__langlet = langlet
        self.parse_symbol = self.symbol = langlet.token
        self.parse_token  = self.token  = langlet.lex_token
        self.parse_nfa    = langlet.lex_nfa
        self.parse_nfa.LANGLET_OFFSET-=256

    def __getattr__(self, name):
        return getattr(self.__langlet, name)

cst = None

def test_lexer():
    import EasyExtend.langlets.zero.langlet
    langlet = token_langlet(EasyExtend.langlets.zero.langlet)
    symbol  = langlet.lex_symbol
    token   = langlet.lex_token

    #import EasyExtend.langlets.blub6.langlet as langlet
    #import EasyExtend.langlets.blub6.lexdef.lex_nfa as lex_nfa
    #symbol  = langlet.token
    #token   = langlet.lex_token

    unparse = langlet.unparse
    from EasyExtend.csttools import find_node

    lex = NFALexer(langlet)

    cst = lex.parse(TokenStream("a.b"))
    pprint.pprint(cst)

    #scanned = lex.scan(TokenStream("0x00 ++ 0x01"))
    #pprint.pprint(scanned)

    cst = lex.parse(TokenStream("def f(): #bla\n  pass"))
    #langlet.pprint(cst)
    #print lex.scan(TokenStream("def f():\n  pass"))

    #cst = lex.parse(TokenStream("0+\\n1"))
    #assert find_node(cst, symbol.Decnumber)
    #langlet.pprint(cst)

    cst = lex.parse(TokenStream("01"))
    assert find_node(cst, symbol.NUMBER)

    cst = lex.parse(TokenStream("1.90"))
    assert find_node(cst, symbol.NUMBER)

    cst = lex.parse(TokenStream("\n"))
    assert find_node(cst, symbol.INTRON)

    cst = lex.parse(TokenStream(">>="))
    assert find_node(cst, symbol.RIGHTSHIFTEQUAL)

    cst = lex.parse(TokenStream(">>"))
    assert find_node(cst, symbol.RIGHTSHIFT)

    cst = lex.parse(TokenStream(">"))
    assert find_node(cst, symbol.GREATER)

    cst = lex.parse(TokenStream("abab"))
    assert find_node(cst, symbol.NAME)

    cst = lex.parse(TokenStream("a123"))
    assert find_node(cst, symbol.NAME)

    cst = lex.parse(TokenStream("'l$'"))
    assert find_node(cst, symbol.STRING)

    cst = lex.parse(TokenStream("r'''o+45\n6&7$'''"))
    assert find_node(cst, symbol.Single3)


if __name__ == '__main__':
    test_lexer()
