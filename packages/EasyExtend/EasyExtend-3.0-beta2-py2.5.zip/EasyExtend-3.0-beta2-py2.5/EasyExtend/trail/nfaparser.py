import EasyExtend
import EasyExtend.util
from EasyExtend.cst import py_symbol, py_token
from EasyExtend.csttools import rule_error
from nfagen import*
from nfatools import*
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
        self.keywords   = langlet.parse_nfa.keywords
        self.symbols_of = langlet.parse_nfa.symbols_of
        self.expanded   = langlet.parse_nfa.expanded
        self.graphs = {}
        self.create_graph()

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

    def get_token_type(self, tok):
        if tok[0]%512 == 1 and tok[1] in self.keywords:
            return tok[1]
        return tok[0]
#
#
#  EESimpleParser  --  general form of NFA trace parser
#
#


class LL1Parser(EEParser):

    def parse(self, tokstream, start_symbol = None):
        if start_symbol is None:
            start_symbol = self.offset+257 # file_input
        tok = tokstream.next()
        return self._parse(tokstream, start_symbol, tok)

    @EasyExtend.util.psyco_optimized
    def _parse(self, tokstream, sym, tok):
        cursor = Cursor(self.graphs[sym])
        selection = cursor.move(sym)
        tree = [sym]
        while tok:
            if tok[1] in self.keywords:
                token_type = tok[1]
            else:
                token_type = tok[0]
            for s in selection:
                if s is not None:
                    try:
                        is_token = s%512<256
                    except TypeError:
                        is_token = True
                    if is_token:
                        if token_type == s:
                            tokstream.position+=1
                            tree.append(list(tok[:-1]))
                            break
                    elif token_type in self.reach.get(s,[]):
                        res = self._parse(tokstream, s, tok)
                        if res:
                            tree.append(res)
                            break
                        else:
                            continue
            else:
                if None in selection:
                    return tree
                else:
                    raise SyntaxError("Failed to parse input '%s' at (line %d , column %d)."%(tok[1],tok[2],tok[3][1]))
            selection = cursor.move(s)
            while 1:
                try:
                    tok = tokstream.tokstream[tokstream.position]
                    if tok[0]%512 in tokstream.ignored:
                        tokstream.position+=1
                    else:
                        break
                except IndexError:
                    break
        return tree

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
            return NFACursor(self.rules, sym)
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

    def handle_error(self, sym, cursor, sub_trees, tok, selection, tokstream):
        if sub_trees:
            cst = sub_trees
        else:
            try:
                cst = self._derive_tree(sym, cursor, sub_trees)
            except RuntimeError:
                cursor.terminate()
                cst = self._derive_tree(sym, cursor, sub_trees)
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
        error_line = "\n"+line+" "*(tok[3][0]+4)+"^"*(tok[3][1]-tok[3][0])+"\n"
        s = "Failed to parse input '%s' at (line %d , column %d). \n"%(word,tok[2],tok[3][1])
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
                print "token: %s -- rule: %s"%t
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
        return self._parse(tokstream, start_symbol, tok, None)

    @EasyExtend.util.psyco_optimized
    def _parse(self, tokstream, sym, tok, parent):
        cursor = self._new_cursor(sym)
        selection = cursor.move(sym)
        if self.debug:
            self._dbg_info(selection, tok, sym, "step")
        sub_trees = self._init_subtrees(sym)
        while tok:
            if tok[1] in self.keywords:
                token_type = tok[1]
            else:
                token_type = tok[0]
            for s in selection:
                if s is not None:
                    if self.is_token(s):
                        if token_type == s:
                            tokstream.shift_read_position()
                            self._store_token(sym, cursor, sub_trees, tok)
                            break
                    elif token_type in self.reach.get(s,[]):
                        res = self._parse(tokstream, s, tok, sym)
                        if res:
                            sub_trees.append(res)
                            break
                        else:
                            continue
            else:
                if None in selection:
                    return self._derive_tree(sym, cursor, sub_trees)
                else:
                    self.handle_error(sym, cursor, sub_trees, tok, selection, tokstream)
            selection = cursor.move(s)
            if self.debug:
                self._dbg_info(selection, tok, (sym, s), "shift")
            try:
                tok = tokstream.next()
            except StopIteration:
                tok = None
        return sub_trees


cst = None

def test_parser(typ, pprint = False, recreate = False, parser_type = "NFA"):
    from EasyExtend.eecompiler import EECompiler
    from EasyExtend.util.path import path


    def _NFAParser(LANGLET):
        eec = EECompiler(LANGLET)
        p = NFAParser(LANGLET)
        return p

    def parse(langlet, content, ignored = [54,53,56], maybe_ignored = []):
        global LANGLET
        LANGLET = langlet
        LANGLET.options["recreate"] = recreate
        eec = EECompiler(LANGLET)
        LANGLET.options["recreate"] = False
        tokenstream = TokenStream(eec.eetokenize_string(content), langlet.token.Ignore)
        if parser_type == "NFA":
            p = _NFAParser(LANGLET)
        else:
            p = _LL1Parser(LANGLET)
        def execute():
            #tokenstream = TokenStream(eec.eetokenize_string(content))
            tokenstream.position = 0
            global cst
            cst = p.parse(tokenstream)
            return cst
        return execute

    def testparser_parse():
        import EasyExtend.langlets.new_parser.langlet as LANGLET
        #content = "e+e-e+e-e+e-e+e-e+e-e+e-e+e-e+e-e+e-e+e-e+e-e+e-e+e-e+e-e+e"
        assert parse(LANGLET, 'f f t')() == [41729, [41730, [41732, [41736, [41737, [41473, 'f', 1]], [41738, [41473, 'f', 1], [41473, 't', 1]]]]], [41476, '\n', 1], [41472, '', 2]]
        assert parse(LANGLET, '2 2 3 3 4 5')() == [41729, [41730, [41746, [41747, [41474, '2', 1], [41747, [41474, '2', 1], [41474, '3', 1]], [41474, '3', 1]], [41748, [41474, '4', 1], [41474, '5', 1]]]], [41476, '\n', 1], [41472, '', 2]]
        assert parse(LANGLET, '0 0 0 1 1 1')() == [41729, [41730, [41743, [41744, [41474, '0', 1], [41744, [41474, '0', 1], [41744, [41474, '0', 1], [41474, '1', 1]], [41474, '1', 1]], [41474, '1', 1]]]], [41476, '\n', 1], [41472, '', 2]]
        return parse(LANGLET, 'f f f t')


    def newlanglet_parse():
        import EasyExtend.langlets.new_parser.langlet as LANGLET
        #content = "e+e-e+e-e+e-e+e-e+e-e+e-e+e-e+e-e+e-e+e-e+e-e+e-e+e-e+e-e+e"
        #content = 'f f f t'
        content = '2 2 3 3 4 4 5 5'
        #content = 'begin x y z end'
        #content = '(a)-(b)'
        #content = 'if ( E1 ) if ( E2 ) Stmt1 else if ( E3 ) Stmt2'
        #content = '_G9 A B C D E 9'

        return parse(LANGLET, content)

    def no_indent_parse():
        import EasyExtend.langlets.no_indent.langlet as LANGLET
        content = '''print 99'''
        '''
        def f():
            while True:
                pass
            end
         end
        '''

        return parse(LANGLET, content)

    def python_parse():
        import EasyExtend.langlets.zero.langlet as LANGLET
        #content = "e+e-e+e-e+e-e+e-e+e-e+e-e+e-e+e-e+e-e+e-e+e-e+e-e+e-e+e-e+e"
        #content  = "+(e+x)"
        #content = "x z y"
        #content = "f(x[1];)"
        #content = open("test_eeparser.py").read()

        import decimal
        dec_file = decimal.__file__
        if dec_file.endswith("c"):
            dec_file = dec_file[:-1]
        content = open(dec_file).read()

        #content = "from EasyExtend.foo.bar import*"
        #content = "a.b.c(d())"
        return parse(LANGLET, content)

    def cpp_parse():
        import EasyExtend.langlets.cpp.langlet as LANGLET
        #content = open(path(LANGLET.__file__).dirname().joinpath("langlettest\\test0.cpp")).read()
        #content = open(path(LANGLET.__file__).dirname().joinpath("langlettest\\test1.cpp")).read()
        #content = open(path(LANGLET.__file__).dirname().joinpath("langlettest\\test2.cpp")).read()
        #content = open(path(LANGLET.__file__).dirname().joinpath("langlettest\\test3.cpp")).read()
        #content = open(path(LANGLET.__file__).dirname().joinpath("langlettest\\test4.cpp")).read()
        #content = open(path(LANGLET.__file__).dirname().joinpath("langlettest\\test5.cpp")).read()
        #content = open(path(LANGLET.__file__).dirname().joinpath("langlettest\\test6.cpp")).read()
        content = open(path(LANGLET.__file__).dirname().joinpath("langlettest\\test7.cpp")).read()
        #content = open(path(LANGLET.__file__).dirname().joinpath("langlettest\\test8.cpp")).read()
        content = open(path(LANGLET.__file__).dirname().joinpath("langlettest\\stl_vector.h")).read()
        #content = 'extern "C" const int foo(int*& x){ \nbool blubb;}'
        #content = 'extern "C" EE_API const int main(){};'
        #content  = "e+x;"
        #content = "tparse.setASTFactory(&factory);"
        return parse(LANGLET, content, [4,5,6,53,54])

    if typ == "new_parser":
        return newlanglet_parse()
    elif typ == "python":
        return python_parse()
    elif typ == "cpp":
        return cpp_parse()
    elif typ == "testparser":
        return testparser_parse()
    elif typ == "no_indent":
        return no_indent_parse()

def test_python():
    import profile
    #__DEBUG__ = True
    __DEBUG__ = False
    p = test_parser("python") #, parser_type = "Simple")
    #p = test_parser("new_parser", parser_type = "NFA")
    #p = test_parser("no_indent", parser_type = "NFA")
    #p = test_parser("te")
    #profile.run("p()")
    #f()
    #cst = cst.tocst()
    #import profile
    import time
    a = time.time()
    cst = p()
    #profile.run("p()")
    print time.time()-a
    #print cst
    '''
    try:
        LANGLET.pprint(cst)
    except TypeError:
        LANGLET.pprint(cst.tocst())
    '''

    #print LANGLET.unparse(cst)
if __name__ == '__main__':
    ""
    #test_python()

