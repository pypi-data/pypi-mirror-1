# URL:     http://www.fiber-space.de
# Author:  Kay Schluehr <easyextend@fiber-space.de>
# Date:    22 June 2007
#--------------------------------------------------------------------------------------
# Factoring release specific definitions into this module
#--------------------------------------------------------------------------------------

# TODO: promote Trail here:
#       - hierarchy can either be created automatically or replaced by reachable()
#       - the path between N and test | statement can be automatically created


from cst import*

def proj_nid(node):
    return node[0]%512


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
    py_symbol.with_stmt:1,
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
               py_symbol.raise_stmt, py_symbol.yield_stmt, py_symbol.with_stmt]:
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
        - with_stmt
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
    elif nid in (py_symbol.if_stmt, py_symbol.for_stmt, py_symbol.while_stmt, py_symbol.try_stmt, py_symbol.classdef, py_symbol.funcdef, py_symbol.with_stmt):
        return [py_symbol.stmt,[py_symbol.compound_stmt,arg]]
    elif nid in (py_symbol.expr_stmt, py_symbol.print_stmt, py_symbol.del_stmt, py_symbol.pass_stmt, py_symbol.flow_stmt, py_symbol.import_stmt, py_symbol.global_stmt, py_symbol.exec_stmt, py_symbol.assert_stmt):
        return [py_symbol.stmt,[py_symbol.simple_stmt,small_stmt(arg),NEWLINE()]]
    elif nid in (py_symbol.break_stmt, py_symbol.continue_stmt, py_symbol.return_stmt, py_symbol.raise_stmt, py_symbol.yield_stmt):
        return [py_symbol.stmt,[py_symbol.simple_stmt,small_stmt(flow_stmt(arg)),NEWLINE()]]
    elif nid == py_symbol.test:
        return any_stmt(expr_stmt(testlist(arg)))
    else:
        raise ValueError, "Can't wrap into 'stmt' node: '%s'"% py_symbol.sym_name.get(nid, "node with nid = %s"%arg[0])


def any_old_test(arg):
    assert isinstance(arg, (tuple,list)), arg
    nid = proj_nid(arg)
    if nid == py_symbol.old_test:
        return arg
    elif nid in ( py_symbol.or_test, py_symbol.old_lambdef ):
        return [py_symbol.old_test,arg]
    elif nid == py_symbol.and_test:
        return [py_symbol.old_test,[symbol.or_test,arg]]
    elif nid in ( py_symbol.not_test, py_symbol.comparison ):
        return [py_symbol.old_test,[symbol.or_test,[py_symbol.and_test,arg]]]
    elif nid == py_symbol.expr:
        return [py_symbol.old_test,[symbol.or_test,[py_symbol.and_test,[py_symbol.not_test,[py_symbol.comparison,arg]]]]]
    else:
        return [py_symbol.old_test,[symbol.or_test,[py_symbol.and_test,[py_symbol.not_test,[py_symbol.comparison,any_expr(arg)]]]]]


def any_test(arg):
    '''
    Returns B{test} node whenever the input is one of  the following nodes:

        - test
        - or_test
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
    elif nid in ( py_symbol.or_test, py_symbol.lambdef ):
        return [py_symbol.test,arg]
    elif nid == py_symbol.and_test:
        return [py_symbol.test,[py_symbol.or_test,arg]]
    elif nid in ( py_symbol.not_test, py_symbol.comparison ):
        return [py_symbol.test,[py_symbol.or_test,[py_symbol.and_test,arg]]]
    elif nid == py_symbol.expr:
        return [py_symbol.test,[py_symbol.or_test,[py_symbol.and_test,[py_symbol.not_test,[py_symbol.comparison,arg]]]]]
    else:
        return [py_symbol.test,[py_symbol.or_test,[py_symbol.and_test,[py_symbol.not_test,[py_symbol.comparison,any_expr(arg)]]]]]

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
        raise ValueError, "Can't wrap into 'test' node: '%s'"% py_symbol.sym_name.get(nid, "node with nid = %s"%arg[0])


