
'''
nfagen module. Used to create characterstic finite automata for grammar rules
'''

from EasyExtend.csttools import find_node, find_all

import EasyExtend.langlets.grammar_langlet.langlet as grammar_langlet
symbol = grammar_langlet.symbol
token  = grammar_langlet.token


__all__ = ["create_lex_nfa", "create_parse_nfa", "GrammarError"]

class GrammarError(Exception):
    def __init__(self, symbols, typ):
        self.symbols = symbols
        self.typ = typ

    def __str__(self):
        S = tuple(self.symbols)[0]
        if self.typ == "Token":
            return "Unreferenced symbol `%s` in Token file detected."%S
        else:
            return "Unreferenced symbol `%s` in Grammar file detected."%S

def get_nid(item, langlet):
    nid = langlet.symbol.__dict__.get(item)
    if nid is not None:
        return nid
    nid = langlet.token.token_map.get(item)
    if nid is not None:
        return nid
    else:
        return item

class GrammarRule(list):
    def __init__(self, lst):
        list.__init__(self, lst)
        self.rule_text = ""

class FlatRule(object):
    """
    Class used to turn EBNF grammar rules into list description using numerical identifiers
    of symbols and tokens. ::

       Example 1:

            single_input: NEWLINE | simple_stmt | compound_stmt NEWLINE

                           =====>

            ['|', ['1', 4], ['1', 267], ['1', 291, 4]]

       Here '1' represents the multiplicty of the whole box. Other multiplicities
       are '*', '+' and '?' according to the EBNF notations.

       Example 2:

           test: and_test ('or' and_test)* | lambdef

                          =====>

           ['|', ['1', 299, ['*', 'or', 299]], ['1', 314]]

    """
    def __init__(self, langlet, nid = -1):
        self.nid   = nid
        self.ALT   = []
        self.ITEMS = []
        self.multiplicity = '1'
        self.langlet = langlet


    def create(self, node):
        alternatives = find_all(node, symbol.ALT, level = 1)
        if len(alternatives)>1:
            for alt in alternatives:
                rule = FlatRule(langlet = self.langlet)
                rule.ITEMS = self.from_alt(alt)
                self.ALT.append(rule)
        else:
            self.ITEMS = self.from_alt(alternatives[0])

    def from_alt(self, node):
        items = []
        for ITEM in find_all(node, symbol.ITEM, level = 1):
            ATOM = find_node(ITEM, symbol.ATOM, level = 1)
            if ATOM:
                rule = FlatRule(langlet = self.langlet)
                if find_node(ITEM, token.PLUS, level = 1):
                    rule.multiplicity = '+'
                if find_node(ITEM, token.STAR, level = 1):
                    rule.multiplicity = '*'
                rhs = find_node(ATOM, symbol.RHS)
                if rhs:
                    rule.create(rhs)
                else:
                    sym_name = find_node(ATOM, token.NAME)
                    if sym_name:
                        rule.nid = self.get_nid(sym_name[1], self.langlet)
                    else:
                        tok = find_node(ATOM, token.STRING)
                        tok_name = tok[1][1:-1]
                        self.strings.add(tok_name)
                        rule.nid = self.get_nid(tok_name, self.langlet)
                items.append(rule)
            else:
                rule = FlatRule(langlet = self.langlet)
                rule.multiplicity = '?'
                rule.create(find_node(ITEM, symbol.RHS))
                items.append(rule)
        return items

    def left_factor(self, alt_rule):
        return alt_rule
        if not alt_rule[0] == '|':
            return alt_rule
        rules = alt_rule[1:]
        typ = rules[0][0]
        prefix = []
        i = 0
        while True:
            try:
                c = rules[0][i]
                for r in rules[1:]:
                    if r[i]!=c:
                        break
                else:
                    i+=1
                    prefix.append(c)
                    continue
                break
            except IndexError:
                break
        if len(prefix)>1:
            m = prefix[0]
            prefix.append(['|']+[[m]+r[len(prefix):] for r in rules])
            return prefix
        else:
            return alt_rule

    def flatten(self):
        if self.ALT:
            _expect = ["|"]
            for r in self.ALT:
                if r.nid>=0:
                    _expect.append(r.nid)
                else:
                    _expect.append(r.flatten())
            if self.multiplicity == '+':
                return ['1',_expect, ['*', _expect]]
            else:
                return _expect
        elif self.ITEMS:
            _expect = [self.multiplicity]
            for r in self.ITEMS:
                if r.nid>=0:
                    if r.multiplicity == '*':
                        _expect.append(['*', r.nid])
                    elif r.multiplicity == '+':
                        _expect.append(r.nid)
                        _expect.append(['*',r.nid])
                    else:
                        _expect.append(r.nid)
                else:
                    flat = r.flatten()
                    if flat[0] == '+':
                        _expect.append(['1']+flat[1:])
                        _expect.append(['*']+flat[1:])
                    elif r.multiplicity in ('?','*') and r.multiplicity!=flat[0]:
                        _expect.append([r.multiplicity,flat])
                    else:
                        _expect.append(flat)
            if _expect[0] == '1' and len(_expect) == 2 and isinstance(_expect[1], list):
                return _expect[1]
            return _expect

    def maybe_elimination(self, stream):
        pass
        # ToDo: reduction of x,['?',y,...,z] -> ['|',['1',x],['1',x,y,...,z]]


    @classmethod
    def generate_all(cls, langlet, typ = "Grammar"):
        '''
        function used to create simple rule table from EBNF grammar description.

        @param langlet: optional langlet module. When available Grammar of langlet is parsed.
            Otherwise Pythons Grammar is used as a default.
        @return: dictionary of rules.
        '''
        if typ == 'Grammar':
            langlet_token  = langlet.parse_token
            langlet_symbol = langlet.parse_symbol
        else:
            langlet_symbol = langlet.lex_symbol
            langlet_token  = langlet.lex_token

        def get_nid(self, item, langlet):
            #if hasattr(langlet_symbol, "token_map"):
            #    nid = langlet_symbol.token_map.get(item) or langlet_symbol.__dict__.get(item)
            #else:
            nid = langlet_symbol.__dict__.get(item)
            if nid is not None:
                return nid
            nid = langlet_token.token_map.get(item) or langlet_token.__dict__.get(item)
            if nid is not None:
                return nid
            else:
                cls.unknown.add(item)
                return item

        grammar = grammar_langlet.load_grammar_cst(langlet, typ)
        FlatRule.get_nid = get_nid
        FlatRule.strings = set()
        FlatRule.unknown = set()
        FlatRule.typ = typ


        rules = {}
        for r in find_all(grammar, symbol.RULE):
            rhs = find_node(r, symbol.RHS)
            rule_name = find_node(r, token.NAME)[1]
            nid = get_nid(None, rule_name, langlet)
            # print "NID", nid
            rule = FlatRule(langlet, nid)
            rule.create(rhs)
            gr = GrammarRule(rule.flatten())
            gr.rule_text = grammar_langlet.unparse(r)
            assert isinstance(nid, int), (nid, type(nid))
            rules[nid] = gr
        return rules


class RuleIter(object):
    def __init__(self, lst):
        self.lst   = lst
        self.entries   = []
        self.endpoints = []
        self.repeat_target = True

    def initials(self):
        '''
        Finds one or more start symbols of a rule.
        '''
        visited = set()
        def _initials(rule):
            visited.add(rule)
            if isinstance(rule, SequenceRule):
                if rule.entries[0] not in visited:
                    return _initials(rule.entries[0])
            elif isinstance(rule, ConstRule):
                return [rule]
            elif isinstance(rule, AltRule):
                return sum([_initials(entry) for entry in rule.entries],[])
            elif isinstance(rule, (MaybeRule, RepeatRule)):
                _inits = _initials(rule.entries[0])
                return _inits
        return _initials(self)


    def finals(self):
        '''
        Finds one or more endpoints of rule.
        '''
        def _finals(rule):
            if isinstance(rule, (MaybeRule, SequenceRule, RepeatRule)):
                return _finals(rule.entries[-1])
            elif isinstance(rule, ConstRule):
                return [rule]
            elif isinstance(rule, AltRule):
                return sum([_finals(entry) for entry in rule.entries],[])
            return []
        return _finals(self)

    def chain(self):
        '''
        Method used to represent rule.
        '''
        if len(self.entries) == 0:
            if self.endpoints:
                return str(self) +"->[" + ";".join([e.chain() for e in self.endpoints]) +"]"
            else:
                return str(self)
        elif isinstance(self, AltRule):
            return "AltRule("+"|".join([entry.chain() for entry in self.entries])+")"
        else:
            return type(self).__name__+"("+self.entries[0].chain()+")"

    def __str__(self):
        return str(self.lst)

    def __repr__(self):
        return str(self.lst)


ConstRule    = type("ConstRule",(RuleIter,),{})
SequenceRule = type("SequenceRule",(RuleIter,),{})
AltRule      = type("AltRule",(RuleIter,),{})
RepeatRule   = type("RepeatRule",(RuleIter,),{})
MaybeRule    = type("MaybeRule",(RuleIter,),{})
BeginRule    = type("BeginRule",(ConstRule,),{})
EmptyRule    = type("EmptyRule",(ConstRule,),{})
EmptyRuleInstance = EmptyRule((None,'-'))

class BeginRule(ConstRule):
    '''
    For testpurposes...
    '''
    def __repr__(self):
        return "BEGIN"

    def __str__(self):
        return "BEGIN"



class RuleGen(object):
    def __init__(self, rule_descr):
        self.cnt   = 0
        self.rules = {'1': SequenceRule, '?': MaybeRule, '|': AltRule, '*': RepeatRule}
        self.rule  = self.produce(rule_descr)
        #self.linking(self.rule)

    def produce(self, rule_descr):
        if isinstance(rule_descr, (int, str)):
            self.cnt+=1
            return ConstRule((rule_descr, self.cnt))
        else:
            Rule = self.rules.get(rule_descr[0])
            r = Rule(rule_descr)
            for item in rule_descr[1:]:
                r.entries.append(self.produce(item))
            r.endpoints = r.finals()
            return r

    def is_mandatory(self, r):
        if isinstance(r, ConstRule):
            return True
        elif isinstance(r, AltRule):
            for sub in r.entries:
                if not self.is_mandatory(sub):
                    return False
            else:
                return True
        elif isinstance(r, SequenceRule):
            for sub in r.entries:
                if self.is_mandatory(sub):
                    return True
            else:
                return False
        elif isinstance(r, (MaybeRule, RepeatRule)):
            return False

    def linking(self, rule, terminate = True):
        if rule == EmptyRuleInstance:
            return
        if terminate:
            for e in rule.endpoints:
                e.endpoints.append(EmptyRuleInstance)
        if len(rule.entries) == 0:   # nothing to link
            return
        if isinstance(rule, AltRule):
            if not self.is_mandatory(rule.entries[0]) and terminate:
                rule.entries.insert(0, EmptyRuleInstance)
            for entry in rule.entries:
                self.linking(entry, False)
            return
        if not self.is_mandatory(rule.entries[0]):# and terminate:
            rule.entries.insert(0, BeginRule((None,'+')))
        if len(rule.entries) == 1:
            self.linking(rule.entries[0], False)
            return
        else:
            final = rule.entries[-1]
            connect = [final]
            self.linking(final, False)
            for item in rule.entries[:-1][::-1]:
                fin  = []
                fin += item.endpoints
                for c in connect:
                    if fin:
                        for f in fin:
                            f.endpoints.append(c)
                    else:
                        item.endpoints.append(c)
                    if not self.is_mandatory(c):
                        for e in c.endpoints:
                            if e in item.endpoints:
                                continue
                            for f in e.endpoints:
                                if f not in item.endpoints:
                                    if isinstance(item, RepeatRule):
                                        f.repeat_target = False
                                        item.endpoints.append(f)
                                    else:
                                        item.endpoints.append(f)
                                    for g in fin:
                                        g.endpoints.append(f)
                self.linking(item, False)
                if self.is_mandatory(item):
                    connect = [item]
                else:
                    connect.append(item)

    def cycles(self, rule):
        '''
        Used for prepratation of RepeatRules. Place RepeatRule in it's own endpoints unless the endpoint is None
        '''
        visited = set()
        def _cycles(rule):
            if id(rule) in visited:
                return
            visited.add(id(rule))
            if isinstance(rule, RepeatRule):
                for entry in rule.entries[::-1]:
                    entry.endpoints.append(rule)
                    if self.is_mandatory(entry):
                        break
                for e in rule.endpoints:
                    if e != EmptyRuleInstance and e.repeat_target:
                        if rule not in e.endpoints:
                            e.endpoints.append(rule)
            if isinstance(rule, AltRule):
                for entry in rule.entries:
                    _cycles(entry)
            elif rule.entries:
                _cycles(rule.entries[0])
            else:
                for e in rule.endpoints:
                    _cycles(e)
        return _cycles(rule)


class NFAGenerator:
    def __init__(self, langlet, typ = "parse"):
        self.langlet = langlet
        self.typ = typ
        self.nfas = {}

    def create_all(self):
        '''
        Creates all nfas for an existing langlet.
        '''
        rules = FlatRule.generate_all(self.langlet, self.typ)
        for r, descr in rules.items():
            rg = RuleGen(descr)
            rg.linking(rg.rule)
            rg.cycles(rg.rule)
            nfa = self.create_nfa(rg.rule, (r,0))
            self.nfas[r] = [descr, descr.rule_text.strip(), (r,0,r), nfa]
        return self.nfas

    def create_nfa(self, rule, init):
        nfa = {}
        def step(rule, state):
            selection = rule.initials()
            trans = nfa.get(state,[])
            trans+=[s.lst for s in selection]
            nfa[state] = trans
            for s in selection:
                if s.lst == (None, '-'):
                    continue
                if not nfa.get(s.lst):
                    for e in s.endpoints:
                        step(e, s.lst)
        step(rule, init)
        if isinstance(rule, (RepeatRule, MaybeRule)):
            nfa[init].append((None,'-'))
        self.substitute(nfa)
        return self.extend_nfa(nfa, init[0])

    def extend_nfa(self, nfa, r):
        '''
        If r is the nid of a rule, then modify each label (a,b) to (a,b,r)
        '''
        init = (r,)
        extended_nfa = {}
        for s, follow in nfa.items():
            extended_nfa[s+init] = [f+init for f in follow]
        return extended_nfa


    def substitute(self, nfa):
        '''
        Substitute (None,'+') by the rhs of the rule.
        '''
        begin = nfa.get((None,'+'))
        #if begin and (None, '+') in begin:
        #    begin.remove((None, '+'))
        if begin:
            del nfa[(None,'+')]
        for k, rhs in nfa.items():
            if (None,'+') in rhs:
                rhs.remove((None,'+'))
                nfa[k] = list(set(begin+rhs))
            else:
                nfa[k] = list(set(rhs))


def create_lex_nfa(langlet, warnings = (), recreate = False, fullexpansion = True):
    return create_nfa(langlet, warnings, recreate, "lex_nfa", fullexpansion)

def create_parse_nfa(langlet, warnings = (), recreate = False, fullexpansion = True):
    return create_nfa(langlet, warnings, recreate, "parse_nfa", fullexpansion)

def create_nfa(langlet, warnings = (), recreate = False, typ = "parse_nfa", fullexpansion = True):
    from EasyExtend.util.path import path
    parser_type = "Grammar" if typ == "parse_nfa" else "Token"
    nfagenerator = NFAGenerator(langlet, parser_type)
    nfas = nfagenerator.create_all()
    S = FlatRule.unknown - FlatRule.strings
    if S:
        raise GrammarError(S, FlatRule.typ)
    import pprint
    import nfadatagen
    nfadatagen = nfadatagen.NFADataGenerator.new(langlet, parser_type, rules = nfas)
    try:
        nfadatagen.create_all()
    except NonSelectableError, e:
        v = e.value
        name = nfadatagen.node_name(v, langlet)
        e.value = "Error in grammar. No rule <%s:%s> found."%(name, v)
        raise
    #import time
    #a = time.time()

    print "Start NFA expansions..."
    nfadatagen.expand_all(fullexpansion)
    k = len(nfadatagen.nfadata.expansion_target)
    if k == 1:
        print "1 NFA expanded."
    else:
        print "%d NFAs expanded."%k

    #print "EXPANSION TIME", time.time() - a
    #print "do-stmt-size", len(nfadatagen.nfadata.nfas[9556][3])
    nfadatagen.check_rightexpand()
    # nfadatagen.expand_transitions()

    nfadata = nfadatagen.nfadata
    try:
        fPyTrans = open(getattr(langlet, typ).__file__.replace("pyc", "py"),"w")
    except AttributeError:
        fPyTrans = open(path(langlet.__file__).dirname().joinpath(typ+".py"),"w")
    print >> fPyTrans, "# %s" % ("_" * 70)
    print >> fPyTrans, "# This was automatically generated by nfagen.py."
    print >> fPyTrans, "# Hack at your own risk."
    print >> fPyTrans
    print >> fPyTrans, "# LANGLET OFFSET\n"
    print >> fPyTrans, "LANGLET_OFFSET = %s"%langlet.LANGLET_OFFSET
    print >> fPyTrans
    print >> fPyTrans, "# trail NFAs:"
    print >> fPyTrans
    print >> fPyTrans, "nfas = "+pprint.pformat(nfadata.nfas)
    print >> fPyTrans
    print >> fPyTrans, "# expansion targets:"
    print >> fPyTrans
    print >> fPyTrans, "expanded  = "+pprint.pformat(nfadata.expansion_target, width=120)
    print >> fPyTrans
    print >> fPyTrans, "# reachables:"
    print >> fPyTrans
    print >> fPyTrans, "reachables = "+pprint.pformat(nfadata.reachables, width=120)
    print >> fPyTrans
    print >> fPyTrans, "# terminals:"
    print >> fPyTrans
    print >> fPyTrans, "terminals  = "+pprint.pformat(nfadata.terminals, width=120)
    print >> fPyTrans
    print >> fPyTrans, "# terminal ancestors:"
    print >> fPyTrans
    print >> fPyTrans, "ancestors  = "+pprint.pformat(nfadata.ancestors, width=120)
    print >> fPyTrans
    print >> fPyTrans, "# symbols of:"
    print >> fPyTrans
    print >> fPyTrans, "symbols_of  = "+pprint.pformat(nfadata.symbols_of, width=120)
    print >> fPyTrans
    print >> fPyTrans, "# keywords:"
    print >> fPyTrans
    print >> fPyTrans, "keywords  = "+pprint.pformat(nfadata.keywords, width=120)

    print >> fPyTrans
    if hasattr(nfadata, "pseudo_token"):
        print >> fPyTrans, "# pseudo_token:"
        print >> fPyTrans
        print >> fPyTrans, "pseudo_token  = "+pprint.pformat(nfadata.pseudo_token, width=80)
        print >> fPyTrans
    fPyTrans.close()

    reload(getattr(langlet, typ))
    print "*** Modify %s ***"%fPyTrans.name
    return nfadata.nfas


def check(rule_descr):
    T = NFAGenerator()
    rg = RuleGen(rule_descr)
    rg.linking(rg.rule)
    rg.cycles(rg.rule)
    transitions = T.create_nfa(rg.rule, (200,0))
    import pprint
    pprint.pprint(transitions)



