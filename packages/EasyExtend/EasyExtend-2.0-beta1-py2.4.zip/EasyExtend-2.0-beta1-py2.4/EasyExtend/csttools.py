# URL:     http://www.fiber-space.de
# Author:  Kay Schluehr <easyextend@fiber-space.de>
# Date:    10 May 2006
#--------------------------------------------------------------------------------------
# 19 Sept 2006
# - Renamed surgery to csttools.
# - Factoring CST_XXX functions into a new module cstgen.py
#--------------------------------------------------------------------------------------

from cst import*
import random
import fstools

########################################################################################
#
#  A CST node may be a subnode of another CST node. The following 'hierarchy' dict
#  provides an ordering scheme among CST nodes. A node of a lower number can include
#  a node of a higher number but not reverse. This bounds the search depth for nodes
#  in a CST and is for optimization purposes only. If a CST node is missing it is
#  assumed that it has a higher number than anyone of the nodes in the hierarchy.
#
########################################################################################

hierarchy = {
    py_symbol.single_input:0,
    py_symbol.file_input:0,
    py_symbol.eval_input:0,
    py_symbol.funcdef:1,
    py_symbol.compound_stmt:1,
    py_symbol.suite:1,
    py_symbol.simple_stmt:2,
    py_symbol.stmt:1,
    py_symbol.classdef:1,
    py_symbol.if_stmt:1,
    py_symbol.while_stmt:1,
    py_symbol.for_stmt:1,
    py_symbol.try_stmt:1,
    py_symbol.small_stmt:3,
    py_symbol.expr_stmt:4,
    py_symbol.augassign:5,
    py_symbol.print_stmt:4,
    py_symbol.expr_stmt:4,
    py_symbol.del_stmt:4,
    py_symbol.pass_stmt:4,
    py_symbol.flow_stmt:4,
    py_symbol.import_stmt:4,
    py_symbol.global_stmt:4,
    py_symbol.exec_stmt:4,
    py_symbol.assert_stmt:4,
    py_symbol.parameters:5,
    py_symbol.break_stmt:5,
    py_symbol.continue_stmt:5,
    py_symbol.return_stmt:5,
    py_symbol.raise_stmt:5,
    py_symbol.yield_stmt:5,
    py_symbol.varargslist:6,
    py_symbol.fpdef:7,
    py_symbol.test:8,
    }

class sealed(list):
    pass


def projection(node):
    '''
    The projection function takes a parse tree of an arbitrary fiber and maps it onto a
    a Python parse tree. This is done by shifting the node ids of each node to the left.
    Since each node id can be described by
        nid = n + k*512,  with n<512
    the node id of the Python node is just the rest of division by 512: n = nid%512
    '''
    if node[0]>MAX_PY_SYMBOL:
        node[0] = node[0]%512
    for item in node[1:]:
        if isinstance(item, (list, tuple)):
            projection(item)
    return node

def lift(node, FIBER_OFFSET):
    # print node
    if node[0]<FIBER_OFFSET:
        node[0] = node[0]+FIBER_OFFSET
    for item in node[1:]:
        if isinstance(item, (list, tuple)):
            lift(item, FIBER_OFFSET)
    return node


def maybe_projection(node):
    '''
    This is a variant of the projection() function. It projects on a Python cst only
    when the first node can be projected.
    '''
    if node[0]>MAX_PY_SYMBOL:
        node[0] = node[0]%512
        for item in node[1:]:
            if isinstance(item, (list, tuple)):
                projection(item)
    return node

def maybe_lift(node, FIBER_OFFSET):
    '''
    This is a variant of the projection() function. It projects on a Python cst only
    when the first node can be projected.
    '''
    if node[0]<FIBER_OFFSET:
        node[0] = node[0]+FIBER_OFFSET
        for item in node[1:]:
            if isinstance(item, (list, tuple)):
                lift(item, FIBER_OFFSET)
    return node

def proj_nid(node):
    return node[0]%512

def node_cmp(tree, node_id):
    '''
    Compares first node of cst tree with node_id.

    @param tree:  CST
    @param node_id: integer representing a py_symbol not a py_token

    @return:
             - 0 if node_id is tree-root.
             - -1 if tree is a py_token or node_id cannot be the node_id of any subtree.
             - 1 otherwise
    '''
    tree_id = proj_nid(tree)
    node_id = node_id%FIBER_OFFSET_SCALE
    if tree_id == node_id:
        return 0
    elif tree_id<256:
        return -1
    try:
        s0 = hierarchy[tree_id]
        s1 = hierarchy[node_id]
        if s0>s1:
            return -1
    except KeyError:
        return 1

def to_text(node_id):
    name = fstools.FSConfig.get_sym_name(node_id)
    if not name:
        name = fstools.FSConfig.get_tok_name(node_id)
    if not name:
        return "(node_id = %s) -> ???"%node_id
    return name


def present_node(node, mark = [], stop = False, indent = 0, short_form = False):
    INDENT = 2

    exclude = [[py_symbol.test, py_symbol.atom]]

    def make_short(node):
        nid = proj_nid(node)
        for iv in exclude:
            if iv[0]<=nid<iv[1]:
                n = node
                while 1:
                    if len(n) > 2:
                        return True, n
                    elif proj_nid(n)<iv[1]:
                        n = n[1]
                    else:
                        return True, n[1]
        return False, node


    def toText(node_id):
        div, rest = divmod(node_id, FIBER_OFFSET_SCALE)
        if rest >= 256:
            name = fstools.FSConfig.get_sym_name(node_id)
            if name:
                return name+"  -- S`%d -- %d"%(node_id, rest)
            return py_symbol.sym_name[rest]+"  -- S`%d"%(rest,)
        else:
            name = fstools.FSConfig.get_tok_name(node_id)
            if name:
                return name+"  -- T`%d -- %d"%(node_id, rest)
            return py_token.tok_name[rest]+"  -- T`%d"%(rest,)

    def node2text(node, indent = 0):
        if not node:
            return " "*(indent+INDENT)+str(node)+"  <----------    ???    <---------  \n\n"

        if node[0] in mark or to_text(node[0]) in mark or ("> MAX_PY_SYMBOL" in mark and node[0]%512 > MAX_PY_SYMBOL):
            s = " "*indent+toText(node[0])+"       <-------  \n"
            if stop == True:
                s+=" "*(indent+INDENT)+".... \n\n"
                return s
        else:
            ln = node[-1]
            if isinstance(ln, int):
                s = " "*indent+toText(node[0])+"     L`%s"%(node[-1])+"\n"
            else:
                s = " "*indent+toText(node[0])+"\n"
        for item in node[1:]:
            if isinstance(item, (list, tuple)):
                if short_form:
                    rc, nd = make_short(item)
                    if rc and nd[0] !=item[0]:
                        indent = indent+INDENT
                        ln = item[-1]
                        if isinstance(ln, int):
                            s += " "*indent+toText(item[0])+"     L`%s"%(node[-1])+"\n"
                        else:
                            s += " "*indent+toText(item[0])+"\n"
                        s+=" "*(indent+INDENT)+"... \n"
                    s+=node2text(nd, indent+INDENT)
                else:
                    s+=node2text(item, indent+INDENT)
            elif isinstance(item, str):
                s+=" "*(indent+INDENT)+item +"\n"
        if indent == 0:
            return "\n"+s+"\n"
        else:
            return s

    return node2text(node, indent = indent)

def pprint(node, mark = [], stop = True, indent = 0, short_form = False):
    print present_node(node, mark = mark, stop = stop, indent = indent, short_form = short_form)


def node_replace(old, new):
    del old[:]
    old.extend(new)
    return old

def left_shift(node):
    rest = node[1]
    return node_replace(node, rest)

def replace_in(context, nid, in_nid, by):
    assert proj_nid(by) == in_nid%512
    for _in in find_all(context, in_nid):
        if _in:
            if find_node(_in, nid):
                node_replace(_in, by)
                break

def prepare_source(source):
    res = []
    lines = source.split("\n")
    k = -1
    for line in lines:
        if line.strip() == "":
            continue
        if k == -1:
            line = line.rstrip()
            n = len(line)
            line = line.lstrip()
            k = n-len(line)
            res.append(line)
        else:
            res.append(line[k:].rstrip())
    return "\n".join(res).strip()

def make_node(item):
    if isinstance(item, (list, tuple)):
        try:
            return atomize(item)
        except (ValueError,TypeError):
            return item
    elif isinstance(item, (int, long, float)):
        return atomize(Number(item))
    elif isinstance(item, str):
        return atomize(String(item))
    else:
        raise SyntaxError, "Cannot turn item %s into node"%item




########################################################################################################
#
#  Functions used to provide important abbreviations.
#
#  Numeric references are used for optimised access and may be replaced.
#
########################################################################################################

# stmt, simple_stmt, compound_stmt, small_stmt, if_stmt, for_stmt, while_stmt, try_stmt
# break_stmt, continue_stmt, return_stmt, raise_stmt, yield_stmt

def is_stmt(node):
    nid = proj_nid(node)
    if nid in [py_symbol.stmt, py_symbol.simple_stmt, py_symbol.compound_stmt, py_symbol.small_stmt, py_symbol.if_stmt, py_symbol.for_stmt,
               py_symbol.while_stmt, py_symbol.try_stmt, py_symbol.break_stmt, py_symbol.continue_stmt, py_symbol.return_stmt,
               py_symbol.raise_stmt, py_symbol.yield_stmt]:
               return True
    return False

def any_stmt(arg):
    '''
    Returns B{stmt} node whenever the input is one of  the following nodes:

        - stmt
        - simple_stmt
        - compound_stmt
        - small_stmt
        - if_stmt
        - for_stmt
        - while_stmt
        - try_stmt
        - break_stmt
        - continue_stmt
        - return_stmt
        - raise_stmt
        - yield_stmt

    '''

    nid = proj_nid(arg)
    if nid == py_symbol.stmt:
        return arg
    elif nid in (py_symbol.simple_stmt, py_symbol.compound_stmt):
        return [py_symbol.stmt,arg]
    elif nid == py_symbol.small_stmt:
        return [py_symbol.stmt,[py_symbol.simple_stmt,arg,NEWLINE()]]
    elif nid in (py_symbol.if_stmt, py_symbol.for_stmt, py_symbol.while_stmt, py_symbol.try_stmt, py_symbol.classdef, py_symbol.funcdef):
        return [py_symbol.stmt,[py_symbol.compound_stmt,arg]]
    elif nid in (py_symbol.expr_stmt, py_symbol.print_stmt, py_symbol.del_stmt, py_symbol.pass_stmt, py_symbol.flow_stmt, py_symbol.import_stmt, py_symbol.global_stmt, py_symbol.exec_stmt, py_symbol.assert_stmt):
        return [py_symbol.stmt,[py_symbol.simple_stmt,small_stmt(arg),NEWLINE()]]
    elif nid in (py_symbol.break_stmt, py_symbol.continue_stmt, py_symbol.return_stmt, py_symbol.raise_stmt, py_symbol.yield_stmt):
        return [py_symbol.stmt,[py_symbol.simple_stmt,small_stmt(flow_stmt(arg)),NEWLINE()]]
    elif nid == py_symbol.test:
        return any_stmt(expr_stmt(testlist(arg)))
    else:
        raise ValueError, "Can't wrap into statement node '%s'"% py_symbol.sym_name[nid]


def any_test(arg):
    '''
    Returns B{test} node whenever the input is one of  the following nodes:

        - test
        - and_test
        - lambdef
        - not_test
        - comparison
        - expr
        - xor_expr
        - and_expr
        - shift_expr
        - arith_expr
        - term
        - factor
        - power
        - atom
        - NAME
        - STRING
        - NUMBER

    '''
    assert isinstance(arg, (tuple,list)), arg
    nid = proj_nid(arg)
    if nid == py_symbol.test:
        return arg
    elif nid in ( py_symbol.and_test, py_symbol.lambdef ):
        return [py_symbol.test,arg]
    elif nid in ( py_symbol.not_test, py_symbol.comparison ):
        return [py_symbol.test,[py_symbol.and_test,arg]]
    elif nid == py_symbol.expr:
        return [py_symbol.test,[py_symbol.and_test,[py_symbol.not_test,[py_symbol.comparison,arg]]]]
    else:
        return [py_symbol.test,[py_symbol.and_test,[py_symbol.not_test,[py_symbol.comparison,any_expr(arg)]]]]

# test, and_test, lambdef, not_test, comparison, expr, xor_expr, and_expr, shift_expr, arith_expr,
# term, factor, power, atom

def test_name(name):
    return any_test(Name(name))

def any_expr(arg):
    assert isinstance(arg,(tuple,list)), arg
    nid = proj_nid(arg)
    if nid == py_symbol.expr:
        return arg
    elif nid == py_symbol.xor_expr:
        return [py_symbol.expr,arg]
    elif nid == py_symbol.and_expr:
        return [py_symbol.expr,[py_symbol.xor_expr,arg]]
    elif nid == py_symbol.shift_expr:
        return [py_symbol.expr,[py_symbol.xor_expr,[py_symbol.and_expr,arg]]]
    elif nid == py_symbol.arith_expr:
        return [py_symbol.expr,[py_symbol.xor_expr,[py_symbol.and_expr,[py_symbol.shift_expr,arg]]]]
    elif nid == py_symbol.term:
        return [py_symbol.expr,[py_symbol.xor_expr,[py_symbol.and_expr,[py_symbol.shift_expr,[py_symbol.arith_expr,arg]]]]]
    elif nid == py_symbol.factor:
        return [py_symbol.expr,[py_symbol.xor_expr,[py_symbol.and_expr,[py_symbol.shift_expr,[py_symbol.arith_expr,[py_symbol.term,arg]]]]]]
    elif nid == py_symbol.power:
        return [py_symbol.expr,[py_symbol.xor_expr,[py_symbol.and_expr,[py_symbol.shift_expr,[py_symbol.arith_expr,[py_symbol.term,[py_symbol.factor,arg]]]]]]]
    elif nid == py_symbol.atom:
        return [py_symbol.expr,[py_symbol.xor_expr,[py_symbol.and_expr,[py_symbol.shift_expr,[py_symbol.arith_expr,[py_symbol.term,[py_symbol.factor,[py_symbol.power,arg]]]]]]]]
    elif nid in (py_token.NAME, py_token.NUMBER, py_token.STRING):
        return [py_symbol.expr,[py_symbol.xor_expr,[py_symbol.and_expr,[py_symbol.shift_expr,[py_symbol.arith_expr,[py_symbol.term,[py_symbol.factor,[py_symbol.power,[py_symbol.atom,arg]]]]]]]]]
    else:
        raise ValueError, "Can't wrap into test node '%s'"% py_symbol.sym_name[nid]

def is_simple(node):
    '''
    check for the structure [a,[b,[c,[...[symbol.atom,...]...]
    This is called a "simple node"
    '''
    py_atom = py_symbol.atom
    n = node
    while n:
        if not isinstance(n, list) or n[0]%512 == py_atom:
            return True
        elif len(n) > 2:
            return False
        n = n[1]

def any_node(arg, node_id):
    nid  = node_id
    node = arg
    if isinstance(arg, int):
        node = Number(arg)
    elif isinstance(arg,str):
        if arg[0] in ("'",'"'):
            node = String(arg)
        else:
            node = Name(arg)
    try:
        if is_simple(node):
            node = any_test(node)
        else:
            node = any_test(atomize(node))
    except ValueError:
        if is_stmt(node):
            pass
    node = any_stmt(node)
    if nid == py_symbol.stmt:
        return node
    return find_node(node, node_id)


def new_name(name):
    return Name(name+str(random.randrange(100000)))

def del_name(name):
    return del_stmt(any_expr(name))

##################################################################################################
#
# Generic functions
#
##################################################################################################

def varargs2arglist(varargs):
    """
    This function is used to turn the arguments of a function defintion into that of a function
    call.

    Rationale:
        Let def f(x,y,*args):
                ...
        be a function definion. We might want to define a function def g(*args,**kwd): ...  that
        shall be called with the arguments of f in the body of f:

            def f(x,y,*args):
                ...
                g(x,y,*args)
                ...
        To call g with the correct arguments of f we need to transform the varargslist node according to
        f into the arglist of g.
    """

    if not varargs:
        raise ValueError, "No varargs found"
    maybe_projection(varargs)
    arguments = []
    i = 1
    while i<len(varargs):
        arg = varargs[i]
        if arg[0] == py_symbol.fpdef:
            if i+1 < len(varargs):
                tok = varargs[i+1][0]
                if tok == py_token.EQUAL:
                    i+=3
                elif tok == py_token.COMMA:
                    i+=2
                arguments.append(argument(test_name(arg[1][1])))
            else:
                arguments.append(argument(test_name(arg[1][1])))
                break
        elif arg[0] == py_token.STAR:
            arguments.append("*")
            arguments.append(test_name(varargs[i+1][1]))
            i+=2
        elif arg[0] == py_token.DOUBLESTAR:
            arguments.append("**")
            arguments.append(test_name(varargs[i+1][1]))
            i+=2
        elif arg[0] == py_token.COMMA:
            i+=1
        else:
            raise ValueError,"Unexpected node %s"%(py_token.tok_name[arg[0]])
    return arglist(*arguments)


def to_signature(varargs):
    signature = {'args':[], 'defaults':{}, 'star_args': None, 'dstar_args':None}
    n = len(varargs)-2
    i = 0
    while i<=n:
        item = varargs[1:][i]
        if proj_nid(item) == py_symbol.fpdef:
            if find_node(item, py_symbol.fplist):
                raise SyntaxError("Does not support tuple-structured arguments")
            else:
                signature['args'].append(item[1][1])
        elif proj_nid(item) == py_symbol.test:
            signature['defaults'][signature['args'][-1]] = item
            del signature['args'][-1]
        elif proj_nid(item) == py_token.STAR:
            i+=1
            _name = find_node(varargs[1:][i], py_token.NAME)[1]
            signature['star_args'] = _name
        elif proj_nid(item) == py_token.DOUBLESTAR:
            i+=1
            _name = find_node(varargs[1:][i], py_token.NAME)[1]
            signature['dstar_args'] = _name
        i+=1
    return signature



def priority_split(nodelist, operators, head = None):
    '''
    split a node list of the kind [Arg0, op0, Arg1, op1, ..., opN, ArgN] into a list of sublists
    that reflects the binding behaviour of the operators. If for example op0<op1 indicates that op0 has
    a lower binding behaviour that op1 than we get:

    L = [arg1, op0, arg2, op1, arg3, op0, arg4]

       priority_splitting(L,(op0,op1)) -> [arg1,op0,[arg2,op1,arg3],op0,arg4]

    If two operators op1,op2 with the same priority, no split will be done. This would be
    expressed by

       priority_splitting(L,(op0,(op1,op2)))

    The maximum nesting level is 1. The length of operators is always 2.

    The operators must be of the kind token.<operator> e.g. token.PLUS, token.SUB etc.

    If the optional parameter head is available one might wrap each non-op argument of the final
    list with head:

        priority_splitting(L, (op0,op1), hd) -> [[hd,arg1],op0,[hd,[arg2,op1,arg3]],op0,[hd,arg4]]
    '''
    assert len(operators) == 2, "Only two priorities ( or priority sets ) may be used"
    res = []
    sub = []
    ops = []
    for op in operators:
        if isinstance(op, int):
            ops.append([op])
        else:
            ops.append(op)
    op1,op2 = ops[0],ops[1]
    for i,item in enumerate(nodelist):
        for o in op1:
            if item[0] == o:
                if len(sub) == 1:
                    sub = sub[0]
                if head:
                    res.append([head,sub])
                else:
                    res.append(sub)
                res.append(item)
                sub = []
                break
        else:
            if sub:
                sub.append(item)
            else:
                sub = [item]
    if len(sub) == 1:
        sub = sub[0]
    if head:
        res.append([head,sub])
    else:
        res.append(sub)
    return res



def power_merge(nodeA, nodeB):
    '''

    This function merges a pair of power nodes in the following way::

          nodeA = atomA + trailerA   \\
                                     | =>   atomB + trailerB + trailerA
          nodeB = atomB + trailerB   /

    '''
    nodeA = maybe_projection(nodeA)
    nodeB = maybe_projection(nodeB)
    if nodeA[0] == py_symbol.power and nodeB[0] == py_symbol.power:
        trailerA = find_all(nodeA,py_symbol.trailer, level = 1)
        if not trailerA:
            trailerA = []
        trailerB = find_all(nodeB,py_symbol.trailer, level = 1)
        if not trailerB:
            trailerB = []
        atomB    = find_node(nodeB, py_symbol.atom)
        return power(atomB, *(trailerB+trailerA))


def concat_funcalls(funA, funB):
    '''
    Two function calls funA(argsA), funB(argsB) are merged to one call funA(args).funB(argsB).
    '''
    if funA[0] == py_symbol.power and funB[0] == py_symbol.power:
        trailerA = find_all(funA,py_symbol.trailer, level = 1)
        trailerB = find_all(funB,py_symbol.trailer, level = 1)
        atomA    = find_node(funA, py_symbol.atom)
        atomB    = find_node(funB, py_symbol.atom)
        return power(atomA, *(trailerA+[trailer(".",atomB[1])]+trailerB))


def atomize(node):
    '''
    A lot of substitutions involve either a test or an expr node as a target. But it might happen that
    the node that shall be substituted is a child of an atom and replacing the parental expr node of this
    atom substitutes too much i.e. all trailer nodes following the atom.

    In this case we apply a trick which we called 'atomization'.
    Let n be a node ( e.g. expr, power, test etc.) with n.node_id > atom.node_id than we apply

         atom("(",testlist_gexp(any_test(n)),")")

    Syntactically atomization puts nothing but parentheses around the expression. Semantically the expression and
    its atomization are identical.
    '''
    nid = proj_nid(node)
    if nid == py_symbol.testlist:
        tests = find_all(node, py_symbol.test, level = 1)
        return any_test(atom("(",testlist_gexp(*tests),")"))
    return atom("(",testlist_gexp(any_test(node)),")")


def split_file_input(tree):
    "splits file_input node containing many stmts into several file_input nodes containing one stmt"
    nid = proj_nid(tree)
    if nid == py_symbol.single_input or not find_node(tree, py_symbol.stmt):
        return [tree]
    assert nid == py_symbol.file_input, nid
    finp = []
    for node in tree[1:]:
        nid = proj_nid(node)
        if nid == py_symbol.stmt:
            finp.append([py_symbol.file_input,node,[py_token.ENDMARKER,""]])
    return finp

def split_expr(node):
    "splits an expr of the kind a.b(x).c(). ... into factors a, b, (x), c, (), ..."
    pw = find_node(node, py_symbol.power)
    at = find_node(pw, py_symbol.atom)
    tr = find_all(pw, py_symbol.trailer, level = 1)
    return [at]+tr


def exprlist2testlist( _exprlist ):
    nid = proj_nid(_exprlist)
    assert nid == py_symbol.exprlist, nid
    _testlist = []
    for en in find_all(_exprlist, py_symbol.expr, level = 1):
        _testlist.append(any_test(en))
    return testlist(*_testlist)


def add_to_suite(_suite, _stmt, pos=-1):
    n = find_node(_suite, py_symbol.simple_stmt, level=1)
    if n:
        _args = [any_stmt(n)]
        if pos==0:
            _args.insert(0,_stmt)
        else:
            _args.append(_stmt)
        return suite(*_args)
    else:
        nodes = find_all(_suite, py_symbol.stmt, level=1)
        if pos == -1:
            nodes.append(_stmt)
        else:
            nodes.insert(pos, _stmt)
        return suite(*nodes)


def func_name(node):
    return node[2][1]
    nid = proj_nid(node)
    name_gen = find_all(node, py_token.NAME, level = 1)
    name_gen.next()
    return name_gen.next()[1]


def normalize(node):
    '''
    Sometimes a function f is defined using a simple_stmt node wrapping its SUITE.

       def f(x):pass

    Trying to insert a stmt node into f's SUITE will cause a wrong statement:

       def f(x):stmt
       pass

    To prevent this we turn the simple_stmt node based SUITE of the original f into a
    stmt node based one which yields the correct result:

       def f(x):
           stmt
           pass
    '''
    nid = proj_nid(node)
    if nid == py_symbol.suite:
        assert nid == py_symbol.suite, py_symbol.sym_name[nid]
        if not find_node(node, py_symbol.stmt):
            _stmt = stmt(find_node(node, py_symbol.simple_stmt))
            return suite(_stmt)
    return node



###################################################
#
# Search and node retrieval functions
#
###################################################


def find_node(tree, node_id, level = 10000, exclude = []):
    '''
    finds one node with a certain node_id.
    '''
    res = node_cmp(tree, node_id)
    if res == 0:
        return tree
    elif res == -1:
        return
    if level<0:
        return
    for sub in tree[1:-1]:
        if sub[0] not in exclude:
            res = find_node(sub, node_id, level=level-1, exclude = exclude)
            if res:
                return res

    if isinstance(tree[-1], (list, tuple)) and tree[-1][0] not in exclude:
        return find_node(tree[-1], node_id, level=level-1, exclude = exclude)

def remove_node(tree, node, level = 10000, exclude = []):
    if not isinstance(tree, list):
        print tree
    node_id = node[0]
    res = node_cmp(tree, node_id)
    if res == -1:
        return
    if level<0:
        return
    for i, sub in enumerate(tree):
        if isinstance(sub, (list, tuple)) and sub[0] not in exclude:
            if sub == node:
                tree.remove(sub)
                return True
            else:
                res = remove_node(sub, node, level=level-1)
                if res:
                    return res
    return False

def find_one_of(tree, node_ids, level = 10000, exclude = []):
    '''
    Generalization of find_node. Instead of one node_id a list of several node ids
    can be passed. The first match will be returned.
    '''
    for nid in node_ids:
        res = find_node(tree, nid, level = level, exclude = exclude)
        if res:
            return res

def find_all(tree, node_id, level=10000, exclude = []):
    '''
    generator that finds all nodes with a certain node_id.
    '''
    return list(find_all_gen(tree, node_id, level = level, exclude = exclude))


def find_all_gen(tree, node_id, level=10000, exclude = []):
    '''
    generator that finds all nodes with a certain node_id.
    '''
    try:
        res = node_cmp(tree, node_id)
        if res == 0:
            yield tree
        elif res == -1 or level<0:
            raise StopIteration
        for sub in tree[1:]:
            if isinstance(sub, (list, tuple)) and sub[0] not in exclude:
                for item in find_all(sub, node_id, level=level-1, exclude = exclude):
                    if item:
                        yield item
    except Exception, e:
        raise e


def count_node(tree, node_id, level=10000, exclude = []):
    '''
    generator that finds all nodes with a certain node_id.
    '''
    res = node_cmp(tree, node_id)
    if res == 0:
        return 1
    elif res == -1 or level<0:
        return 0
    count = 0
    for sub in tree[1:]:
        if isinstance(sub, (list, tuple)) and sub[0] not in exclude:
            count+=count_node(sub, node_id, level=level-1, exclude = exclude)
    return count


def find_all_of(tree, node_ids = [], level=10000, exclude = []):
    '''
    Generalizes find_all such that all nodes are yielded that have a node id listed in node_ids.
    '''
    def comp(t, nids):
        mx = -1
        for res in (node_cmp(t, nid) for nid in nids):
            if res == 0:
                return 0
            mx = max(res, mx)
        return mx
    try:
        res = comp(tree, node_ids)
        if res == 0:
            yield tree
        elif res == -1 or level<0:
            raise StopIteration
        for sub in tree:
            if isinstance(sub, (list, tuple)) and sub[0] not in exclude:
                for item in find_all_of(sub, node_ids=node_ids, level=level-1, exclude = exclude):
                    if item:
                        yield item
    except Exception, e:
        raise e


# import cstgen to provide a single interface to all kinds of csttools
from cstgen import*


if __name__ == '__main__':
    import parser
    PASS    = any_stmt(pass_stmt())
    ARG     = fpdef(Name("x"))
    VARARGS = varargslist(ARG)
    PARAMS  = parameters(VARARGS)
    SUITE   = suite(PASS)

    f_tree = file_input(stmt(compound_stmt(funcdef(Name("f"),PARAMS,SUITE))))
    [261, [1, 'def'], [1, 'f'],
          [262, [7, '('], [263, [264, [1, 'x']]], [8, ')']], [11, ':'],
          [297, [4, ''], [5, ''], [266, [267, [268, [273, [1, 'pass']]]]], [6, '']]]

    lambda_expr = parser.suite("lambda x,y=9:x+9").tolist()
    print while_stmt.__doc__
    print if_stmt.__doc__
    print break_stmt()
    print suite.__doc__
    print stmt.__doc__
    print power.__doc__

    suite(any_stmt(break_stmt()))

    #print find_all(parser.expr("a+b+c+f(d*8)").tolist(),py_token.NAME)
    #print parser.suite("a=8").tolist()
    #[257, [266, [267, [268, [269, [320, [298, [299, [300, [301, [303, [304, [305, [306, [307, [308, [309, [310, [311, [1, 'a']]]]]]]]]]]]]]], [22, '='], [320, [298, [299, [300, [301, [303, [304, [305, [306, [307, [308, [309, [310, [311, [2, '8']]]]]]]]]]]]]]]]], [4, '']]], [0, '']]
    print listmaker.__doc__
    print atom.__doc__

    print parser.suite("def f(x):\n  pass").tolist() == f_tree
    print argument.__doc__
    print import_stmt.__doc__
    print import_from.__doc__
    print import_name.__doc__
    print dotted_as_name.__doc__
    print dotted_as_name.__doc__
    print dotted_name.__doc__

    a = any_test(Name("8989"))
    #print bl("name")
    #print find_node(parser.suite("sig[k].update()").tolist(),py_symbol.expr)
    #print any_expr(power(Name("sig"),trailer("[",subscriptlist(subscript(any_test(Name("k")))),"]"),trailer(".","update"),trailer("(",")")))
    #print py_symbol.trailer

    def f(x,z=0):
        print vars()
    f(2)
    print list(find_all_of(lambda_expr, (1,2,3)))
    print priority_split([[4,9],[1],[5,10],[0],[6,11],[2],[7,12]],((0,2),1),77)


