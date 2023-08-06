# URL:     http://www.fiber-space.de
# Author:  Kay Schluehr <easyextend@fiber-space.de>
# Date:    10 May 2006

import sys
#import EasyExtend
from EasyExtend.util.path import path
import EasyExtend.util
from csttools import*

__all__ = ["Transformer", "transform", "transform_dbg"]


def transform(f):
    '''
    Decorator for all cst transfoormation handlers.
    '''
    f.cst_transformer = True
    return f


def t_dbg(spec, cond = None, **kwd):
    '''
    Decorator used to display and check properties of input and output nodes
    that are passed into a node handler.

    Arguments::
        spec    --  specifier string. A specifier string is a list of command specifiers
                    e.g. 'ni no co gc'. Each command spec is only two letters long.

                    Commands can be chained arbitrarily with or without demlimiters.
                    If you use delimiters use whitespace, colons, commas or semicolons.

        cond    --  predicate. If cond predicate is available commands will only be executed when the
                    input data passed the cond filter. cond has the signature cond(node, **locals).


        kwd     --  dictionary containing actions for commands.


    Commands::
        ni   --  display plain node (input)
        no   --  display plain node(s) (output)
        ci   --  display input CST
        co   --  display output CSTs
        cv   --  CST validation test
        so   --  unparsed python source output
        si   --  unparsed python source input
        sn   --  unparsed python source of input node after
                 transformation. Used when input node is modified.
        r1   --  check that result is a single node
        r>   --  check that result is a list of nodes
        r=   --  check that result node ids equals input node id
        r!   --  check that result node ids not equals input node id
        fi   --  arbitrary test function of one argument
                 executed on node input
        fo   --  arbitrary test function of one argument
                 executed on node list output

    Use::

        @transform_dbg("ni cv r1")
        def foo(self, node):
            ...

        @transform_dbg("r>soco")
        def bar(self, node):
            ...

        def raises(ln):
            if ln>1:
                raise ValueError("Only one output argument expected")

        @transform_dbg("r1,co", 'r1' = raises)
        def bar(self, node):
            ...
    '''
    def action(specifier, node, **kwd):
        f = kwd.get(specifier)
        if f:
            f(node, **kwd)

    def transform(f):
        name = f.__name__

        def call_dbg(self, node, **kwd):
            assert isinstance(node, list), type(node)
            assert node, "node == []"
            assert isinstance(node[0], int), type(node[0])
            if cond:
                if not cond(node, **kwd):
                    return f(self, node, **kwd)
            n_id = id(node)%100
            if 'fi' in spec:
                action('fi', node, **kwd)
            if 'ni' in spec:
                print "[ni -- plain node (input) -- %s:%02d>\n"%(name, n_id)
                print node
                action('ni', node, **kwd)
                print "<ni -- plain node (input)-- %s:%02d]\n"%(name, n_id)
            if 'si' in spec:
                print "[si -- python source (input) -- %s:%02d>\n"%(name, n_id)
                print self.langlet.unparse(node)
                action('si', node, **kwd)
                print "<si -- python source (input) -- %s:%02d]\n"%(name, n_id)
            if 'ci' in spec:
                print "[ci -- cst (input) -- %s:%02d>\n"%(name, n_id)
                self.langlet.pprint(node)
                action('ci', node, **kwd)
                print "<ci -- cst (input) -- %s:%02d]\n"%(name, n_id)

            res = f(self, node, **kwd)

            if 'sn' in spec:
                print "[sn -- python source (input node -- after trans) -- %s:%02d>\n"%(name, n_id)
                print self.langlet.unparse(node)
                action('sn', node, **kwd)
                print "<sn -- python source (input node -- after trans) -- %s:%02d]\n"%(name, n_id)
            if res:
                assert isinstance(res, (list, tuple)), type(res)
                if isinstance(res[0], int):
                    rlist = [res]
                else:
                    rlist = res
                if 'fo' in spec:
                    action('fo', rlist, **kwd)
                if 'no' in spec:
                    print "[no -- plain node (output) -- %s:%02d>\n"%(name, n_id)
                    print(res)
                    action('no', res)
                    print "<no -- plain node (output) -- %s:%02d]\n"%(name, n_id)

                if 'rs' in spec:
                    print "[rs -- single node return? -- %s:%02d>\n"%(name, n_id)
                    print len(rlist) == 1
                    action('rs', len(rlist))
                    print "<rs -- single node return? -- %s:%02d]\n"%(name, n_id)
                elif 'r>' in spec:
                    print "[r> -- multiple node return? -- %s:%02d>\n"%(name, n_id)
                    print len(rlist) > 1
                    action('r>', len(rlist), **kwd)
                    print "<r> -- multiple node return? -- %s:%02d]\n"%(name, n_id)
                if 'r=' in spec:
                    print "[r= -- nid(return_node) == nid(input_node)? -- %s:%02d>\n"%(name, n_id)
                    print all(x[0] == node[0] for x in rlist)
                    action('r=', rlist, **kwd)
                    print "<r= -- nid(return_node) == nid(input_node)? -- %s:%02d]\n"%(name, n_id)
                if 'r!' in spec:
                    print "[r! -- nid(return_node) != nid(input_node)? -- %s:%02d>\n"%(name, n_id)
                    print all(x[0] != node[0] for x in rlist)
                    action('r!', rlist, **kwd)
                    print "<r! -- nid(return_node) == nid(input_node)? -- %s:%02d]\n"%(name, n_id)
                if 'so' in spec:
                    print "[so -- python source (output) -- %s:%02d>\n"%(name, n_id)
                    for i, nd in enumerate(rlist):
                        if i:
                            print "\n---------------- %s ----------------\n"%(i+2)
                        print self.langlet.unparse(nd)
                        action('so', nd, **kwd)
                    print "<so -- python source (output) -- %s:%02d]\n"%(name, n_id)
                if 'co' in spec:
                    print "[co -- cst (output) -- %s:%02d>\n"%(name, n_id)
                    for i, nd in enumerate(rlist):
                        if i:
                            print "\n---------------- %s ----------------\n"%(i+2)
                        self.langlet.pprint(nd)
                        action('co', nd, **kwd)
                    print "<co -- cst (output) -- %s:%02d]\n"%(name, n_id)
                if 'cv' in spec:
                    import EasyExtend.langlets.zero.langlet as zero
                    print "[cv -- cst validation test -- %s:%02d>\n"%(name, n_id)
                    for i, nd in enumerate(rlist):
                        if i:
                            print "\n---------------- %s ----------------\n"%(i+2)
                        check_node(nd, zero)
                        action('gc', nd, **kwd)
                    print "<cv -- cst validation test -- %s:%02d]\n"%(name, n_id)
            return res

        call_dbg.__name__ = name
        call_dbg.__doc__  = f.__doc__
        call_dbg.cst_transformer = False
        return call_dbg
    return transform

def transform_dbg(spec, cond = None, **kwd):
    def transform(f):
        call_dbg = t_dbg(spec, cond = cond, **kwd)(f)
        call_dbg.cst_transformer = True
        return call_dbg
    return transform


class Chain(object):
    def __init__(self, node_stack):
        self._node_stack = node_stack

    def up(self):
        n = len(self._node_stack)
        if n == 1:
            return self._node_stack[-1], None
        elif n>1:
            return self._node_stack[-1], Chain(self._node_stack[:-1])
        else:
            return None, None

class FSTransformer:
    def __init__(self):
        self.transformer = []
        self.langlet_offsets = set([0])  # py_default
        self.node_ids = set()          # collects all possible node id ranges
                                       # of available node transformers
        self._node_stack = {}
        self.toplevel_nids = (py_symbol.single_input,   # TODO: list toplevel
                              py_symbol.file_input,     # nids in nfamodule
                              py_symbol.eval_input)

    def _maybe_remove(self, trans):
        '''
        Method used to check whether a particular transformer has to be removed.

        @param trans: Transformer instance.
        '''
        alive = []
        dead  = []
        idx   = -1
        if trans.terminated:
            for i,T in enumerate(self.transformer):
                if T.langlet.LANGLET_OFFSET == trans.langlet.LANGLET_OFFSET:
                    if T.terminated:
                        dead.append(T)
                    else:
                        alive.append(T)
                    if T == trans:
                        idx = i
        if (alive or len(dead)>=1) and idx>=0:  # isn't the former condition trivially fulfilled?
            del self.transformer[idx]           # TODO: eliminate cruft, but carefully!


    def _add_transformer(self, trans):
        '''
        Adds one LangletTransformer instance.
        @param trans: Transformer instance.
        '''
        assert isinstance(trans, Transformer), str(type(trans))
        if trans.langlet.LANGLET_OFFSET not in self.langlet_offsets or len(self.node_ids)==0:
            self.langlet_offsets.add(trans.langlet.LANGLET_OFFSET)
            for T in self.transformer+[trans]:
                for nid in T._handler:
                    self.node_ids.update(self.nrange(nid))
        self.transformer.insert(0,trans)
        #print "DEBUG: _add_transformer", self.transformer

    @EasyExtend.util.psyco_optimized
    def nrange(self, nid):
        """
        For a node id return the corresponding node ids of all active langlets.
        """
        N0 = nid%512
        return [N0+offset for offset in self.langlet_offsets]

    def is_node(self, node, nid):
        '''
        Used to determine whether a node has a certain node id.

        This method generalizes the naive check on node[0] == nid.
        If the node can be guaranteed to be not a Python node this check is performed directly
        otherwise a test on the nrange of the node id is performed.

        @param node: node to be checked.
        @param nid: node id.
        @returns: True | False
        '''
        if node[0] == nid:
            return True
        return node[0] in self.nrange(nid)

    def get_handler(self, nid):
        """
        Seek for appropriate node handler using node id and ranging.

        @param nid: node id.
        @returns: list of node handlers for node id. Empty list if none was found.
        """
        handler    = []
        if nid in self.node_ids:
            for T in self.transformer:
                if T.terminated:
                    continue
                h = T._handler.get(nid)
                if h:
                    return [h]
            for T in self.transformer:
                for k in self.nrange(nid):
                    h = T._handler.get(k)
                    if h:
                        return [h]
        return handler

    def _mark_node(self, tree, transformer, parent = None, par_idx = -1, untrans = set()):
        '''
        Method used to apply settings on nodes having node id's that correspond with
        node handlers.

        If relevant node N was found wrap N into a cstnode object and set ::

             N.transformable = True
        '''
        cst = tree
        nid = tree[0]
        if not nid in untrans:
            h = self.get_handler(nid)
            if h:
                cst = cstnode(tree)
                cst.transformable = True
                cst.handler  = h
                cst.prepared = True
                if parent:
                    parent[par_idx] = cst
            else:
                untrans.add(nid)
        for i,sub in enumerate(cst[1:]):
            if isinstance(sub, list):
                if isinstance(sub, cstnode):
                    if sub.prepared:
                        break
                self._mark_node(sub, transformer, cst, i+1, untrans)
        return cst

    @EasyExtend.util.psyco_optimized
    def _unmark_node(self, tree, nid):
        '''
        Unmark all nodes i.e. set N.transformable = False on all cstnode
        objects.
        '''
        if isinstance(tree, cstnode):
            if nid>=0:
                if is_node(tree, nid):
                    tree.transformable = False
            else:
                tree.transformable = False
        for item in tree[1:]:
            if isinstance(item, list):
                self._unmark_node(item, nid)


    def call_node_transformer(self, tree, handler, kwd):
        '''
        Call node transformer.

        @param tree: target node of transformation.
        @param handler: handler corresponding to the node id.
        @param kwd: local context used to evaluate handler.
        @returns: a tuple of one or more nodes.
        '''
        # print "HANDLER", handler, kwd
        nodes = []
        err_msg = None
        for i, this_handler in enumerate(handler):
            try:
                nodes = this_handler(tree, **kwd)
            except TypeError:
                nodes = this_handler(tree)
            break
        else:
            cls, msg, tb = err_msg
            raise cls, msg, tb
        if nodes:
            assert isinstance(nodes, (list, tuple)), "self.%s() -> %s. Node(s) were expected."%(this_handler.__name__, nodes)
            if isinstance(nodes, list):
                if isinstance(nodes[0], list):
                    nodes = tuple(nodes)
                else:
                    nodes = (nodes,)
        return nodes

    @EasyExtend.util.psyco_optimized
    def find_transformable(self, T, node_stack, visited):
        if id(T) in visited:
            # The return has been caused by a cycle. The following code won't be executed
            # yet but might be activated in a stricter handling of cycles.
            from fstools import FSConfig
            name = FSConfig.get_sym_name(T[0])
            raise NodeCycleError("N in N with N of type `%s`. Use clone_node(N) to avoid cycles."% name)
        visited.add(id(T))
        res = []
        for sub in T[1:]:
            if isinstance(sub, cstnode):
                if sub.transformable:
                    res.append((sub, node_stack+[T]))
                    continue
            if isinstance(sub, list):
                res+=self.find_transformable(sub, node_stack+[T], set(visited))
        return res

    def _transform_more(self, tree, node_stack, kwd):
        def find_transformable(T, node_stack, visited):
            if id(T) in visited:
                # The return has been caused by a cycle. The following code won't be executed
                # yet but might be activated in a stricter handling of cycles.
                from fstools import FSConfig
                name = FSConfig.get_sym_name(T[0])
                raise NodeCycleError("N in N with N of type `%s`. Use clone_node(N) to avoid cycles."% name)
            visited.add(id(T))
            res = []
            for sub in T[1:]:
                if isinstance(sub, cstnode):
                    if sub.transformable:
                        res.append((sub, node_stack+[T]))
                        continue
                if isinstance(sub, list):
                    res+=find_transformable(sub, node_stack+[T], visited = set(visited))
            return res

        transformables = self.find_transformable(tree, node_stack, set())
        for (sub,c) in transformables:
            if sub.transformable:
                self.run(sub, node_stack = c, **kwd)


    def _check_nodes(self, handler, nodes):
        handler_name = handler.__name__
        if not hasattr(nodes, "__iter__"):
            raise TypeError("not iterable. Make sure that return value of handler '%s' is either 'None' or iterable."%handler_name)
        for node in nodes:
            if not hasattr(node, "__iter__"):
                raise TypeError("not iterable. Make sure that return value of handler '%s' is an iterable of iterables."%handler_name)
            if not node:
                raise ValueError("empty list or tuple. Make sure that return value of handler '%s' is an iterable of non-empty lists or tuples."%handler_name)
            if not isinstance(node[0], int):
                raise TypeError("no CST. First entry of node must be the node id of a parse tree node. Found '%s' instead"%node[0])


    def substitute(self, tree, nodes, repl_id, node_stack):
        '''
        Let (parent(tree), parent(parent(tree)), ..., parent(...(parent(tree))...))
        the parental hierarchy of tree. It can be denoted as (P1, ..., P(n)) where P(i) is
        the node id of the i-th grandparent of tree.

        The substitution algorithm seeks for P(i) with repl_id in nrange(P(i)). If found it
        replaces P(i) in P(i+1) with nodes = (N1, ..., N(k)). It is guaranteed that the node
        id of N(j) == repl_id.
        '''
        if repl_id % 512<256:  # replace token
            if tree[0]%512<256:
                tree[:] = nodes[0]
                return
        else:
            if node_stack:
                C_0 = node_stack[0]    # used for error reporting only ( see throwing of TranslationError below )
            else:
                C_0 = tree
            while node_stack:
                P = node_stack.pop()
                # print "DEBUG", P[0], self.nrange(P[0])
                if repl_id in self.nrange(P[0]):
                    try:
                        K = node_stack.pop()
                        for j,N in enumerate(K):
                            if id(N) == id(P):
                                K[:] = K[:j]+list(nodes)+K[j+1:]
                                return
                    except IndexError:    # nothing to pop from node_stack
                        P[:] = nodes[0]
                        return
                if P:
                    C_0 = P
        S = "Failed to embedd node %s.\n  Node %s must be a subnode of %s in:  \n\n%s"%(
             (tree[0], to_text(tree[0])),
             (tree[0], to_text(tree[0])),
             (repl_id, to_text(nodes[0][0])),
             present_node(C_0, mark=[tree[0]], stop=True, indent=8))
        raise TranslationError( S )


    def run(self, tree, node_stack = [], **kwd):
        '''
        Main transformation loop. Dispatches one node to node handlers decorated by @transform.
        The dispatched node gets replaced by the result of the node handler.

        @param tree: node to be dispatched.
        @param node_stack: internally maintained node stack. Used to manage node replacments.
        @param kwd: dictionary that contains local context of the langlet transformation to be
                       evaluated.
        '''
        assert isinstance(tree, list), tree
        tree_id = id(tree)
        try:
            tree.transformable = False
        except AttributeError:
            return self._transform_more(tree, node_stack, kwd)
        handler = self.get_handler(tree[0])   # retrieve handler by node id
        if handler:
            self._node_stack[tree_id] = node_stack  # store node_stack current node stack in variable _node_stack
                                                    # and make it available for the node transformer
            nodes = self.call_node_transformer(tree, handler, kwd)
            try:
                del self._node_stack[tree_id]
            except KeyError:
                pass
            if nodes:
                try:
                    repl_id = nodes[0][0]
                except Exception:
                    self._check_nodes(handler, nodes)
                    raise
                if  repl_id not in self.nrange(tree[0]) or len(nodes)>1:
                    nrange_0 = self.nrange(nodes[0][0])
                    for node in nodes:
                        assert node[0] in nrange_0, "Uniformity of sequence expected. %s was returned by self.%s() instead."%(nodes, handler[0].__name__)
                        self.run(node, node_stack=node_stack, kwd=kwd)
                    self.substitute(tree, nodes, repl_id, node_stack)
                else:   # input node has same node_id as returned node
                    tree[:] = nodes[0]
        self._transform_more(tree, node_stack, kwd)

fs_transformer = FSTransformer()

class Transformer(object):

    def __init__(self, langlet, **kwd):
        self.langlet = langlet
        self.token = self.langlet.token
        self.symbol= self.langlet.symbol
        self._handler = {}
        self._notified = False
        self.terminated = False

    @EasyExtend.util.psyco_optimized
    def prepare(self, tree):
        '''
        Add this transformer unconditionally to fiberspace transformers.
        '''
        if self._notified:
            return tree
        self._notified = True
        self._find_handler()
        fs_transformer._add_transformer(self)
        return fs_transformer._mark_node(tree, self)

    def mark_node(self, tree):
        fs_transformer._mark_node(tree, self)

    def unmark_node(self, tree, nid = -1):
        fs_transformer._unmark_node(tree, nid)

    def is_node(self, node, nid):
        return fs_transformer.is_node(node, nid)

    def contains_node(self, node, nids):
        for nid in nids:
            if fs_transformer.is_node(node, nid):
                return True
        return False

    def node_stack(self, node):
        _node_stack =  fs_transformer._node_stack.get(id(node))
        if _node_stack:
            return Chain(_node_stack)
        else:
            raise ValueError("No node_stack available for node")

    def get_container(self, node, nid):
        '''
        Get node N with node_id = nid when N is in the parental chain of node.
        raise ValueError if no such node is found.
        '''
        chain = self.node_stack(node)
        while chain:
            nd, chain = chain.up()
            if self.is_node(nd, nid):
                return nd
        raise ValueError("No node available with nid = %s that contains input node."%nid)


    def run(self, tree, **kwd):
        '''
        Delegate to multi-langlet transformer
        '''
        tree = self.prepare(tree)
        fs_transformer.run(tree, **kwd)


    def terminate(self):
        '''
        Explicit signaling of langlet transform termination. Dispatch to nodes of this transformer
        is stopped.
        '''
        self.terminated = True
        fs_transformer._maybe_remove(self)


    def _find_handler(self):
        '''
        Method used to find all methods that handle one node.
        '''
        items = [(name,getattr(self, name)) for name in dir(self)]
        for key,val in items:
            if hasattr(val,"cst_transformer"):
                try:
                    self._handler[getattr(self.symbol,key)] = val
                except AttributeError:
                    self._handler[getattr(self.token,key)] = val


    def _load_exospace(self):
        from EasyExtend.exotools import import_exoload
        return import_exoload

    def is_main(self, _if_stmt):
        '''
        Returns True if _if_stmt node has the structure "if __name__ == '__main__': BLOCK"
        otherwise it returns False.
        @param _if_stmt: node where node[0] == symbol.if_stmt
        '''
        if _if_stmt is None:
            return False
        assert self.is_node(_if_stmt, self.symbol.if_stmt), "if_stmt expected. %s found instead"%to_text(_if_stmt[0])
        if _if_stmt and len(_if_stmt)>4:
            _NAME = find_node(_if_stmt[2], self.token.NAME)
            _EQEQ = find_node(_if_stmt[2], self.token.EQEQUAL)
            _STR  = find_node(_if_stmt[2], self.token.STRING)
            if not _NAME or not _EQEQ or not _STR:
                return False
            else:
                if _NAME[1] !="__name__" or _STR[1] not in ("'__main__'",'"__main__"'):
                    return False
            return True
        return False


    def general_transform(self, tree):
        '''
        Toplevel transformations::
            (A)       if __name__ == '__main__':   =>  def __like_main__():
                                                          BLOCK

                                                      if __name__ == '__main__':
                                                         __like_main__()

            (B)       import __langlet__  =>  __langlet__ = import_and_init_langlet( <langlet_name> )


            (C)       STMT1
                      STMT2 ... =>  if STMT1 == from __future__ import*
                                        STMT1; from EasyExtend.exotools import exoload; exospace = exoload(__file__);
                                        STMT2 ....
                                    else:
                                        from EasyExtend.exotools import exoload; exospace = exoload(__file__);
                                        STMT1
                                        STMT2 ...
        '''
        # TODO: correct the docstring
        try:
            self.symbol.import_stmt
            self.symbol.if_stmt
            self.symbol.suite
        except AttributeError:
            return               # langlet might not support general transformations

        def no_future(node):
            if find_node(node, self.token.NAME):
                _import_stmt = find_node(node, self.symbol.import_stmt, level=3)
                if _import_stmt:
                    ls = find_all(_import_stmt, self.token.NAME)
                    if "__future__" in ls[1]:
                        return False
                return True

            return False

        def import_langlet_trans(node):
            if no_future(node):
                fragments = path(self.langlet.__file__).splitext()[0].splitall()
                pth = map(str, fragments[fragments.index("EasyExtend"):])
                dotted_import_as = dotted_as_names(dotted_as_name(dotted_name(*pth),'as','__langlet__'))
                #dotted_import_as = dotted_as_names(dotted_as_name(dotted_name(*pth)),'as','__langlet__')
                import_langlet  = any_stmt(import_stmt(import_name(dotted_import_as)))
                import_eecommon = small_stmt(import_stmt(CST_Import("EasyExtend.eecommon")))
                init_langlet    = small_stmt(CST_Assign("__langlet__",CST_CallFunc("EasyExtend.eecommon.init_langlet", ["__langlet__"])))
                return (stmt(simple_stmt(import_eecommon,init_langlet)) , import_langlet)
            return False

        def like_main_trans(node):
            #print "DEBUG - node[0]",node[0]
            _if_stmt = find_node(node, self.symbol.if_stmt,level=2)
            if self.is_main(_if_stmt):
                _suite = find_node(_if_stmt, self.symbol.suite)
                _func_def_suite = _suite[:]
                def__like_main__ = stmt(compound_stmt(funcdef(Name("__like_main__"),parameters(),_func_def_suite)))
                tree.insert(i,def__like_main__)
                _like_main_call = suite(simple_stmt(small_stmt(expr_stmt(testlist(any_test(power(atom(Name("__like_main__")),trailer("(",")"))))))))
                del _suite[:]
                _suite+=normalize(_like_main_call)
                return True
            return False

        imp_langlet = like_main_t = exo_t = False

        i = 1
        while i<len(tree):
            if like_main_t and imp_langlet and exo_t:
                break
            node = tree[i]
            if isinstance(node, list):
                if not like_main_t:
                    like_main_t = like_main_trans(node)
                if not imp_langlet:
                    trans = import_langlet_trans(node)
                    if trans:
                        tree.insert(i, trans[0])
                        tree.insert(i, trans[1])
                        i+=2
                        imp_langlet = True
                '''
                if not exo_t:
                    exo_t = no_future(node)
                    if exo_t:
                        exo = self._load_exospace()
                        tree.insert(i-1,self._load_exospace())
                        i+=1
                '''
            i+=1



