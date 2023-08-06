import EasyExtend
import EasyExtend.util
from EasyExtend.cst import py_symbol, py_token
from EasyExtend.csttools import rule_error
from nfagen import*
from nfatracing import*
import pprint
import copy

__DEBUG__ = False

LANGLET = None

def get_name(langlet, nid):
    if isinstance(nid, str):
        return "'"+nid+"'"
    else:
        return langlet.parse_symbol.sym_name.get(nid,"")+langlet.parse_token.tok_name.get(nid,"")


class AbstractTokenStream(object):
    '''
    TokenStream class objects encapsulate iterator functionality over a token stream for a parser.
    '''
    def __init__(self, stream, ignored = []):
        self._ignored = ignored

    def __iter__(self):
        return self

    def __getitem__(self, idx):
        raise NotImplementedError

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

    def __len__(self):
        raise NotImplementedError

class TokenStream(AbstractTokenStream):
    def __init__(self, stream, ignored = []):
        try:
            self.tokstream = stream.tokstream
            self.position = stream.position
            self.size = stream.size
            self.ignored = stream.ignored[:]
        except AttributeError:
            self.tokstream = stream
            self.position = 0
            self.size = len(stream)
            self.ignored = ignored

    def __iter__(self):
        return self

    def __getitem__(self, idx):
        return self.tokstream[idx]

    def is_ignored(self, tok):
        return tok[0] in self.ignored

    def shift_read_position(self):
        self.position+=1

    def next(self):
        while 1:
            try:
                tok = self.tokstream[self.position]
                if tok[0] in self.ignored:
                    self.position+=1
                else:
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


class EEParser(object):
    def __init__(self, langlet):
        self.langlet    = langlet
        self.debug      = langlet.options.get("debug_parser", False)
        self.offset     = langlet.parse_nfa.LANGLET_OFFSET
        self.rules      = langlet.parse_nfa.nfas
        self.reach      = langlet.parse_nfa.reachables
        self.ancestors  = langlet.parse_nfa.ancestors
        self.keywords   = langlet.parse_nfa.keywords
        self.symbols_of = langlet.parse_nfa.symbols_of
        self.expanded   = langlet.parse_nfa.expanded
        self.graphs = {}
        self._cache = {}
        #self.create_graph()

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

    def get_token_type(self, tok):
        if tok[0]%512 == 1 and tok[1] in self.keywords:
            return tok[1]
        return tok[0]
#
#
#
#  NFAMatcher  --  acts somewhat like a parser but is used to accept a stream of a lexical scan
#
#
#
'''
class NFAMatcher(NFAParser):
    def match(self, tokstream, sym):
        tok = tokstream.next()
        return self._parse(tokstream, sym, tok, None)

    @EasyExtend.util.psyco_optimized
    def _parse(self, tokstream, sym, tok, parent):
        cursor = self._new_cursor(sym)
        selection = cursor.move(sym)
        if self.debug:
            self._dbg_info(selection, tok, sym, "step")
        while tok:
            if tok[1] in self.keywords:
                token_type = tok[1]
            else:
                token_type = tok[0]

            for s in selection:
                if s is not None:
                    if is_token(s):
                        if token_type == s:
                            tokstream.shift_read_position()
                            break
                    elif token_type in self.reach.get(s,[]):
                        res = self._parse(tokstream, s, tok, sym)
                        if res:
                            break
                        else:
                            continue
            else:
                if None in selection:
                    return True
                else:
                    return False
            selection = cursor.move(s)
            if self.debug:
                self._dbg_info(selection, tok, (sym, s), "shift")
            try:
                tok = tokstream.next()
            except StopIteration:
                tok = None
        return True
'''


#
#
#
#  NFAParser  --  general form of NFA trace parser
#
#
#


class NFAParser(EEParser):

    def _init_subtrees(self, sym):
        if sym in self.expanded:
            return []
        else:
            return [sym]

    def _new_cursor(self, sym):
        if sym in self.expanded:
            return NFACursor(self.rules, sym, self._cache)
        else:
            return SimpleNFACursor(self.rules, sym, self._cache)

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

    def handle_error(self, sym, cursor, sub_trees, tok, selection, tokstream):
        if sub_trees:
            cst = sub_trees
        else:
            cursor.terminate()
            cst = self._derive_tree(sym, cursor, sub_trees)[:-1]
        if cst:
            if isinstance(cst[0],list):
                rule = rule_error(self.langlet, cst[-1], selection, self.keywords, type = "parse")
            else:
                rule = rule_error(self.langlet, cst, selection, self.keywords, type = "parse")
        else:
            rule = ""
        word = tok[1]
        if tok[1] == '\n':
            word = r"\n"
        line = "    "+self.untokenize_line(tokstream)
        error_line = "\n"+line+'\n'+" "*(tok[3][0]+4)+"^"*(tok[3][1]-tok[3][0])+"\n"
        s = "Failed to parse input '%s' at (line %d , column %d). \n"%(word,tok[2],tok[3][0]+1)
        raise ParserError(s+error_line+rule, **{"token": tok, "selection": selection})

    def untokenize_line(self, tokenstream):
        '''
        Method used to reconstruct current line from tokenstream for highlighting errors.

        Point of analysis is the position of the current token.
        '''
        p   = tokenstream.position
        tok = tokenstream[p]
        lno = tok[2]
        l = p-1
        r = p+1
        left = []
        right = []
        while l>=0:
            T = tokenstream[l]
            if T[2] == lno:
                left.insert(0, T)
                l-=1
            else:
                break
        while r<tokenstream.size:
            T = tokenstream[r]
            if T[2] == lno:
                right.append(T)
                r+=1
            else:
                break
        stream = []
        col_end = 0
        for T in left+[tok]+right:
            k = T[3][0]-col_end
            if k:
                stream.append(' '*k)
            stream.append(T[1])
            col_end = T[3][1]
        return ''.join(stream)



    def _dbg_info(self, selection, tok, T, move):
        t = str(tok)
        if move == "step":
            if isinstance(T, str):
                print "token: %s -- rule: %s"%(t, T)
            else:
                name = get_name(self.langlet, T)
                print "token: %s -- rule: %s = "%(t, T)+name
            print "                   "+" "*(len(t)-2)+"next selection: %s"%(selection,)
        else:
            sym, s = T
            name_sym = get_name(self.langlet, sym)
            if isinstance(s, str):
                print "token: %s -- rule: %s "%(t,"'"+s+"'")+" (shift: %s)"%name_sym
            else:
                name_s = get_name(self.langlet, s)
                print "token: %s -- rule: %s = "%(t, s)+name_s+" (shift: %s)"%name_sym
            print "                   "+" "*(len(t)-2)+"next selection: %s"%(selection,)


    def parse(self, tokstream, start_symbol = None):
        if start_symbol is None:
            start_symbol = self.offset+257 # file_input
        tok = tokstream.next()
        return self._parse(tokstream, start_symbol, tok)

    @EasyExtend.util.psyco_optimized
    def _parse(self, tokstream, sym, tok, parent = 0):
        cursor = self._new_cursor(sym)
        selection = cursor.move(sym, tok)
        if self.debug:
            self._dbg_info(selection, tok, sym, "step")
        sub_trees = self._init_subtrees(sym)
        while tok:
            if tok[1] in self.keywords:
                token_type = tok[1]
            else:
                token_type = tok[0]

            if token_type in selection:
                tokstream.shift_read_position()
                self._store_token(sym, cursor, sub_trees, tok[:-1])
                s = token_type
            else:
                try:
                    nts = self.ancestors[token_type]
                    #print "DEBUG - selection 2", selection
                    S = nts & selection
                    if S:
                        s = S.pop()
                        res = self._parse(tokstream, s, tok, sym)
                        if res:
                            sub_trees.append(res)
                    else:
                        if None in selection:
                            return self._derive_tree(sym, cursor, sub_trees)
                        else:
                            self.handle_error(sym, cursor, sub_trees, tok, selection, tokstream)
                except KeyError:
                    if None in selection:
                        return self._derive_tree(sym, cursor, sub_trees)
                    else:
                        self.handle_error(sym, cursor, sub_trees, tok, selection, tokstream)
            selection = cursor.move(s, tok)
            if self.debug:
                self._dbg_info(selection, tok, (sym, s), "shift")
            try:
                tok = tokstream.next()
            except StopIteration:
                tok = None
        return sub_trees

if __name__ == '__main__':
    # 1.         44040 function calls (42424 primitive calls) in 0.451 CPU seconds
    # 2.         37880 function calls (36264 primitive calls) in 0.402 CPU seconds
    # 3.         31672 function calls (30056 primitive calls) in 0.354 CPU seconds
    # 4.         30985 function calls (29369 primitive calls) in 0.348 CPU seconds
    # 5.         30985 function calls (29369 primitive calls) in 0.346 CPU seconds
    # 6.         24048 function calls (23209 primitive calls) in 0.284 CPU seconds
    import profile as profile
    import time
    import EasyExtend.langlets.p4d.langlet as langlet
    from EasyExtend.util.path import path
    import EasyExtend.eecommon
    source = open(path(langlet.__file__).dirname().joinpath("tests","p4d_football_big.p4d")).read()
    #source = open(path(langlet.__file__).dirname().joinpath("tests","cst.py")).read()
    from   EasyExtend.trail.nfaparser import TokenStream, NFAParser
    parser = NFAParser(langlet)
    stream = EasyExtend.eecommon.tokenize(langlet, source)
    profile.run("EasyExtend.eecommon.tokenize(langlet, source)")
    stream = TokenStream(stream)
    profile.run("parser.parse(stream)")



