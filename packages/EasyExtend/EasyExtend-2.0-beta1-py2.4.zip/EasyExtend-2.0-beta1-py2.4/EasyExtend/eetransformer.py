# URL:     http://www.fiber-space.de
# Author:  Kay Schluehr <easyextend@fiber-space.de>
# Date:    10 May 2006

import sys
from csttools import*
from eexcept import*


class WrongTransformerException(Exception):pass

__all__ = ["Transformer", "transform", "WrongTransformerException"]

def transform(f):
    '''
    Decorator for all cst transformer methods.
    '''
    f.cst_transformer = True
    return f

STOP_RECURSION = -1

import sets

class FSTransformer:
    def __init__(self):
        self.transformer = []
        self.fiber_offsets = sets.Set([0])  # py_default
        self.node_ids = sets.Set()          # collects all possible node id ranges
                                            # of available node transformers
    def maybe_remove(self, trans):
        '''
        Method used to check whether a particular transformer has to be removed.
        Remove transformer if answer is yes.

        @param trans: Transformer instance.
        '''
        live = []
        dead = []
        idx  = -1
        if trans.terminated:
            for i,T in enumerate(self.transformer):
                if T.fiber.FIBER_OFFSET == trans.fiber.FIBER_OFFSET:
                    if T.terminated:
                        dead.append(T)
                    else:
                        live.append(T)
                    if T == trans:
                        idx = i
        if (live or len(dead)>=1) and idx>=0:  # isn't the former condition trivially fulfilled?
            del self.transformer[idx]          # TODO: eliminate cruft, but carefully!


    def add_transformer(self, trans):
        '''
        Adds one FiberTransformer instance.
        @param trans: Transformer instance.
        '''
        assert isinstance(trans, Transformer), str(type(trans))
        if trans.fiber.FIBER_OFFSET not in self.fiber_offsets or len(self.node_ids)==0:
            self.fiber_offsets.add(trans.fiber.FIBER_OFFSET)
            for T in self.transformer+[trans]:
                for nid in T._handler:
                    self.node_ids.update(self.nrange(nid))
        self.transformer.insert(0,trans)
        #print "DEBUG: add_transformer", self.transformer

    def nrange(self, nid):
        """
        For a node id return the corresponding node ids of all fibers currently active.
        """
        N0 = nid%512
        return [N0+offset for offset in self.fiber_offsets]

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

    def call_node_transformer(self, tree, handler, locals = None):
        '''
        Call node transformer.
        @param tree: target node of transformation.
        @param handler: handler corresponding to the node id.
        @param locals: local context used to evaluate handler.
        @returns: one or more nodes.
        @type returns: tuple.
        '''
        nodes = []
        err_msg = None
        for i, this_handler in enumerate(handler):
            try:
                if locals:
                    try:
                        nodes = this_handler(tree, locals)
                    except TypeError:
                        nodes = this_handler(tree)
                else:
                    nodes = this_handler(tree)
                this_handler.im_self._trans_stmt = True
                break
            except WrongTransformerException:
                err_msg = sys.exc_info()
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

    def _find_transformable(self, tree, chain):
        '''
        Used to find nodes in tree that have corresponding node transformers.
        '''
        res = []
        for sub in tree[1:]:
            if isinstance(sub, list):
                if self.get_handler(sub[0]):
                    res.append((sub, chain+[tree]))
                else:
                    res+=self._find_transformable(sub, chain = chain+[tree])
        return res

    def run(self, tree, chain = [], locals = None, prio = None):
        '''
        Main transformation loop. Dispatches one node to node handlers decorated by @transform.
        The dispatched node gets replaced by the result of the node handler.

        @param tree: node to be dispatched.
        @param chain: internally maintained node stack. Used to manage node replacments.
        @param locals: dictionary that contains local context of the fiber transformation to be
                       evaluated.
        @param prio: yet unused scheduling advice. RFU.
        '''

        assert isinstance(tree, list), tree

        handler = self.get_handler(tree[0])
        if handler:
            nodes = self.call_node_transformer(tree, handler, locals)
            if nodes:
                try:
                    repl_id = nodes[0][0]
                except TypeError:
                    raise TypeError, "Can't access nodes[0][0] from node list where nodes[0] = %s"%nodes[0]
                if  repl_id not in self.nrange(tree[0]) or len(nodes)>1:
                    for node in nodes:
                        assert repl_id in self.nrange(node[0]), "Uniformity of sequence expected. %s was returned by self.%s() instead."%(nodes, handler.__name__)
                        self.run(node, chain=chain, locals=locals)
                    if chain:
                        C_0 = chain[0]    # used for error reporting only ( see throwing of TranslationError below )
                    else:
                        C_0 = tree
                    found = False                                             # chain = [[A..],[B,..],[repl_id,..],[C,..],[D,..]]
                    while chain:                                              # [A,..                        [A,..
                        P = chain.pop()                                       #   [B,..                        [B,..
                        if repl_id in self.nrange(P[0]):                      #     [repl_id,..     ===>         [repl_id',..
                            try:                                              #       [C,..
                                K = chain.pop()                               #         [D,..  transform(D) -> ([repl_id',..], )
                                for j,s in enumerate(K):
                                    if s == P:
                                        found = True
                                        K[j] = nodes[0]
                                        for T in reversed(nodes[1:]):
                                            K.insert(j+1,T)
                                        break
                            except IndexError:    # nothing to pop from chain
                                if repl_id%512 in (py_symbol.single_input,
                                                   py_symbol.file_input,
                                                   py_symbol.eval_input):

                                    del P[:]
                                    P.extend(nodes[0])
                                    found = True
                            break
                        if P:
                            C_0 = P
                    if not found:
                        S = "unable to subst node %s by node %s in:\n\n%s"%(
                             (tree[0], to_text(tree[0])),
                             (node[0], to_text(nodes[0][0])),
                             present_node(C_0, mark=[tree[0]], stop=True, indent=8))
                        raise TranslationError( S )
                else:   # input node has same node_id as returned node
                    if isinstance(nodes[0], sealed):
                        return
                    n = nodes[0][:]
                    del tree[:]
                    tree+=n
                    for (sub,c) in self._find_transformable(tree, chain):
                        self.run(sub, chain = c, locals = locals, prio = prio)

            else:  # empty node(s) returned from handler
                for (sub,c) in self._find_transformable(tree, chain):
                    self.run(sub, chain = c, locals = locals, prio = prio)

        else:  # no handler available yet
            for (sub,c) in self._find_transformable(tree, chain):
                self.run(sub, chain = c, locals = locals, prio = prio)


fs_transformer = FSTransformer()

class Transformer(object):

    def __init__(self, fiber, **kwd):
        self.fiber = fiber
        self.token = self.fiber.token
        self.symbol= self.fiber.symbol
        self._handler = {}
        self._trans_stmt = False
        self._notified = False
        self.terminated = False
        self.STOP_RECURSION = -1

    def notify(self):
        '''
        Add this transformer unconditionally to fiberspace transformers.
        '''
        if self._notified:
            return True
        self._notified = True
        self._find_handler()
        fs_transformer.add_transformer(self)
        return True

    def is_node(self, node, nid):
        return fs_transformer.is_node(node, nid)

    def contains_node(self, node, nids):
        for nid in nids:
            if fs_transformer.is_node(node, nid):
                return True
        return False

    def run(self, tree, locals = None):
        '''
        Delegate to multi-fiber transformer
        '''
        if self.notify():
            fs_transformer.run(tree, locals = locals, prio = self)

    def terminate(self):
        '''
        Explicit signaling of fiber transform termination. Dispatch to nodes of this transformer
        is stopped.
        '''
        self.terminated = True
        fs_transformer.maybe_remove(self)

    def has_trans_stmt(self):
        '''
        Indicates that transformation has been performed.
        '''
        return self._trans_stmt

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

    def _import_fiber(self):                          # does it always import? test!!!
        import os
        _f = self.fiber.__file__.split(os.sep)
        fiber_name = _f[-2]
        fiber_mod  = _f[-1].split(".")[0]
        dotted_import_as = dotted_as_names(dotted_as_name(dotted_name("EasyExtend","eecommon"),'as','eecommon'))
        import_eecommon  = small_stmt(import_stmt(import_name(dotted_import_as)))
        return simple_stmt(import_eecommon,
                           small_stmt(CST_Assign("__fiber__", CST_CallFunc("eecommon.import_and_init_fiber", ["'"+fiber_name+"'"])))
                          )

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

    def general_transform(self,tree):
        '''
        Toplevel transformations:
        (A)       if __name__ == '__main__':   =>  def __like_main__():
                                                      BLOCK

                                                  if __name__ == '__main__':
                                                     __like_main__()

        (B)       import __fiber__  =>  __fiber__ = import_and_init_fiber( <fiber_name> )
        '''
        if self.fiber.thin_fiber:   # thin fibers may not support various statements like if_stmt, import_stmt etc.
            return

        def import_fiber_trans(node):
            _import_stmt = find_node(node, self.symbol.import_stmt, level=3)
            if _import_stmt:
                ls = find_all(_import_stmt, self.token.NAME)
                if len(ls)==2:
                    if "__fiber__" in ls[1]:
                        if node[0] % 512 == py_symbol.stmt:
                            _import_and_init = self._import_fiber()
                            if _import_and_init:
                                node_replace(node, any_stmt(_import_and_init))
                                return True
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

        fiber_t     = False
        like_main_t = False
        for i,node in enumerate(tree):
            if isinstance(node, list):
                if like_main_t and fiber_t:
                    break
                else:
                    if not like_main_t:
                        like_main_t = like_main_trans(node)
                    if not fiber_t:
                        fiber_t = import_fiber_trans(node)



