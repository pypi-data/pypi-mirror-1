from conf import*
from EasyExtend.csttools import*
import random

import chainlet
import ip
from chainlet import Chainlet

def isChainlet(obj):
    return isinstance(obj,Chainlet)

__publish__ = ["isChainlet", "Chainlet", "ip"]


class LangletTransformer(Transformer):

    @transform
    def switch_stmt(self, node):
        SELECT  = "SELECT_"+str(random.randrange(100000))
        _test   = node[2]
        _case   = find_node(node,symbol.case_stmt,level = 1)
        _else   = find_node(node,symbol.suite,level = 1)
        _cond   = any_expr(power(atom(Name("isChainlet")),trailer("(",arglist(argument(any_test(_test))),")")))
        _select = testlist(any_test(Name(SELECT)))
        assign_else = any_stmt(expr_stmt(_select,"=",testlist(any_test(_test))))
        _testlist   = map(any_test,find_all(_case,symbol.expr, level = 1))
        select_args = arglist(*map(argument,_testlist))
        trailer_select      = trailer(".",Name("select"))
        trailer_select_args = trailer("(",select_args,")")
        call_select = testlist(any_test(power(parens(find_node(_test,symbol.atom)), trailer_select, trailer_select_args)))
        assign_if   = any_stmt(expr_stmt(_select,"=",call_select))
        if_chainlet = any_stmt(if_stmt(any_test(_cond),suite(assign_if),suite(assign_else)))
        if_case     = any_stmt(self._handle_case_stmt(_case,_select,_else))
        del_select  = any_stmt(del_stmt(exprlist(any_expr(Name(SELECT)))))
        return if_chainlet, if_case, del_select

    def _handle_case_stmt(self, node, _select, _else_suite = None):
        _tests   = map(any_test,find_all(node,symbol.expr,level = 1))
        _suites  = find_all(node,symbol.suite,level = 1)
        _select  = find_node(_select,symbol.expr)
        _conds   = [any_test(not_test(comparison(find_node(test,symbol.expr),"==",_select))) for test in _tests]
        if_input = sum(map(list,zip(_conds,_suites)),[])
        if _else_suite:
            if_input.append(_else_suite)
        return if_stmt(*if_input)

    @transform
    def repeat_stmt(self, node):
        "repeat_stmt: 'repeat' ':' suite 'until' ':' (NEWLINE INDENT test NEWLINE DEDENT | test NEWLINE )"
        _suite = find_node(node, symbol.suite)
        _test  = find_node(node, symbol.test, level=1)
        _until = if_stmt(_test, suite(any_stmt(break_stmt())))
        _suite.insert(-1, any_stmt(_until))
        return any_stmt(CST_While(True,_suite))

    @transform
    def if_stmt(self, node):
        "if_stmt: 'if' test [ as_name ] ':' suite ('elif' test [ as_name ] ':' suite)* ['else' ':' suite]"
        #
        # if test as x:
        #    BLOCK
        #
        #  --------->
        #
        # __d = {}
        # if __d.__setitem__("x", test) or __d["x"]:
        #    x = __d["x"]
        #    BLOCK
        # del __d

        if not find_node(node, symbol.as_name, level = 1):
            return

        __d = "__d_"+str(random.randrange(100000))
        __d_assign = any_stmt(CST_Assign(__d, CST_Dict()))
        __d_del    = any_stmt(CST_Del(__d))
        nodes = node[1:]
        new_if = [symbol.if_stmt]
        i = 0
        while i<len(nodes):
            item = nodes[i]
            if is_node(item, symbol.test):
                _test = item
                if is_node(nodes[i+1], symbol.as_name):
                    _suite = nodes[i+3]
                    name = find_all(nodes[i+1], token.NAME)[-1][1]
                    new_if.append(CST_Or(CST_CallFunc("%s.%s"%(__d, "__setitem__"), [String(name),_test]), CST_GetItem(__d, String(name))))
                    new_if.append(nodes[i+2])
                    name_assign = any_stmt(CST_Assign(name, CST_GetItem(__d, String(name))))
                    new_if.append(add_to_suite(_suite, name_assign, 0))
                    i+=4
                    continue
                else:
                    new_if.append(item)
            else:
                new_if.append(item)
            i+=1
        return [__d_assign, any_stmt(new_if), __d_del]


    @transform
    def IPv4Address(self, node):
        nd = find_node(node, token.IPv4Address)
        if nd:
            sub = nd[1].split(".")
            T = CST_Tuple(*sub)
            return atomize(CST_CallFunc("ip.IPv4", [T]))



    @transform
    def thunk_stmt(self, node):
        small = find_node(node, symbol.small_stmt)

        # perform checks on expression form NAME '=' NAME for small_stmt
        # and extract names

        _expr_stmt = find_node(small, symbol.expr_stmt)
        if not _expr_stmt:
            raise SyntaxError("thunk_stmt is required to have the form:  NAME = NAME ':' SUITE")
        if len(_expr_stmt) == 4:
            nid, tl1, eq, tl2 = _expr_stmt
            if not ( is_node(tl1, symbol.testlist) and \
                     is_node(eq, token.EQUAL) and \
                     is_node(tl2, symbol.testlist)):
                raise SyntaxError("thunk_stmt is required to have the form:  NAME = NAME ':' SUITE")
            a1, a2 = smallest_node(tl1), smallest_node(tl2)
            if not ( is_node(a1, symbol.atom) and \
                     is_node(a2, symbol.atom)):
                raise SyntaxError("thunk_stmt is required to have the form:  NAME = NAME ':' SUITE")
            Name = find_node(a1, token.NAME, level = 1)
            Func = find_node(a2, token.NAME, level = 1)
            if Name is None or Func is None:
                raise SyntaxError("thunk_stmt is required to have the form:  NAME = NAME ':' SUITE")
        else:
            raise SyntaxError("thunk_stmt is required to have the form:  NAME = NAME ':' SUITE")

        name, func = Name[1], Func[1]
        returns    = any_stmt(CST_Return(CST_CallFunc("locals",[])))
        BLOCK      = add_to_suite(find_node(node, symbol.suite), returns)
        thunk      = any_stmt(CST_Function("thunk",BLOCK, ()))
        thunk_call = any_stmt(CST_Assign(name, CST_CallFunc(func, dstar_args = CST_CallFunc("thunk",[]))))
        del_thunk  = any_stmt(CST_Del("thunk"))
        return [thunk, thunk_call, del_thunk]


if __name__ == '__main__':
    import langlet
    (options, args) = opt.parse_args()
    langlet.options   = options.__dict__
    if args:
        py_module = args[-1]
        EasyExtend.run_module(py_module, langlet)
    else:
        console = EasyExtend.create_console("Gallery", langlet)
        console.interact()



