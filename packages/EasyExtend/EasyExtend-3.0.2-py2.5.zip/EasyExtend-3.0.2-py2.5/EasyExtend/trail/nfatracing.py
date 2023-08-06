import string
import pprint
import copy
import sys

SKIP = '.'

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

    def set_token(self, tok):
        #print "DEBUG - set token", tok
        for label in self.traces:
            if label[0] in tok[:2]:
                self.traces[label].token = tok

    def terminate(self):
        '''
        Close all traces. Used to derive trace in error cases.
        '''
        for parent in self.traces:
            self.update(parent, [[(None, '-', parent[-1])]])
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
                lst.append(label)
                node = node.parent
                continue
            link = label[-1]
            if link == '*':
                label[-1] = lst[-1][0]
            if node.token:   # replace label index by token
                #print "DEBUG - label", label
                #print "DEBUG - token", node.token
                lst.append((label[0], node.token, label[-1]))
            else:
                lst.append( label )
            node = node.parent
        return lst[::-1]

    def node_sequence(self):
        return self.flatten()

    def update(self, parent, follow):
        '''
        Step 1::
            build links of the kind:

                    new_label |-- <parent>

            <parent> is a NFATraceNode with parent as an endpoint.

            Depending on the number of new labels there might be many such pairs. In case
            of skipped nodes long chains can grow

                    new_label |-- <lk> -- <lk-1> ... <l2> -- <l1> -- <parent>

            Many instances of these new traces can be build
        Step 2::
            see L{commit}
        '''
        trRoot = self.traces.get(parent)
        new_traces = {}
        if trRoot is None:
            raise RuntimeError("Can't connect label %s with NFAMultiTrace datastructure"%(parent,))
        for S in follow:
            trNode = trRoot
            for label in S:
                trNode = NFATraceNode(trNode, label)
            self.new_traces[label] = trNode

    def commit(self):
        '''
        Step 2:
             Build process for traces is closed. Newly built traces replace the old ones
             for the next round.
        '''
        self.traces = self.new_traces
        self.new_traces = {}

    def mk_tree(self, labels, sub_trees):
        '''
        '''
        # print "-------   DEBUG  ------------"
        # print "-- labels --"
        # pprint.pprint(labels)
        # print "-- subtrees --"
        # pprint.pprint(sub_trees)
        # print
        root = labels[0][0]
        stack = []
        reminder = [root]
        for label in labels[1:]:
            if label[1] == SKIP:
                S = []
                reminder.pop()
                entry = stack.pop()
                while entry!=label[0]:
                    S.append(entry)
                    entry = stack.pop()
                S.append(entry)
                if label[-1]!=reminder[-1]:
                    stack.append(label[-1])
                    reminder.append(label[-1])
                stack.append(S[::-1])
                continue
            elif label[0] is None:
                if isinstance(stack[0], int):
                    return stack
                else:
                    return [label[-1]]+stack
            sub = (sub_trees[0] if sub_trees else None)
            label = list(label)
            link = label.pop()
            if link!=reminder[-1]:
                stack.append(link)
                reminder.append(link)
            if sub:
                if sub[0] == label[0] and isinstance(label[1], int):
                    sub_trees.pop(0)
                    stack.append(sub)
                elif isinstance(label[1], list):
                    stack.append(label[1])
                else:
                    stack.append(label)
            else:
                if isinstance(label[1], list):
                    stack.append(label[1])
                else:
                    stack.append(label)
        else:
            if len(labels)>1:
                raise ValueError("Exit label `(None, ..)` missing in: %s"%labels)
            else:
                raise ValueError("No trace available")


    def derive_tree(self, sub_trees):
        '''
        Creates parse tree from label list. sub_trees replace corresponding node ids if available.
        '''
        flattened = self.flatten()
        tree = self.mk_tree(flattened, sub_trees)
        return tree


class NFACursor:
    def __init__(self, nfatable, nid, cache):
        self.nfa = nfatable[nid]
        self.transitions = self.nfa[3]
        self.state   = set([self.nfa[2]])
        self.mtrace  = NFAMultiTrace(self.nfa[2])
        self.terminated = False
        self.cache = cache

    def derive_tree(self, sub_trees):
        return self.mtrace.derive_tree(sub_trees)

    def node_sequence(self):
        return self.mtrace.node_sequence()

    def set_token(self, tok):
        self.mtrace.set_token(tok)

    def terminate(self):
        self.mtrace.terminate()

    def set_nonterminal(self, nt):
        self.mtrace.set_nonterminal(nt)

    def move(self, nid, tok):
        if nid is None:
            if self.terminated:
                raise NonSelectableError(str(nid))
            self.mtrace.update(None, self.state)
            self.terminated = True
            return set()
        stateset = set()
        for state in self.state:
            if state[0] == nid:
                follow = self.get_next_state(state)
                for S in follow:
                    stateset.add(S[-1])
                self.mtrace.update(state, follow)
        self.mtrace.commit()
        self.state = stateset
        selection = set([s[0] for s in stateset])
        # print "DEBUG - state", self.state
        # print "DEBUG - selection 1", selection
        return selection

    def get_next_state(self, state):
        next_states = []
        labels = self.transitions[state]
        for label in labels:
            if label[1] == SKIP:
                for S in self.get_next_state(label):
                    next_states.append([label]+S)
            else:
                next_states.append([label])
        return next_states


class SimpleNFACursor(NFACursor):
    def __init__(self, nfatable, nid, cache):
        self.nfa = nfatable[nid]
        self.transitions = self.nfa[3]
        self.state   = set([self.nfa[2]])
        self.terminated = False
        self.cache = cache

    def move(self, nid, tok):
        if nid is None:
            if self.terminated:
                raise ValueError(str(nid))
            self.terminated = True
            return set()
        stateset = set()
        for state in self.state:
            if state[0] == nid:
                follow = self.get_next_state(state)
                for S in follow:
                    stateset.add(S[-1])
        self.state = stateset
        selection = set([s[0] for s in stateset])
        # print "DEBUG - state", self.state
        # print "DEBUG - selection 1", selection
        return selection

class NFATracer:
    def __init__(self, table):
        self.nfa_table  = table
        self.state      = None   # can be shared by more than one node with same nid
        self.selectable = []
        self.nfa = {}

    def clone(self):
        rt = self.__class__(self.nfa_table)
        rt.selectable = self.selectable[:]
        rt.state = self.state[:]
        rt.nfa = self.nfa
        return rt

    def get_nid(self, state):
        return state[0][0]

    def initialize(self, nid):
        nfa = self.nfa_table[nid]
        self.nfa   = nfa[3]
        self.state = [nfa[2]]

    def select(self, nid, *other):
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
        states = set()
        if len(state) == 1:
            if state[0][0] is None:
                states.add(state[0])
                return states
            trans = self.nfa[state[0]]
            for item in trans:
                if item[1] == SKIP:
                    if item in visited:
                        continue
                    visited.add(item)
                    sub_states = self._get_next_state([item], visited)
                    states.update(sub_states)
                else:
                    states.add(item)
        else:
            for S in state:
                if S in visited:
                    continue
                visited.add(S)
                sub_states = self._get_next_state([S], visited)
                states.update(sub_states)
        return states

    def _next(self):
        visited = set()
        states = self._get_next_state(self.state, visited)
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

use_cytrail = True

if use_cytrail:
    try:
        import cyTrail
        NFACursor = cyTrail.NFACursor
        SimpleNFACursor = cyTrail.SimpleNFACursor
        is_token = cyTrail.is_token
    except ImportError:
        use_cytrail = False



