'''
This module contains implementations that are not yet used.
'''

class pnode(list):
    '''
    Wrapper for all node objects.
    '''
    def __init__(self, lst):
        list.__init__(self, lst)

#################################################################################################
#
#  The BinList function is used to handle nested list of the structure [a,[b,[c,...[y,z]]..]
#
#################################################################################################
def BinList(flat):
    '''
    The csttools module contains lots of functions that return deeply nested lists e.g.

        [py_symbol.expr,[py_symbol.xor_expr,[py_symbol.and_expr,[py_symbol.shift_expr,arg]]]]

    Here 'arg' is the only variable. Now we want to consider this list as immutable
    and just replace 'arg' without creating it each time. The BinList approach replaces
    the list by a recursive data structure that has a list-like interface but stores the
    variable part separately.

    '''
    proto = None

    class _BinList(object):
        def __init__(self, x=None):
            self.x = x       # our variable
            if proto:
                self.first = proto.first
                self.next  = proto.next

        def _nest(self, lst):
            self.first = lst.pop(0)
            self.next  = None
            if lst:
                self.next = _BinList()
                self.next._nest(lst)

        def __getitem__(self, i):
            if i==0:
                return self.first
            elif i==1:
                if self.next:
                    self.next.x = self.x
                    return self.next
                else:
                    return self.x
            else:
                raise IndexError,i

        def __repr__(self):
            if self.next is None:
                return "[%s, %s]"%(self.first,self.x)
            else:
                return "[%s, %s]"%(self[0], self[1])

    bl = _BinList()
    bl._nest(flat)
    proto = bl
    return _BinList

def repair_lines(tree, offset):
    '''
    Not used yet.
    '''
    tree = tuplify(tree, True)
    class LineNumber:
        ln   = 1
    stack = []

    def repair(node):
        for sub in node:
            if isinstance(sub, list):
                ln = sub[-1]
                if ln<offset:
                    del sub[-1]
                else:
                    sub[-1]-=offset
                '''
                if ln < LineNumber.ln:
                    del sub[-1]
                elif ln > LineNumber.ln:
                    if ln == LineNumber.ln+1:
                        LineNumber.ln+=1
                    else:
                        del sub[-1]

                    else:
                        try:
                            i = ori_token.index(sub)
                            if ori_token[i-2][-1] > LineNumber.ln:
                                sub[-1] = LineNumber.ln
                            else:
                                LineNumber.ln = sub[-1]
                        except ValueError:
                            del sub[-1]
                '''
                print "LN", sub #, LineNumber.ln
            elif isinstance(sub, tuple):
                repair(sub)
    repair(tree)


def tuplify(tree, semi=False):
    '''
    Turns CST list representation into an aequivalent tuple representation.
    '''
    for i,t in enumerate(tree):
        if isinstance(t, list):
            if semi and isinstance(t[-1],int):
                tree[i] = t[:]
            else:
                tree[i] = tuplify(t,semi)
        elif isinstance(t, tuple):
            tree[i] = tuplify(list(t), semi)
    return tuple(tree)

class Lifter(object):
    '''
    Motivation:
       Let F1, F2 be independently defined fibers that shall be combined ( see the macro fiber for example ).
       When both define new grammar rules at least one node with node-id = MAX_PY_SMBOL+1 will be generated for
       each fiber. This causes a conflict to be resolved.
       The Lifter is a simple attempt to resolve conflicting node id's. If N is a node parsed according to F1
       'lifting' N means shifting each node-id with node-id > MAX_PY_SYMBOL by a fixed offset.

    The Lifter is a crude hack to enable shifting symbols at runtime.
    Background: you might have two fibers F1 and F2 that define new grammar rules. These rules will be mapped
       on a common token id 334.
    '''
    def __init__(self, offset):
        self.offset = offset

    def lift_symbols(self, symbols):
        for name in dir(symbols):
            v = getattr(symbols,name)
            if isinstance(v,int) and v > MAX_PY_SYMBOL:
                setattr(symbols, name, v+self.offset)
                symbols.sym_name[v+self.offset] = name
        return symbols

    def lift_node(self, node):
        if node[0]>MAX_PY_SYMBOL:
            node[0] = node[0]+self.offset
        for item in node[1:]:
            if isinstance(item, (list, tuple)):
                self.lift_node(item)
        return node

    def lift_lines(self, tree):
        "line numbers of orginal code will be lifted so that they can be identified in new code"
        for i,t in enumerate(tree):
            if isinstance(t, list):
                if isinstance(t[-1],int):
                    t[-1]+=self.offset
                else:
                    self.lift_lines(t)

import types

class s_(object):
    def __init__(self, arg):
        self.cst = arg

break_    = s_(break_stmt())
continue_ = s_(continue_stmt())

class return_(s_):
    def __init__(self, *args):
        self.cst = return_stmt(testlist(*[any_test(e_(arg).cst) for arg in args]))

class if_(s_):
    def __init__(self, _test, _suite):
        self._cst = [any_test(e_(_test).cst), _suite.cst]

    def elif_(self, _test, _suite):
        self._cst += [any_test(e_(_test).cst), _suite.cst]

    def else_(self, _suite):
        self._cst.append(_suite.cst)

    def _get_cst(self):
        return if_stmt(*self._cst)

    cst = property(_get_cst)

class suite_(s_):
    def __init__(self, *args):
        self._cst = []
        for arg in args:
            self.stmt_(arg)

    def stmt_(self, arg):
        if isinstance(arg, list):
            self._cst.append(any_stmt(arg))
        elif isinstance(arg, e_):
            self._cst.append(any_stmt(any_test(arg.cst)))
        elif isinstance(arg, s_):
            self._cst.append(any_stmt(arg.cst))
        else:
            raise ValueError("Cannot turn argument into statement")

    def _get_cst(self):
        return suite(*self._cst)

    cst = property(_get_cst)

def in_(arg1, arg2):
    return e_(arg1).in_(arg2)

def not_in_(arg1, arg2):
    return e_(arg1).not_in_(arg2)

class e_(object):
    def __init__(self, arg):
        if isinstance(arg, (int, long, float, complex)):
            self.cst = Number(arg)
        elif isinstance(arg, str):
            self.cst =  Name(arg)
        elif isinstance(arg, e_):
            self.cst = arg.cst
        elif isinstance(arg, list):
            self.cst = arg
        elif isinstance(arg, types.MethodType):
            self.cst = Name(arg.__name__)
        else:
            raise TypeError("Invalid type for e_ constructor : %s"%type(arg))

    def __add__(self, arg):
        return e_(CST_Add(self.cst, e_(arg).cst))

    def __radd__(self, arg):
        return e_(CST_Add(e_(arg).cst, self.cst))

    def __sub__(self, arg):
        return e_(CST_Sub(self.cst, e_(arg).cst))

    def __rsub__(self, arg):
        return e_(CST_Sub(e_(arg).cst, self.cst))

    def __mul__(self, arg):
        return e_(CST_Mul(self.cst, e_(arg).cst))

    def __rmul__(self, arg):
        return e_(CST_Mul(e_(arg).cst, self.cst))

    def __div__(self, arg):
        return e_(CST_Div(self.cst, e_(arg).cst))

    def __rdiv__(self, arg):
        return e_(CST_Div(e_(arg), self))

    def __pow__(self, arg):
        return e_(CST_Pow(self, e_(arg)))

    def __getitem__(self, arg):
        return e_(CST_Subscript(self.cst, e_(arg).cst))

    def __contains__(self, arg):
        return True

    def __getattr__(self, arg):
        return e_(CST_GetAttr(self.cst, Name(arg)))

    def in_(self, arg):
        return e_(CST_Comparison(self.cst, 'in', e_(arg).cst))

    def not_in_(self, arg):
        return e_(CST_Comparison(self.cst, 'not in',e_(arg).cst))

    def __call__(self, *args, **kwd):
        #names = find_all(self.cst, py_token.NAME, level = 1)
        #if not names:
        #    raise ValueError("Cannot find name of CST representing function")
        #name = namename[1]

        _power = find_node(self.cst, py_symbol.power)
        if _power:
            func = CST_CallFunc("xxx", args = [n.cst for n in args], dstar_args = kwd)
            return e_(power_merge(func, _power))
        else:
            _name = ( find_node(self.cst, py_token.NAME) or self.cst )
            return e_(CST_CallFunc(_name, args = [n.cst for n in args], dstar_args = kwd))


class list_(e_):
    def __init__(self, li):
        self._cst = [e_(item) for item in li]

    def _get_cst(self):
        return any_test(atom('[',listmaker(*[any_test(item.cst) for item in self._cst]),']'))

    cst = property(_get_cst)


class tuple_(list_):
    def _get_cst(self):
        return any_test(atom('(',testlist_gexp(*[any_test(item.cst) for item in self._cst]),')'))

    cst = property(_get_cst)

class dict_(e_):
    def __init__(self, dct):
        self._cst = []
        for key,val in dct.items():
            self._cst.extend([e_(key), e_(val)])

    def _get_cst(self):
        return any_test(atom('{',dictmaker(*[any_test(item.cst) for item in self._cst]),'}'))

    cst = property(_get_cst)

# import late since cstgen is also used by csttools

from csttools import any_test, any_stmt, any_expr, any_node, find_node, power_merge


if __name__ == '__main__':
    pass
    #print CST_CallFunc("name", [any_expr(Number(6))])
    CST_CallFunc("rev.re_Const",(Name("a"),))
    CST_Assign("bExecuted",Name("False"))
    x = e_("dev")
    from cst2source import*
    unparse = Unparser()
    e_("a")()


    print unparse((e_("a")+e_("b").f.h(e_(String("zu")))).cst)
    #print unparse(if_(e_("i") in e_("range")(e_(100)).cst)

    CST.If( (CST.E(1).Not_In(CST.Dict({'1':2, '"o"':5} ))),
             CST.Suite(
                 CST.E("print")(CST.E(9)+'a')

    print unparse(
        if_( (e_(1).not_in_(dict_({'1':2,"'o'":5}))),
             suite_(
                e_("print")(e_(9)+'a'),
                return_(
                    list_((9,88))
                )
            )
       ).cst)

