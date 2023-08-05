import random
from conf import*
import PyGrammar
from EasyExtend.csttools import*
from EasyExtend.eetransformer import Transformer, transform

import chainlet
from chainlet import Chainlet

def isChainlet(obj):
    return isinstance(obj,Chainlet)

from xi import Xi

__publish__ = ["isChainlet", "Chainlet","Xi"]


class FiberTransformer(Transformer):

    @transform
    def switch_stmt(self, node):
        SELECT  = "SELECT_"+str(random.randrange(100000))
        _test   = node[2]
        _case   = find_node(node,symbol.case_stmt,level=0)
        _else   = find_node(node,symbol.suite,level=0)
        _cond   = any_expr(power(atom(Name("isChainlet")),trailer("(",arglist(argument(any_test(_test))),")")))
        _select = testlist(any_test(Name(SELECT)))
        assign_else = any_stmt(expr_stmt(_select,"=",testlist(any_test(_test))))
        _testlist   = map(any_test,find_all(_case,symbol.expr,level=0))
        select_args = arglist(*map(argument,_testlist))
        trailer_select      = trailer(".",Name("select"))
        trailer_select_args = trailer("(",select_args,")")
        call_select = testlist(any_test(power(find_node(_test,symbol.atom), trailer_select, trailer_select_args)))
        assign_if   = any_stmt(expr_stmt(_select,"=",call_select))
        if_chainlet = any_stmt(if_stmt(any_test(_cond),suite(assign_if),suite(assign_else)))
        if_case     = any_stmt(self._handle_case_stmt(_case,_select,_else))
        del_select  = any_stmt(del_stmt(exprlist(any_expr(Name(SELECT)))))
        return if_chainlet, if_case, del_select

    def _handle_case_stmt(self, node, _select, _else_suite = None):
        _tests   = map(any_test,find_all(node,symbol.expr,level=0))
        _suites  = find_all(node,symbol.suite,level=0)
        _select  = find_node(_select,symbol.expr)
        _conds   = [any_test(not_test(comparison(find_node(test,symbol.expr),"==",_select))) for test in _tests]
        if_input = sum(map(list,zip(_conds,_suites)),[])
        if _else_suite:
            if_input.append(_else_suite)
        return if_stmt(*if_input)

    @transform
    def repeat_stmt(self, node):
        "repeat_stmt: 'repeat' ':' suite 'until' ':' (NEWLINE INDENT test NEWLINE DEDENT | test NEWLINE )"
        _suite = find_node(node,symbol.suite)
        _test  = find_node(node, symbol.test, level=0)
        _until = if_stmt(_test,suite(any_stmt(break_stmt())))
        _suite.insert(-1,any_stmt(_until))
        return any_stmt(while_stmt(any_test(Number(1)),_suite))

    @transform
    def on_stmt(self, node):
        "on_stmt: 'on' NAME '=' test ':' suite ['else' ':' suite] "
        assert node[2][0] == token.NAME
        name = node[2][1]
        _name      = test_name(name)
        _test      = find_node(node,symbol.test)
        _suites    = find_all(node, symbol.suite, level=1)
        _assign    = CST_Assign(name, _test)
        stmt1 = any_stmt(_assign)
        stmt2 = any_stmt(if_stmt(_name,*_suites))
        return stmt1,stmt2

    # TODO: document feature
    @transform
    def xidef(self, node):
        __publish__.append("Xi")
        if node[2:] == []:
            return any_test(CST_CallFunc("Xi",["None"]))
        return any_test(CST_CallFunc("Xi",[test([symbol.lambdef,Name("lambda")]+node[2:])]))


if __name__ == '__main__':
    import fiber
    (options, args) = opt.parse_args()
    fiber.options   = options.__dict__
    if args:
        py_module = args[-1]
        EasyExtend.run_module(py_module, fiber)
    else:
        console = EasyExtend.create_console("Gallery", fiber)
        console.interact()


