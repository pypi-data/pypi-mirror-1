import EasyExtend
import EasyExtend.util
from EasyExtend.cst import py_symbol, py_token
import pprint
import warnings
import copy
import sys

__DEBUG__ = True

SKIP = '.'

class LeftRecursionWarning(Warning):
    def __init__(self,*args, **kwd):
        super(LeftRecursionWarning, self).__init__(*args, **kwd)
        self.rules = []

class NeedsMoreExpansionWarning(Warning): pass
class RightExpansionWarning(Warning): pass


warnings.simplefilter("always",LeftRecursionWarning)
warnings.simplefilter("always",NeedsMoreExpansionWarning)
warnings.simplefilter("always",RightExpansionWarning)


def node_name(item, langlet):
    try:
        return langlet.lex_symbol.sym_name[item]
    except KeyError:
        pass
    try:
        return langlet.lex_token.tok_name[item]
    except KeyError:
        pass
    return "UNKNOWN"


@EasyExtend.util.psyco_optimized
def combinations(l):
    if l == ():
        return ((),)
    else:
        return [(x,)+y for x in l[0] for y in combinations(l[1:]) if (y and x<y[0] or y==())]

def lower_triangle(lst):
    '''
    Converts list of integers ( or ordered values of another type ) into a list of pairs belonging
    to a lower triangle matrix.

    Example:

        >>> L = [1, 2, 3]
        >>> lower_triangle(L)
        [(1,2),(1,3),(2,3)]

    There is no sorting involved so when you keep a rotated list the result will differ:

        >>> L = [2, 1, 3]
        >>> lower_triangle(L)
        [(2,3),(1,2),(1,3)]

    Doubles will not be erased:

        >>> L = [3, 1, 3]
        >>> lower_triangle(L)
        [(1,3),(1,3)]

    '''
    _lst = list(lst)
    L = (_lst,_lst)
    return combinations(L)

def symbols(lst):
    res = set()
    for s in lst[1:]:
        if isinstance(s, list):
            res.update(symbols(s))
        else:
            res.add(s)
    return res


class NFATraceNode:
    '''
    Atomic node. Used to store one label and its parent for a multitrace.
    '''
    def __init__(self, parent, label, tok = None):
        self.parent = parent
        self.label  = label
        self.token  = tok

    def __repr__(self):
        return "<%s -> %s>"%(self.parent, self.label)

def is_token(nid):
    try:
        return nid % 512 < 256
    except (TypeError, ValueError):
        return True

class NFAMultiTrace:
    '''
    Datastructure used to hold a tree which is organized like a multi-stack.

    The growth is coordinated. Several nodes are pushed into a new_state box. On commit()
    previous traces become parents of the new states and those will be the heads of the
    new traces. Some traces might not be followed anymore when iterating through a NFA. When
    traces get stuck they get deleted. Reaching a terminal (None, '-') will eliminate all
    traces but one. This trace can be formed into the seeked parse tree.
    '''
    def __init__(self, start):
        # print "DEBUG - start", start
        self.start  = start
        self.traces = {start: NFATraceNode(None, start)}
        self.new_traces = {}
        self.b_lex = False

    def set_token(self, tok):
        # print "DEBUG - set token", tok
        for label, nfanode in self.traces.items():
            if label[0] in tok[:2]:
                nfanode.token = list(tok[:-1])

    def terminate(self):
        '''
        Close all traces. Used to derive trace in error cases.
        '''
        for parent in self.traces:
            self.update(parent, (None, '-', parent[-1]))
        self.commit()


    def flatten(self):
        '''
        Unwind multitrace from a single endpoint into a flat list.
        For token labels replace index by token.
        '''
        lst = []
        for label in self.traces:
            if label[0] is None:
                node = self.traces[label]   # select a single endpoint
                break                       # no ambiguities are handled here
        else:
            raise RuntimeError("Incomplete Trace. No exit symbol found.")
        while node:
            label = node.label
            if label[0] is None:
                lst.insert(0, label )
                node = node.parent
                continue
            if node.token:   # replace label index by token
                #print "DEBUG - label", label
                #print "DEBUG - token", node.token
                lst.insert(0, (label[0], node.token, label[-1]))
            else:
                lst.insert(0, label )
            node = node.parent
        return lst


    def update(self, parent, new_label):
        '''
        Step 1:
            build links of the kind:

                    new_label |-- <parent>

            <parent> is a NFATraceNode with parent as an endpoint.

            Depending on the number of new labels there might be many such pairs. In case
            of skipped nodes long chains can grow

                    new_label |-- <lk> -- <lk-1> ... <l2> -- <l1> -- <parent>

            Many instances of these new traces can be build
        '''
        # print "DEBUG - update", parent, new_label
        trNode = self.new_traces.get(parent, self.traces.get(parent))
        if trNode:
            self.new_traces[new_label] = NFATraceNode(trNode, new_label)
        else:
            raise RuntimeError("Can't connect label %s with NFAMultiTrace datastructure"%(parent,))

    def commit(self):
        '''
        Step 2:
             Build process for traces is closed. Newly built traces replace the old ones
             for the next round.
        '''
        self.traces = {}
        self.traces.update(self.new_traces)
        self.new_traces = {}
        #print "DEBUG - traces", len(self.traces.keys())


    def derive_tree(self, sub_trees):
        '''
        Creates parse tree from label list. sub_trees replace corresponding node ids if available.
        '''
        def mk_tree(labels, trees):
            root  = labels[0][0]
            trees[root] = [root]
            for label in labels[1:]:
                nid  = label[0]
                link = label[-1]
                if nid is None:
                    return trees[root]
                sub = (sub_trees[0] if sub_trees else None)
                t   = is_token(nid)
                if t:
                    T = trees.get(link, [link])
                    T.append(label[1])
                elif nid == link:
                    if nid == root:
                        trees[root].append(nid)
                    elif sub and sub[0] == nid:
                        T = trees[nid]
                        T.append(sub)
                        sub_trees.pop(0)
                else:
                    T = trees.get(link, [link])
                    N = trees.get(nid)
                    if N:
                        T.append(N)
                        del trees[nid]
                    else:
                        if sub and sub[0] == nid:
                            T.append(sub)
                            sub_trees.pop(0)
                trees[T[0]] = T
            else:
                if len(labels)>1:
                    raise ValueError("Exit label `(None, ..)` missing in: %s"%labels)
                else:
                    raise ValueError("No trace available")
        tree = mk_tree(self.flatten(), {})
        # print "----  TREE ----", tree

        k = 0
        # print "DEBUG - subtrees", sub_trees
        if sub_trees:
            for j, nid in enumerate(tree[1:]):
                if not is_token(nid, self.b_lex):
                    for i, sub in enumerate(sub_trees[k:]):
                        if sub[0] == nid:
                            tree[1+j] = sub
                            k += i+1
                            break
        # print "DEBUG - tree", tree
        return tree


class NFACursor:
    def __init__(self, nfatable, nid):
        self.nfa = nfatable[nid]
        self.transitions = self.nfa[3]
        self.state   = set([self.nfa[2]])
        self.mtrace  = NFAMultiTrace(self.nfa[2])
        self.terminated = False

    def derive_tree(self, sub_trees):
        return self.mtrace.derive_tree(sub_trees)

    def terminate(self):
        return self.mtrace.terminate()

    def set_parsemode(self, mode):
        self.mtrace.b_lex = mode

    def set_token(self, tok):
        self.mtrace.set_token(tok)

    def set_nonterminal(self, nt):
        self.mtrace.set_nonterminal(nt)

    def move(self, nid):
        if nid is None:
            if self.terminated:
                raise NonSelectableError(str(nid))
            self.mtrace.update(None, self.state[0])
            self.terminated = True
            return []
        stateset = set()
        for state in self.state:
            if state[0] == nid:
                stateset.update(self.get_next_state(state))
        self.state = stateset
        self.mtrace.commit()
        selection = list(set(s[0] for s in stateset))
        # print "DEBUG - state", self.state
        # print "DEBUG - selection", selection
        return selection

    def get_next_state(self, state):
        next_states = set()
        labels = self.transitions[state]
        delayed = None
        for label in labels:
            if label == state:
                delayed = state
                continue
            self.mtrace.update(state, label)
            if label[1] == SKIP:
                next_states.update(self.get_next_state(label))
            else:
                next_states.add(label)
        if delayed:
            self.mtrace.update(delayed, delayed)
            if delayed[1] == SKIP:
                next_states.update(self.get_next_state(delayed))
            else:
                next_states.add(delayed)
        return next_states


class NFATracer:
    def __init__(self, table):
        self.nfa_table  = table
        self.state      = None   # can be shared by more than one node with same nid
        self.selectable = []
        self.nfa = {}
        self.embedded = []

    def clone(self):
        rt = self.__class__(self.nfa_table)
        rt.selectable = self.selectable[:]
        rt.state = self.state[:]
        rt.nfa = self.nfa
        return rt

    def get_nid(self, state):
        return state[0][0]

    def initialize(self, nid):
        self.nfa   = self.nfa_table[nid][3]
        self.state = [self.nfa_table[nid][2]]

    def select(self, nid, *other):
        self.embedded = []
        try:
            if self.state is None:
                self.initialize(nid)
                return self._next()
            if nid is None:
                raise NonSelectableError(str(nid))
            self.state = [s for s in self.selectable if s[0] == nid]
            for n in other:
                self.state += [s for s in self.selectable if s[0] == n]
            if self.state:
                return self._next()
            raise NonSelectableError(nid)
        except KeyError:
            raise NonSelectableError(nid)

    move = select

    def _selection(self):
        return tuple(set(s[0] for s in self.selectable))

    def _get_next_state(self, state, visited):
        embedded = []
        states = set()
        if len(state) == 1:
            if state[0][0] is None:
                states.add(state[0])
                return states
            trans = self.nfa[state[0]]
            for item in trans:
                if item[1] == SKIP:
                    embedded.append(item)
                    if item in visited:
                        continue
                    visited.add(item)
                    sub_states,sub_embedd = self._get_next_state([item], visited)
                    states.update(sub_states)
                    if sub_embedd:
                        embedded.append(sub_embedd)
                else:
                    states.add(item)
        else:
            for S in state:
                if S in visited:
                    continue
                visited.add(S)
                sub_states,sub_embedd =self._get_next_state([S], visited)
                states.update(sub_states)
                if sub_embedd:
                    embedded.append(sub_embedd)
        return states, embedded

    def _next(self):
        visited = set()
        states, self.embedded = self._get_next_state(self.state, visited)
        self.selectable  = tuple(states)
        return self._selection()


class NFATracerDetailed(NFATracer):
    def get_nid(self, state):
        return state[0]

    def _selection(self):
        return self.selectable

class NFATracerUnexpanded(NFATracer):
    def __init__(self, nfa_mod):
        self.expanded   = nfa_mod.expanded
        self.nfa_table  = nfa_mod.nfas
        self.state      = None   # can be shared by more than one node with same nid
        self.selectable = []
        self.nfa = {}
        self.embedded = []

    def get_trans(self, nid):
        return self.nfa[state[0]]

    def initialize(self, nid):
        if nid in self.expanded:
            self.nfa   = self.expanded[nid][3]
            self.state = [self.expanded[nid][2]]
        else:
            self.nfa   = self.nfa_table[nid][3]
            self.state = [self.nfa_table[nid][2]]


class Vertex(object):
    diagrams = {}
    def __init__(self, state):
        self.state  = state
        self.nid    = state[0]
        self.connected = set()
        self.selection = []

    def __repr__(self):
        return str(self.state)+"<Vertex>"

class SyntaxGraph(object):
    def __init__(self, start, rules):
        self.rules    = rules
        self.start    = Vertex((start,0))
        self.vertices = {(start,0): self.start}

        for s in rules[start][3]:
            self.vertices[s] = Vertex(s)

    def create_connections(self):
        visited = set()

        def set_connections(rt, vertex):
            selection = rt.select(vertex.nid)
            vertex.selection = tuple(set(s[0] for s in selection))
            for s in selection:
                if s[0] is None:
                    vertex.connected.add(None)
                    continue
                else:
                    s_vertex = self.vertices[s]
                    vertex.connected.add(s_vertex)
                if s in visited:
                    continue
                visited.add(s)
                cloned = rt.clone()
                set_connections(cloned, s_vertex)

        rtd = NFATracerDetailed(self.rules)
        set_connections(rtd, self.start)

        for a,v in self.vertices.items():
            v.connected = tuple(v.connected)


class Cursor(object):
    def __init__(self, graph, state = []):
        self.graph = graph
        self.state = state

    def clone(self):
        c = self.__class__(self.graph)
        c.state = list(self.state)
        return c

    def move(self, nid, *other):
        if not self.state:
            start = self.graph.start
            if start.nid!=nid:
                raise NonSelectableError(str(nid))
            self.state = (start,)
            return start.selection
        next = set()
        for s in self.state:
            for v in s.connected:
                if v:
                    if v.nid == nid or v.nid in other:
                        next.add(v)
        if not next:
            raise NonSelectableError(str(nid))
        self.state = tuple(next)
        if len(self.state)>1:
            selection = set()
            for s in self.state:
                selection.update(s.selection)
            return tuple(selection)
        else:
            return self.state[0].selection

class NFAData:
    def __init__(self):
       self.nfas       = {}
       self.keywords   = []
       self.reachables = {}
       self.first_set  = {}
       self.traces     = {}
       self.used_symbols = set()
       self.terminals    = set()
       self.nonterminals = set()
       self.symbols_of   = {}
       self.expansion_target = {}


class NFADataGenerator(object):
    @classmethod
    def new(self, langlet, parser_type, transitions = None, rules = None):
        if parser_type == "Token":
            return NFADataGenerator_TrailLexer(langlet, transitions = transitions, rules = rules)
        else:
            return NFADataGenerator_TrailParser(langlet, transitions = transitions, rules = rules)

    def graph(self, nt):
        rtd = NFATracerDetailed(self.rules)
        return rtd.graph(nt)

    def create_all(self):
        self._collect_symbols()
        self._keywords()
        self._terminals()
        self._first_set(self.start_symbol)
        self._reachables()
        return self.nfadata

    def _collect_symbols(self):
        self.used_symbols = set()
        for k,v in self.rules.items():
            S = symbols(v[0])
            self.nfadata.used_symbols.update(S)
            self.nfadata.symbols_of[k] = S

    def _keywords(self):
        if not self.nfadata.used_symbols:
            self._collect_symbols()
        self.nfadata.keywords = set(s for s in list(self.nfadata.used_symbols) if isinstance(s, str))

    def _terminals(self):
        for s in list(self.nfadata.used_symbols):
            if s in self.nfadata.keywords:
                self.nfadata.terminals.add(s)
            elif s%512<256:
                self.nfadata.terminals.add(s)
            else:
                self.nfadata.nonterminals.add(s)

    def reduced_nfa(self, start):
        '''
        Computes a nfa while skipping any skippable labels.
        '''
        reduced = {}
        tracer    = NFATracerDetailed(self.nfadata.nfas)
        visited   = set()
        def trace(tracer, label, visited):
            selection = tracer.select(label[0])
            reduced[label] = selection
            visited.add(label)
            for s in selection:
                if s[0] is not None and s not in visited:
                    trace(tracer.clone(), s, visited)
        trace(tracer, start, visited)
        return reduced

    def _last_set(self):
        '''
        The EndTrans(A) = { A_t1, ..., A_tk } is the set of "end transitions" of A i.e. those transitions
        that contain (None,'-',A). The LastSet(A) of A is defined recursively by EndTrans(A) together with
        the EndTrans of each element in EndTrans(A). Often LastSet(A) is just {None}. In those cases we
        do not care.

        This function computes the LastSets of all nodes in the NFA set.
        '''
        def end_trans(r):
            etrans = set()
            nfa = self.nfadata.nfas[r]
            start = nfa[2]
            for t in self.reduced_nfa(start).values():
                if (None, '-', r) in t:
                    for label in t:
                        if label[0] is not None:
                            etrans.add(label[0])
            return etrans

        last_sets = {}
        visited = set()
        def compute_last_set(r):
            visited.add(r)
            S = last_sets.get(r)
            if S:
                return S
            else:
                etrans = end_trans(r)
                for t in tuple(etrans):
                    if not self.is_token(t):
                        if t not in visited:
                            etrans.update(compute_last_set(t))
                        else:
                            etrans.update(last_sets.get(t,set()))
                last_sets[r] = etrans
            return etrans

        last_sets = {}
        for r in self.nfadata.nfas:
            if last_sets.get(r) is None:
                compute_last_set(r)
        for r in last_sets:
            S = last_sets[r]
            for A in self.nfadata.reachables[r]:
                if not self.is_token(A):
                    S.update(last_sets[A])
        return last_sets

    def _first_set(self, state):
        rt = NFATracer(self.rules)
        try:
            selection = [s for s in rt.select(state) if s]
            self.nfadata.first_set[state] = selection
            for s in selection:
                if not self.nfadata.first_set.get(s) and self.rules.get(s):
                    self._first_set(s)
        except Exception:
            pass

    def span(self):
        def exhaust(nt):
            rtd = NFATracerDetailed(self.rules)
            visited = set()
            symbols = set()

            def get_selections(rt, state):
                tree = [state]
                selection = rt.select(state)
                for s in selection:
                    if s in visited or s[0] is None:
                        continue
                    visited.add(s)
                    symbols.add(s[0])
                    cloned = rt.clone()
                    tree.append(get_selections(cloned, s[0]))
                return tree

            tree = get_selections(rtd, nt)
            return tree, symbols

        spanned = {}
        for nt in list(self.nfadata.nonterminals):
            tree, symbols = exhaust(nt)
            flt = self.flatten(tree)
            if not isinstance(flt[0], list):
                flt = [flt]
            spanned[nt] = (symbols, flt)
        return spanned

    def cyclefree_traces(self):
        cfree_traces = {}
        spanned = self.span()
        # pprint.pprint(spanned)
        for r, (sym, lst) in spanned.items():
            cfree_traces[r] = lst
        return cfree_traces


    def flatten(self,lst):
        if not isinstance(lst, list) or len(lst)==1:
            return lst
        else:
            flst = []
            for item in lst:
                fl = self.flatten(item)
                if isinstance(fl, list) and isinstance(fl[0], list):
                    flst+=fl
                else:
                    flst.append(fl)
            res  = [[lst[0]]+item for item in flst[1:]]
            if len(res) == 1:
                return res[0]
            else:
                return res

    def _reachables(self):
        def get_reachables(state):
            reach = self.nfadata.reachables.get(state)
            if reach:
                return reach
            selection = [s for s in NFATracer(self.rules).select(state) if s!=None]
            self.nfadata.reachables[state] = set(selection)
            for s in selection:
                if self.is_token(s):
                    if isinstance(s, str):
                        self.nfadata.keywords.add(s)
                    continue
                self.nfadata.reachables[state].update(get_reachables(s))
            return self.nfadata.reachables[state]
        for r in self.rules:
            get_reachables(r)


class NFADataGenerator_TrailParser(NFADataGenerator):
    def __init__(self, langlet, transitions = None, rules = None):
        assert transitions or rules
        self.start_symbol = langlet.symbol.file_input
        if rules:
            self.rules = rules
        else:
            self.rules = transitions.nfas
        self.langlet   = langlet
        self.nfadata = NFAData()
        self.nfadata.nfas = self.rules
        self.cnt = 0

    def is_token(self, s):
        return s in self.nfadata.terminals

    def node_name(self, item):
        return self.langlet.parse_symbol.sym_name.get(item,"")+self.langlet.parse_token.tok_name.get(item,"")

    def _get_follow_sets(self, start):
        '''
        returns all follow sets containing at least two elements
        '''
        follow = []
        for T in self.reduced_nfa(start).values():
            K = [label for label in T if label[0] is not None]
            if len(K)>1:
                follow.append(K)
        return follow

    def redux(self, label):
        if isinstance(label[1], int):
            return label
        else:
            return (label[0], label[1][1:], label[2])

    def check_embedded(self, label, rule, embedded):
        if (label, rule) in embedded:
            return False
        if (self.redux(label), rule) in embedded:
            nid_A = label[0]
            A = self.nfadata.nfas[nid_A]
            R_NAME = A[1].split(":")[0]
            Z = self.nfadata.nfas[rule]
            lineno = sys._getframe(0).f_lineno +1

            warnings.warn_explicit('no expansion of `%s` possible in rule\n\t\t `%s`!\n'%(R_NAME, Z[1]), ExpansionWarning, "nfatools.py", lineno)
            return False
        return True

    def expand_all(self):
        visited = set()
        self.state_shift = 100
        self.labels = set()
        for r in self.nfadata.nfas:
            if r not in visited:
                self.expand(r, visited)

        # TODO : this is an implementation wart. Avoid this completely. Check whether it is stable
        #        and how it behaves in the presence of left recursion
        not_fully_expanded = []
        for r in self.nfadata.nfas:
            if self.check_expanded(self.nfadata, r):
                not_fully_expanded.append(r)
                self.expand(r, set())
                self.check_expanded(self.nfadata, r, print_warning = True)

    def shift_state(self, nfa):
        shift = self.state_shift
        Z = {}
        for key, follow in nfa.items():
            new_follow = []
            for label in follow:
                if label[1] == SKIP:
                    new_follow.append((label[0],SKIP,label[2]+shift,label[3]))
                elif label[1] == '-':
                    new_follow.append(label)
                else:
                    new_follow.append((label[0],label[1]+shift,label[2]))
            if key[1] == SKIP:
                Z[(key[0],SKIP,key[2]+shift,key[3])] = new_follow
            else:
                Z[(key[0],key[1]+shift,key[2])] = new_follow
        self.state_shift+=10
        return Z

    def expand(self, rule = 0, visited = set()):
        if not rule:
            rule = self.start_symbol

        def maybe_expand(r):
            if r and r not in visited and not self.is_token (r):
                self.expand(r, visited)

        expanded = set()
        embedded = set()
        start = self.nfadata.nfas[rule][2]
        nfa = self.nfadata.nfas[rule][3]
        visited.add(rule)
        while True:
            k = 0
            follow_sets = self._get_follow_sets(start)
            #if __DEBUG__:
            #    print "DEBUG - follow_sets", follow_sets
            for follow in follow_sets:
                follow = list(follow)
                selectable = [s[0] for s in follow if s]
                pairs = lower_triangle( selectable )
                for A,B in pairs:
                    if (A,B) in expanded:
                        continue
                    elif self.is_token(A):
                        if self.is_token(B):
                            continue
                        elif A in self.nfadata.reachables[B]:
                            # print "INTERSECTION", A, B
                            for label in (label for label in follow if label[0] == B):
                                maybe_expand(label[0])
                                if not (label, rule) in embedded:
                                    self.embedd_nfa(label, rule)
                                embedded.add((label, rule))
                            expanded.add((A,B))
                            k+=1
                            break
                    elif self.is_token(B):
                        if B in self.nfadata.reachables[A]:
                            #print "INTERSECTION", A, B
                            for label in (label for label in follow if label[0] == A):
                                maybe_expand(label[0])
                                if not (label, rule) in embedded:
                                    self.embedd_nfa(label, rule)
                                embedded.add((label, rule))
                            expanded.add((A,B))
                            k+=1
                            break
                    elif self.nfadata.reachables[A] & self.nfadata.reachables[B]:
                        # print "INTERSECTION", A, B
                        for label in (label for label in follow if label[0] in (A,B)):
                            maybe_expand(label[0])
                            if not (label, rule) in embedded:
                                self.embedd_nfa(label, rule)
                            embedded.add((label, rule))
                        k+=1
                        expanded.add((A,B))
                        break
                    if k:
                        break
            if k == 0:
                break


    def shift_tridex(self, tridex, nfa):
        def new_label(label):
            if len(label) == 4:
                l2 = label[2]
                _tridex = tridex[:2]+(l2,) if isinstance(l2, int) else tridex[:2]+(l2[2],)
                return (label[0], label[1], _tridex, label[3])
            else:
                l1 = label[1]
                _tridex = tridex[:2]+(l1,) if isinstance(l1, int) else tridex[:2]+(l1[2],)
                return (label[0], _tridex, label[2])

        # pprint.pprint(tridex)
        # pprint.pprint(nfa)
        Z = {}
        for key, follow in nfa.items():
            new_follow = []
            for label in follow:
                if label[1] == '-':
                    new_follow.append(label)
                else:
                    new_follow.append(new_label(label))
            Z[new_label(key)] = new_follow
        self.shift_idx+=1
        return Z

    def embedd_nfa(self, label, at):
        # print "embedd_nfa(self, label: %s, at: %s)"%(label, at)
        nid_A = label[0]
        Z = self.nfadata.nfas[at]
        A = self.nfadata.nfas[nid_A]
        if label[0] == at:
            R_NAME = A[1].split(":")[0]
            lineno = sys._getframe(0).f_lineno +1

            warnings.warn_explicit('no expansion of `%s` possible in `%s`!'%(R_NAME, Z[1]), LeftRecursionWarning, "nfatools.py", lineno)
            return

        if not at in self.nfadata.expansion_target:
            self.nfadata.expansion_target[at] = copy.deepcopy(Z)
        start_A  = (A[2][0], self.state_shift, A[2][0]) # shift
        nfa_A    = self.shift_state(A[3])
        nfa_Z    = Z[3]
        follow_A = nfa_A[start_A]
        transit  = (label[0], SKIP )+label[1:]
        for key, follow in nfa_Z.items():
            if key == label:
                nfa_Z[transit] = follow
                del nfa_Z[label]
            try:
                k = follow.count(label)
                if k:
                    while k:
                        follow.remove(label)
                        k-=1
                    follow.extend(follow_A)
            except ValueError:
                pass
        for key, follow in nfa_A.items():
            for i,v in enumerate(follow):
                if v[0] == None:
                    new_follow = follow[:]
                    new_follow[i] = transit
                    nfa_Z[key] = new_follow
                    break
            else:
                if start_A == key:
                    continue
                nfa_Z[key] = follow


    def check_expanded(self, nfamodule, rule = None, print_warning = False):
        def check(label, tracer, visited, trace):
            labels = tracer.select(label[0])
            selection = [s[0] for s in labels]
            terminals = set([t for t in selection if (t is not None) and (isinstance(t, str) or t%512<256)])
            pairs = lower_triangle( [t for t in selection if t and isinstance(t, int) and t%512>=256 ] )
            for A,B in pairs:
                S = nfamodule.reachables.get(A, set())
                T = (tuple(terminals)[0] if len(terminals) == 1 else tuple(terminals))
                assert S & terminals == set(),  "FirstSet(%s) /\\ FirstSet(%s) != {} in %s\n"%(A, T, self.node_name(label[0]))
                assert nfamodule.reachables.get(B, set()) & terminals == set(), "FirstSet(%s) /\\ FirstSet(%s) != {} in %s\n"%(B, T, self.node_name(label[0]))
                assert S & nfamodule.reachables.get(B, set()) == set(), "FirstSet(%s) /\\ FirstSet(%s) != {} in %s\n"%(A, B, self.node_name(label[0]))
            for label in labels:
                if label[0] is not None and label not in visited:
                    visited.add(label)
                    subtracer = tracer.clone()
                    check(label, subtracer, visited, trace+[label[0]])

        for r, nfa in self.rules.items():
            if rule and r!=rule:
                continue
            visited = set()
            tracer = NFATracerDetailed(nfamodule.nfas)
            start = nfa[2]
            trace = [start[0]]
            try:
                check(start, tracer, visited, trace)
            except AssertionError, e:
                if print_warning:
                    lineno = sys._getframe(0).f_lineno +1

                    warnings.warn_explicit(e, NeedsMoreExpansionWarning, "nfatools.py", lineno)
                return True


    def check_rightexpand(self):
        last_sets = self._last_set()
        warned = set()

        def format_stream(T, k):
            stream = []
            for t in [t for t in T[:k+2]]:
                if isinstance(t, int):
                    stream.append(self.node_name(t))
                else:
                    stream.append("'"+t+"'")
            return stream[0]+': '+' '.join(stream[1:])

        for r, traces in self.cyclefree_traces().items():
            for T in traces:
                for i in range(1,len(T)-1):
                    A = T[i]
                    B = T[i+1]
                    if (r,A,B) in warned or A == B:
                        continue
                    if self.is_token(B):
                        if B in last_sets.get(A, set()):
                            warn_text = "LastSet(%s) /\\ set(`%s`) != {} in %s"%(self.node_name(A),B, format_stream(T,i))

                            warnings.warn_explicit(warn_text, RightExpansionWarning, "nfatools.py", sys._getframe(0).f_lineno-1)
                            warned.add((r,A,B))
                            break
                    else:
                        S = last_sets.get(A, set()) & self.nfadata.reachables.get(B, set())
                        if S:
                            warn_text = warn_text = "LastSet(%s) /\\ FirstSet(%s) != {} in %s"%(self.node_name(A),self.node_name(B),format_stream(T,i))

                            warnings.warn_explicit(warn_text, RightExpansionWarning, "nfatools.py", sys._getframe(0).f_lineno-1)
                            warned.add((r,A,B))
                            break


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#
#   NFADataGenerator_TrailLexer
#
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class PseudoTokenSet(dict):
    max_tid = 0
    def __init__(self, dct={}):
        dict.__init__(self, dct)

    def __setitem__(self, key, value):
        dict.__setitem__(self, key, value)
        PseudoTokenSet.max_tid = max(PseudoTokenSet.max_tid, key)

    def __repr__(self):
        d = {}
        for tid, pt in self.items():
            d[tid] = pt.litset
        return pprint.pformat(d)


class PseudoToken(object):
    def __init__(self, tid, litset, name = ""):
        if tid == -1:
            PseudoTokenSet.max_tid +=1
            self.tid = PseudoTokenSet.max_tid
        else:
            self.tid    = tid
        self.litset = litset
        self.name   = name

    def __repr__(self):
        return "<PT: %s , %-16s, %s>"%(self.tid, self.name, self.litset)


class NFADataGenerator_TrailLexer(NFADataGenerator_TrailParser):
    def __init__(self, langlet, transitions = None, rules = None):
        assert transitions or rules
        self.start_symbol = langlet.lex_symbol.token_input
        if rules:
            self.rules = rules
        else:
            self.rules = transitions.nfas
        self.langlet   = langlet
        self.nfadata = NFAData()
        self.nfadata.nfas = self.rules
        self.pseudo_token = PseudoTokenSet()
        self.initial_pseudo_token()
        #pprint.pprint(self.pseudo_token, width = 360)

    def is_token(self, s):
        return ( s in self.nfadata.terminals or \
                 s in self.pseudo_token )

    def node_name(self, item):
        return self.langlet.lex_symbol.sym_name.get(item,"")+self.langlet.lex_token.tok_name.get(item,"")

    def initial_pseudo_token(self):
        offset = self.langlet.LANGLET_OFFSET
        for name, val in self.langlet.lex_token.litset.__dict__.items():
            if not name.startswith("LS_"):
                continue
            tid = self.langlet.lex_token.token_map[name[3:]]
            self.pseudo_token[tid] = PseudoToken(tid, val, name[3:])

    def expand_all(self):
        visited = set()
        self.state_shift = 100
        for r in self.nfadata.nfas:
            if r not in visited:
                self.expand(r, visited)
        self.check_expanded(self.nfadata, print_warning = True)
        self.nfadata.pseudo_token = self.pseudo_token

    def expand_all(self):
        super(NFADataGenerator_TrailLexer, self).expand_all()
        self.nfadata.pseudo_token = self.pseudo_token


    def expand(self, rule = 0, visited = set()):
        if not rule:
            rule = self.start_symbol
        start = self.nfadata.nfas[rule][2]
        nfa = self.nfadata.nfas[rule][3]
        self.expand_nt(rule, start, nfa, visited)
        self.expand_pseudo_token(rule, start, nfa)

    def expand_pseudo_token(self, rule, start, nfa):
        # print "EXPAND_PSEUDO", rule, start
        more = True
        while more:
            more = False
            kicked = []
            reduced_nfa = self.reduced_nfa(start)
            transitions = reduced_nfa.values()
            for trans in transitions:
                follow = [f for f in trans if f[0]!=None and f not in kicked]
                if len(follow)<2:
                    continue
                pseudo_token = self.split(follow)
                for label, sets in pseudo_token.items():
                    nids = []
                    for S in sets:
                        if len(S) == 1:
                            nids.append(list(S)[0])
                            continue
                        for P in self.pseudo_token.values():
                            if P.litset == S:
                                nids.append(P.tid)
                                break
                        else:
                            pt = PseudoToken(-1, S)
                            self.pseudo_token[pt.tid] = pt
                            nids.append(pt.tid)
                            # print "NEW pt", pt
                    label_follow = nfa[label]
                    del nfa[label]
                    kicked.append(label)
                    new_labels = []
                    for n in nids:
                        i = 0
                        new_label = (n, label[1]+i, label[-1])
                        while nfa.get(new_label):
                            i+=1
                            new_label = (n, label[1]+i, label[-1])
                        nfa[new_label] = label_follow
                        new_labels.append(new_label)
                    for trans in nfa.values():
                        if label in trans:
                            trans.remove(label)
                            trans+=new_labels
                    more = True

    def split(self, labels):
        pt_list, np_list = [],[]
        for label in labels:
            if label[0] in self.pseudo_token:
                pt_list.append(label)
            else:
                np_list.append(label)
        res = []
        pseudo_token = {}
        for i,A in enumerate(pt_list):
            LS_A = self.pseudo_token[A[0]].litset
            for B in pt_list[1+i:]:
                if A[0]!=B[0]:
                    LS_B = self.pseudo_token[B[0]].litset
                    K = LS_A & LS_B
                    if K:
                        if K!=LS_A:
                            pt = pseudo_token.get(A,[])
                            pt.append(K)
                            pseudo_token[A] = pt
                        if K!=LS_B:
                            pt = pseudo_token.get(B,[])
                            pt.append(K)
                            pseudo_token[B] = pt
                        # print "SPLIT", A,B,K
            for t in np_list:
                if t[0] in LS_A:
                    pt = pseudo_token.get(A,[])
                    pt.append(set(t[0]))
                    pseudo_token[A] = pt
        if pseudo_token:
            i = 1
            for A, sets in pseudo_token.items():
                R = [self.pseudo_token[A[0]].litset]
                for S in sets:
                    K = []
                    for T in R:
                        for r in T & S, T-S, S-T:
                            if r and r not in K:
                                K.append(r)
                    R = K
                pseudo_token[A] = R
        return pseudo_token


    def expand_nt(self, rule, start, nfa, visited):

        def maybe_expand(r):
            if r and r not in visited and not self.is_token (r):
                self.expand(r, visited)

        def intersect(R_A, R_B):
            for t in R_A:
                if t in self.pseudo_token:
                    LS_t = self.pseudo_token[t].litset
                    for u in R_B:
                        if u in self.pseudo_token:
                            if LS_t & self.pseudo_token[u].litset:
                                return True
                        else:
                            if u in LS_t:
                                return True
            return False

        def try_expansion(nids, follow, rule, embedded):
            for label in (label for label in follow if label[0] in nids):
                maybe_expand(label[0])
                if not (label, rule) in embedded:
                    self.embedd_nfa(label, rule)
                embedded.add((label, rule))
            return True

        visited.add(rule)
        expanded = set()
        embedded = set()
        while True:
            more = False
            #pprint.pprint(nfa)
            follow_sets = self._get_follow_sets(start)
            #if __DEBUG__:
            #    print "DEBUG - follow_sets", follow_sets
            for follow in follow_sets:
                follow = list(follow)
                selectable = [s[0] for s in follow if s]
                pairs = lower_triangle( selectable )
                for A,B in pairs:
                    rc = 0
                    if (A,B) in expanded:
                        continue
                    elif A in self.nfadata.terminals and not A in self.pseudo_token:
                        #elif self.is_token(A) and not A in self.pseudo_token:
                        if self.is_token(B):
                            pass
                        elif A in self.nfadata.reachables[B]:
                            rc = try_expansion([B], follow, rule, embedded)
                    elif self.is_token(B) and not B in self.pseudo_token:
                        if A in self.pseudo_token:
                            continue
                        elif B in self.nfadata.reachables[A]:
                            rc =try_expansion([A], follow, rule, embedded)
                    elif A in self.pseudo_token:
                        if B in self.pseudo_token:
                            continue
                        R_B = self.nfadata.reachables[B]
                        if intersect([A],R_B):
                            rc = try_expansion([B], follow, rule, embedded)
                    elif B in self.pseudo_token:
                        R_A = self.nfadata.reachables[A]
                        if intersect([B],R_A):
                            rc = try_expansion([A], follow, rule, embedded)
                    elif self.nfadata.reachables[A] & self.nfadata.reachables[B]:
                        rc = try_expansion([A,B], follow, rule, embedded)
                    else:
                        R_A = self.nfadata.reachables[A]
                        R_B = self.nfadata.reachables[B]
                        if intersect(R_A, R_B) or intersect(R_B, R_A):
                            rc = try_expansion([A,B], follow, rule, embedded)
                    if rc:
                        expanded.add((A,B))
                        more = True
            if not more:
                #pprint.pprint(nfa)
                break


    def embedd_nfa(self, label, at):
        # print "EMBEDD", label, "at", at
        nid_A = label[0]
        Z = self.nfadata.nfas[at]
        A = self.nfadata.nfas[nid_A]
        if label[0] == at:
            R_NAME = A[1].split(":")[0]
            lineno = sys._getframe(0).f_lineno +1

            warnings.warn_explicit('no expansion of `%s` possible in:\n\t\t`%s`!'%(R_NAME, Z[1]), LeftRecursionWarning, "nfatools.py", lineno)
            return

        if not at in self.nfadata.expansion_target:
            self.nfadata.expansion_target[at] = copy.deepcopy(Z)

        start_A  = (A[2][0], self.state_shift, A[2][0]) # shift
        nfa_A    = self.shift_state(A[3])
        nfa_Z    = Z[3]
        follow_A = nfa_A[start_A]
        transit  = (label[0], SKIP )+label[1:]
        for key, follow in nfa_Z.items():
            if key == label:
                nfa_Z[transit] = follow
                del nfa_Z[label]
            try:
                k = follow.count(label)
                if k:
                    while k:
                        follow.remove(label)
                        k-=1
                    follow.extend(follow_A)
            except ValueError:
                pass
        for key, follow in nfa_A.items():
            for i,v in enumerate(follow):
                if v[0] == None:
                    new_follow = follow[:]
                    new_follow[i] = transit
                    nfa_Z[key] = new_follow
                    break
            else:
                if start_A == key:
                    continue
                nfa_Z[key] = follow


def check_grammar(langlet, typ):
    if typ == "Token":
        nfadata = NFADataGenerator.new(langlet, "Token", langlet.lex_nfa)
    else:
        nfadata = NFADataGenerator.new(langlet, "Parser", langlet.parse_nfa)
    nfadata.create_all()
    nfadata.expand_all()
    nfadata.check_rightexpand()

def nfa2dot(nfa, langlet):
    '''
    Create dot diagram
    '''
    start = nfa[2]
    transitions = nfa[3]
    nodes = []
    nodes.append('    nodeNone[label = "{None|-|%s}"];'%start[0])

    def Node(label):
        if len(label) == 3:
            return '    node%d[label = "{%s|{%s|%s|%s}}"];'%(label[1], node_name(label[0],langlet),label[0],label[1],label[2])
        else:
            return '    node%d[label = "{%s|{%s|.|%s|%s}}", color = green];'%(label[2], node_name(label[0],langlet),label[0],label[2],label[3])

    def Arrows(label):
        form   = "    node%s -> node%s;"
        idx = (label[2] if label[1] == SKIP else label[1])
        arrows = []
        for f in transitions[label]:
            if f[0] is None:
                arrows.append(form%(idx,"None"))
            else:
                idx2 = (f[2] if f[1] == SKIP else f[1])
                arrows.append(form%(idx,idx2))
        return "\n".join(arrows)

    arrows = []
    for label in transitions:
        nodes.append(Node(label))
        arrows.append(Arrows(label))
    graph = "digraph G {\n    node [shape = record,height=.1];\n"
    graph+="\n".join(nodes)+"\n"
    graph+="\n".join(arrows)
    graph+="\n}\n"
    return graph



def test1():
    import EasyExtend.langlets.zero.langlet as langlet
    import EasyExtend.langlets.zero.nfamodule as nfamodule
    ga = NFADataGenerator.new(langlet, nfamodule)
    ga.create_all()
    ga.expand_all()

def test2():
    import EasyExtend.langlets.new_parser.langlet as langlet
    import nfagen
    return nfagen.create_parse_nfa(langlet, recreate = True)

def test3():
    import EasyExtend.langlets.new_parser.nfamodule as nfamodule
    import pprint
    ga = NFADataGenerator.new(langlet, nfamodule)
    ga.create_all()
    ga.expand()
    '''
    pprint.pprint( ga.nfadata.symbols_of )
    pprint.pprint( ga.nfadata.overlap )
    ga._first_set(langlet.symbol.file_input)

    pprint.pprint( ga.nfadata.first_set )

    ga._reachables()
    print "\nv_arcs:\n"
    pprint.pprint(ga.v_arcs)

    print "\nreachables:\n"
    pprint.pprint(ga.nfadata.reachables)
    '''

    g = SyntaxGraph(langlet.LANGLET_OFFSET+263, ga.rules)
    g.create_connections()


def test4():
    import EasyExtend.langlets.new_parser.langlet as langlet
    import EasyExtend.langlets.new_parser.nfamodule as nfamodule
    ga = NFADataGenerator.new(langlet, nfamodule)
    ga.create_all()
    ga.expand_all()
    ga.check_expanded(ga.nfadata)
    return ga

def test5():
    import EasyExtend.langlets.zero.langlet as langlet
    import EasyExtend.langlets.zero.nfamodule as nfamodule
    ga = NFADataGenerator.new(langlet, nfamodule)
    ga.create_all()
    ga.expand_all()
    #reload(nfamodule)
    #ga.check_expanded(ga.nfadata)
    return ga

def test6():
    import EasyExtend.langlets.lexer.langlet as langlet
    import EasyExtend.langlets.lexer.nfamodule as nfamodule
    ga = NFADataGenerator.new(langlet, nfamodule)
    ga.create_all()
    ga.expand_all()
    return ga

def test7():
    import EasyExtend.langlets.expansion.langlet as langlet
    from EasyExtend.trail.nfagen import create_lex_nfa
    create_lex_nfa( langlet, recreate = True)

def check_last_set_zero():
    import EasyExtend.langlets.zero.langlet as langlet
    nfadata = NFADataGenerator.new(langlet, "Parser", langlet.parse_nfa)
    nfadata.create_all()
    nfadata.expand_all()
    #pprint.pprint(nfadata._last_set())
    #nfadata.check_rightexpand()
    pprint.pprint(nfadata.span())

def check_grammar(langlet, typ):
    if typ == "Token":
        nfadata = NFADataGenerator.new(langlet, "Token", langlet.lex_nfa)
    else:
        nfadata = NFADataGenerator.new(langlet, "Parser", langlet.parse_nfa)
    nfadata.create_all()
    nfadata.expand_all()
    nfadata.check_rightexpand()

def check_last_set_gallery():
    import EasyExtend.langlets.gallery.langlet as langlet
    check_grammar(langlet, "Token")
if __name__ == '__main__':
    check_last_set_zero()

