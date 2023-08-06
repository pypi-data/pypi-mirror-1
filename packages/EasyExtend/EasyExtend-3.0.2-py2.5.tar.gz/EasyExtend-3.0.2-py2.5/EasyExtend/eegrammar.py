from __future__ import with_statement
import EasyExtend
from EasyExtend.util.path import path
from EasyExtend.util import more_recent
import eeoptions
import pprint

class LineList:
    """
    Implements a readline-style interface to a string or list of lines.
    """
    def __init__ (self, s_or_l):
        self.index = 0
        if isinstance(s_or_l, list):
            self.lineList = s_or_l
        else:
            self.lineList = s_or_l.splitlines()

    def __iter__(self):
        return self

    def next(self):
        if self.index>=len(self.lineList):
            raise StopIteration
        return self()

    def __call__ (self):
        retVal = ''
        if self.index < len(self.lineList):
            retVal = self.lineList[self.index] + "\n"
            self.index += 1
        return retVal


class GrammarUpdater(object):
    def __init__(self, pth, options = {}):
        self.recreate    = options.get("build_nfa")
        self.pth_langlet = self.langlet_path(pth)
        self.offset      = self.read_offset()

    def langlet_path(self, pth):
        while pth:
            root = path(pth).dirname()
            if root.basename() == "langlets":
                return pth
            pth = root

    def read_offset(self):
        for line in open(self.pth_langlet.joinpath("conf.py")).readlines():
            if line.startswith("LANGLET_OFFSET"):
                return int(line.split("LANGLET_OFFSET = ")[1])

    def track_change(self):
        pth_gram_glob = self.global_grammar_path()
        pth_gram_ext  = self.grammar_ext_path()
        pth_sym       = self.symbol_path()
        pth_nfa       = self.nfa_path()

        if pth_gram_ext.isfile():
            if more_recent(pth_gram_glob, pth_nfa):
                return (pth_gram_ext, "global_ext")
            elif more_recent(pth_gram_ext, pth_nfa) or self.recreate or pth_sym.size<10:
                return (pth_gram_ext, "ext")
            else:
                return (None, False)
        else:
            pth_local_grammar = self.local_grammar_path()
            if pth_local_grammar.isfile():
                if self.recreate or more_recent(pth_local_grammar, pth_nfa) or pth_sym.size<10:
                    return (pth_local_grammar, "local")
                else:
                    return (None, False)

    def load_grammar(self):
        '''
        Function used to create ext-language specific grammarObjects that contain
        dfa parser tables. These grammar objects will be created using lifted nodes of the
        the used langlets.

        @note: The grammarObj will be replaced by a newer version if the Grammar file
            is more recent than the parsetable.py module.
        '''
        # is parsetable.py file module more recent than the Grammar file or small than return the
        # grammarObj immediately ...
        pth_grammar, typ = self.track_change()
        if typ is False:
            return False
        elif typ in ( "ext", "global_ext"):
            gram_lines = self._merge_ext(pth_grammar)
        else:
            lines = open(pth_grammar).readlines()
            gram_lines = LineList(lines)
            self.map_extended(self.create_rules(LineList(lines)))
        # create symbols
        with open(self.symbol_path(),"w") as f_symbol:
            self.map_symbols(f_symbol, gram_lines)
        return True

    def create_rules(self, lines):
        k = 1
        rule = ""
        rules = {}
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if line.find("#")>=0:
                single = 0
                double = 0
                for i,c in enumerate(line):
                    if c == '"':
                        single+=1
                    elif c == "'":
                        double+=1
                    elif c == '#':
                        if single%2==0 and double%2==0:
                            line = line[:i]
                            break
                if not line:
                    continue
            colidx = line.find(":")
            if colidx>=0:
                rule_name = line[:colidx]
                if not rule_name.split("_")[0].isalnum():
                    idx, rule_text = rules[rule]
                    rules[rule] = (idx, rule_text + " "+ line.strip())
                else:
                    rule = rule_name
                    rules[rule] = (k, line)
                    k+=1
            else:
                (idx, l) = rules[rule_name]
                rules[rule_name] = (idx, l+line)
        return rules

    def _merge_ext(self, f_ext):
        '''
        Create a new set of lines reading Grammar + Grammar.ext.
        If Grammar.ext contains a rule R of the same name as Grammar replace R of
        Grammar with R of Grammar.ext
        '''
        global_lines = open(self.global_grammar_path()).readlines()
        ext_lines    = open(f_ext).read().splitlines()
        global_rules = self.create_rules(global_lines)
        ext_rules    = self.create_rules(ext_lines)
        k = 1
        n = len(global_rules)
        for r, v in ext_rules.items():
            line, rule_def = v
            rule = global_rules.get(r)
            if rule:
                # overwrite existing rule
                global_rules[r] = (rule[0], rule_def)
            else:
                # new rule
                global_rules[r] = (n+k, rule_def)
                k+=1
        grammar = [line for (k,line) in sorted(global_rules.values())]
        self.map_extended(global_rules)
        self.write_merged_grammar(grammar)
        return LineList(grammar)


    def write_merged_grammar(self, grammar):
        with open(self.local_grammar_path(),"w") as G:
            for l in grammar:
                l = self.post_process_line(l)
                print >> G, l

    def map_symbols(self, f_symbol, gram_lines):
        '''
        Create new langlet specific xxx_symbol.py file.
        '''
        print >> f_symbol, "#  This file is automatically generated; please don't muck it up!"
        print >> f_symbol
        print >> f_symbol, "#--begin constants--"
        print >> f_symbol
        i = 0
        for line in gram_lines:
            if line and line[0] not in (' ','\t', '#'):
                NT = line.split(":")[0].strip()  # split rule name from rule
                if NT:
                    print >> f_symbol, "%s = %s"%(NT, self.offset+256+i)
                    i+=1

        print >> f_symbol
        print >> f_symbol, "#--end constants--"
        print >> f_symbol
        print >> f_symbol, "tok_name = sym_name = {}"
        print >> f_symbol, "for _name, _value in globals().items():"
        print >> f_symbol, "    if type(_value) is type(0):"
        print >> f_symbol, "        sym_name[_value] = _name\n"
        self._write_extended(f_symbol)

    def local_grammar_path(self):
        raise NotImplementedError

    def global_grammar_path(self):
        raise NotImplementedError

    def grammar_ext_path(self):
        raise NotImplementedError

    def symbol_path(self):
        raise NotImplementedError

    def nfa_path(self):
        raise NotImplementedError

    def map_extended(self, rules):
        raise NotImplementedError

    def post_process_line(self, line):
        raise NotImplementedError

    def _write_extended(self, f_symbol):
        raise NotImplementedError


class EEGrammar(GrammarUpdater, eeoptions.EEShow):
    '''
    Class used to handle creation / updates of Grammar + Grammar.ext specific files ::

            parse_symbol.py
            parse_nfa.py
    '''

    def local_grammar_path(self):
        return self.pth_langlet.joinpath("parsedef","Grammar")

    def grammar_ext_path(self):
        return self.pth_langlet.joinpath("parsedef","Grammar.ext")

    def global_grammar_path(self):
        return path(EasyExtend.__file__).dirname().joinpath("Grammar")

    def nfa_path(self):
        return self.pth_langlet.joinpath("parsedef","parse_nfa.py")

    def symbol_path(self):
        return self.pth_langlet.joinpath("parsedef","parse_symbol.py")

    def map_extended(self, rules):
        pass

    def post_process_line(self, line):
        return line

    def _write_extended(self, f_symbol):
        pass

class EETokenGrammar(GrammarUpdater, eeoptions.EEShow):
    '''
    Class used to handle creation / updates of Token + Token.ext specific files ::

            lex_symbol.py
            lex_nfa.py

    but also ::

            parse_token.py
    '''
    def local_grammar_path(self):
        return self.pth_langlet.joinpath("lexdef", "Token")

    def grammar_ext_path(self):
        return self.pth_langlet.joinpath("lexdef", "Token.ext")

    def global_grammar_path(self):
        return path(EasyExtend.__file__).dirname().joinpath("Token")

    def nfa_path(self):
        return self.pth_langlet.joinpath("lexdef","lex_nfa.py")

    def symbol_path(self):
        return self.pth_langlet.joinpath("lexdef","lex_symbol.py")


    def map_extended(self, rules):
        self.token_map = {}
        for i,rule in sorted(rules.values()):
            rhs = rule[rule.index(":")+1:].strip()
            r = "".join(rhs.split())
            r = "".join(r.split("'"))
            self.token_map[r] = 255+i+self.offset

    def post_process_line(self, line):
        '''
        Rules in Token + Token.ext may contain strings of the kind ::

            R: A B 'xyz' C

        The strings will be splitted and the resulting rule looks like ::

            R: A B 'x' 'y' 'z' C
        '''
        fragments = []
        n = len(line)
        i = 0
        while i<n:
            k1 = line.find("'",i)
            k2 = line.find('"',i)
            if k1 == k2 == -1:
                fragments.append(line[i:])
                break
            k = min(k for k in (k1,k2) if k>0)
            quote = "'" if k== k1 else '"'
            l = line.find(quote, k+1)
            if l==-1:
                raise ValueError("line = '%s', index = %d"%(line, k))
            if l>2+k:
                fragments.append(line[i:k])
                if line[k+1] == '\\':
                    fragments.append(quote+line[k+1:l]+quote+" ")
                else:
                    for c in line[k+1:l]:
                        fragments.append(quote+c+quote+" ")
            else:
                fragments.append(line[i:l+1])
            i = l+1
        return "".join(fragments)


    def _write_extended(self, f_symbol):
        print >> f_symbol
        print >> f_symbol, "token_map = "+pprint.pformat(self.token_map, width=120)

    def load_lex_symbol(self):
        l = self.pth_langlet.split(self.pth_langlet.sep)
        return __import__(str(".".join(l[l.index("langlets"):]+["lexdef", "lex_symbol"])), globals(), locals(), ["EasyExtend"], -1)

    def map_to_parse_token(self):
        '''
        The files lex_symbol.py and parse_token.py contain the same symbols but use different node ids.

        The general rule is ::

            Nid(lex_symbol.S) == Nid(parse_token.S) - 256

        Since lex_symbol.py is created first this function creates parse_token.py from lex_symbol.py.
        '''
        tok_path   = self.pth_langlet.joinpath("parsedef", "parse_token.py")
        lex_symbol = self.load_lex_symbol()
        with open(tok_path, "w") as fPToken:
            print >> fPToken, "#  This file is automatically generated; please don't muck it up!"
            print >> fPToken
            print >> fPToken, "#--begin constants--"
            print >> fPToken
            symbols = sorted((val, key) for (key, val) in lex_symbol.__dict__.items() if isinstance(val, int))
            for val, key in symbols:
                # print "%s = %s"%(key, val - 256)
                print >> fPToken, "%s = %s"%(key, val - 256)

            print >> fPToken
            print >> fPToken, "#--end constants--"
            print >> fPToken
            print >> fPToken, "tok_name = sym_name = {}"
            print >> fPToken, "for _name, _value in globals().items():"
            print >> fPToken, "    if type(_value) is type(0):"
            print >> fPToken, "        sym_name[_value] = _name\n"

            new_tok_map = {}
            for k, v in lex_symbol.token_map.items():
                new_tok_map[k] = v - 256
            print >> fPToken
            print >> fPToken, "token_map = "+pprint.pformat(new_tok_map, width=120)
            print >> fPToken
            fPToken.close()

    def load_grammar(self):
        if super(EETokenGrammar, self).load_grammar():
            self.map_to_parse_token()
            return True
        return False



if __name__ == '__main__':
    EasyExtend.new_langlet("zero")
