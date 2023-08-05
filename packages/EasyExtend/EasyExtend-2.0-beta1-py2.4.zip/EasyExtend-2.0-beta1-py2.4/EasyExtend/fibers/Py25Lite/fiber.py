from conf import*       # fiber specific modules ( symbol, token ) and objects ( prompt, pprint, unparse ...)
import EasyExtend       # EasyExtend package
import PyGrammar        # contains fiber specific DFA tables used by the parser
from EasyExtend.csttools import*   # tools used to manipulate CSTs
from EasyExtend.eetransformer import*   # node transformer
from EasyExtend.parser.PyParser import PyParser
import copy
import random
from EasyExtend.fibers.macro import fiber as macro_fiber

from builtins import any, all

class FinallyException(Exception):
    '''
    Exception class for tokenization failures.
    '''

class GeneratorExit(Exception):
    '''
    Request that a generator exit.
    '''

class YieldResult(Exception):   # new in Py25Lite
    '''
    Request for last computed value in a stream.
    '''

def puts(s):
    print s

class GVar:
    def __init__(self):
        self.value = None
        self.throw = None
        self.close = None

    def __getitem__(self, item):
        return self.__dict__[item]

    def __setitem__(self, item, value):
        self.__dict__[item] = value

class EnhancedGenerator(object):
    def __init__(self, gen):
        self.gen_func = gen
        self.started  = False

    class ClosedGenerator:
        def next(self):
            raise StopIteration
        def send(self, value):
            raise StopIteration

    def __call__(self, *args, **kwd):
        self.gvar = GVar()
        kwd["gvar"] = self.gvar
        self.gen = self.gen_func(*args, **kwd)
        return self

    def next(self):
        if not self.started:
            self.started = True
        val = self.gen.next()
        self.gvar["value"] = None
        return val

    def send(self, value):
        if not self.started:
            raise TypeError("can't send non-None value to a just-started generator")
        self.gvar["value"] = value
        return self.next()

    def throw(self, type, value=None, traceback=None):
        self.close()
        raise type, value, traceback

    def close(self):
        try:
            self.gen.next()   # one last shot
        except StopIteration:
            pass
        self.gen = self.ClosedGenerator()

    def __iter__(self):
        return self.gen

def enhanced_generator(func):
    def fn(*args, **kwd):
        eg = EnhancedGenerator(func)
        return eg(*args, **kwd)
    fn.__name__ = func.__name__
    return fn

import sys

# used by try...finally transformation
finally_exc_block ='''
if 1:
    exc_cls, exc_value, exc_tb = sys.exc_info()
    if exc_cls == FinallyException:
        fin_exc_cls, fin_exc_value, fin_exc_tb = exc_value[0]
        raise fin_exc_cls, fin_exc_value, fin_exc_tb
    else:
        FINALLY_BLOCK
    raise exc_cls, exc_value, exc_tb
'''
finally_exc = find_node(PyParser.suite(finally_exc_block).tolist(), symbol.suite)  # no macro transformation needed

counter = 0

def decompose_yield(suite_node, tl_node, k):
    pass


class FiberTransformer(Transformer):
    '''
    Defines fiber specific transformations
    '''

    @transform
    def test(self, node):
        "test: or_test ['if' or_test 'else' test] | lambdef"
        if not find_node(node, symbol.or_test, level=1):
            return
        n = node[1:]
        E1 = n[0]
        E1[0] = symbol.test   # old_test
        if len(n)>1:
            E2 = n[2]
            E2[0] = symbol.test
            E3 = n[4]
            T1 = CST_Tuple(E1,True)
            T2 = CST_Tuple(E3,True)
            R = any_test(CST_Subscript(CST_Or(CST_And(E2,T1), T2),Number(0)))  # (E2 and (E1,True) or (E3,True))[0]
            return R
        else:
            return E1

    @transform
    def or_test(self, node):
        "and_test ('or' and_test)*"
        node[0] = symbol.test
        return node

    @transform
    def old_test(self, node):
        node[1][0] = symbol.test
        return node_replace(node, node[1])

    @transform
    def funcdef(self, node):
        '''
        Used to transform enhanced_generators
        '''

        # if no yield expression is available being *not* defined within a closure
        # move on
        if not find_node(node, symbol.yield_expr, exclude = [symbol.funcdef]):
            return
        # extend funcdef node s.t. it supports @enhanced_generator decorator
        _enhanced_generator = decorator(dotted_name("enhanced_generator"))
        _decorators = find_node(node, symbol.decorators, level = 1)
        if _decorators:
            _decorators.append(_enhanced_generator)
        else:
            _decorators = decorators(_enhanced_generator)
            node.insert(1, _decorators)
        # extend the varargs signature to support keyword arguments
        _arglist = find_node(node, symbol.varargslist, level = 1)
        kwd_name = "kwd_"+func_name(node)
        if _arglist:
            if find_node(_arglist, token.DOUBLESTAR, level = 1):
                # we need to know the name of the kwd-dict
                for i,item in enumerate(_arglist[1:]):
                    if item[0] == token.DOUBLESTAR:
                        kwd_name = _arglist[1:][i+1][1]
            else:
                _arglist.append(Symbol(token.COMMA, ','))
                _arglist.append(Symbol(token.DOUBLESTAR, '**'))
                _arglist.append(Symbol(token.NAME,kwd_name))
        else:
            _new_params = parameters(varargslist('**', kwd_name))
            _params = find_node(node, symbol.parameters)
            del _params[:]
            _params+=_new_params

        _func_suite = normalize(find_node(node, symbol.suite))

        # insert gvar = kwd["gvar"]
        _assignment = any_stmt(CST_Assign("gvar", CST_Subscript(kwd_name, "'gvar'")))
        _func_suite.insert(3, _assignment)
        # seek for all suites that are *not* contained within a closure
        for _suite in find_all(node, symbol.suite, exclude = [symbol.funcdef]):
            if not find_node(_suite, symbol.yield_expr, exclude = [symbol.suite, symbol.funcdef]):
                continue
            new_suite = [symbol.suite]
            for item in _suite[1:]:
                if self.is_node(item, symbol.stmt) and find_node(item, symbol.yield_expr):
                    _expr_stmt = find_node(item, symbol.expr_stmt, level = 2)
                    if _expr_stmt:
                        _yield_expr = find_node(_expr_stmt, symbol.yield_expr)
                        if _yield_expr:
                            if count_node(_expr_stmt, symbol.yield_expr)>1:
                                raise NotImplementedError("Does not support combinations of yield expressions in: %s"%unparse(_expr_stmt))
                            _yield_expr[0] = symbol.yield_stmt
                            if not find_node(_yield_expr, symbol.testlist):
                                _yield_expr.insert(2,testlist(any_test(Name("None"))))
                            new_suite.append(any_stmt(_yield_expr))
                            _expr_stmt = copy.deepcopy(_expr_stmt)
                            if find_node(_expr_stmt, token.EQUAL):
                                _yield_stmt = find_node(_expr_stmt, symbol.yield_stmt, level = 1)
                                if _yield_stmt:
                                    node_replace(_yield_stmt, testlist(any_test(CST_Subscript("gvar", "'value'"))))
                                else:
                                    replace_in(_expr_stmt, symbol.yield_stmt, symbol.atom, atomize(CST_Subscript("gvar", "'value'")))
                            else:
                                replace_in(_expr_stmt, symbol.yield_stmt, symbol.atom, atomize(CST_Subscript("gvar", "'value'")))
                            new_suite.append(any_stmt(_expr_stmt))
                            continue
                    else:
                        _yield_stmt = find_node(item, symbol.yield_stmt)
                        if _yield_stmt:
                            left_shift(_yield_stmt) # yield_expr
                            _yield_stmt[0] = symbol.yield_stmt
                            if not find_node(_yield_stmt, symbol.testlist):
                                _yield_stmt.insert(2,testlist(any_test(Name("None"))))
                new_suite.append(item)
            node_replace(_suite, new_suite)


    @transform
    def try_stmt(self, node):
        """
        try_stmt: ('try' ':' suite
                   ((except_clause ':' suite)+ ['else' ':' suite] ['finally' ':' suite] |
                   'finally' ':' suite))
        """
        # transform try-stmt when
        # 1) A yield_expr is inside of a try...finally block
        # 2) try...except...finally are combined

        # first check for finally clause...
        for item in find_all(node, token.NAME, level=1):
            if item[1] == 'finally':
                break
        else:
            # no finally clause
            return
        if not find_node(node, symbol.except_clause, level=1):
            if not find_node(node, symbol.yield_stmt, exclude = [symbol.funcdef, symbol.lambdef]):
                # finally according to Python 2.4 rules -> o.k.
                return
        _try_suite = [find_node(node, symbol.suite)]
        _except = []
        _else   = []
        i = 4
        while i<len(node):
            item = node[i]
            if self.is_node(item,symbol.except_clause):
                _except.append(node[i+2])
                i+=3
            elif self.is_node(item,token.NAME) and item[1] == 'else':
                _else = [node[i+2]]
                i+=3
            elif self.is_node(item, token.NAME) and item[1] == 'finally':
                _finally = node[i+2]
                break

        # raise FinallyException(sys.exc_info())
        r = any_test(CST_CallFunc("FinallyException",[CST_CallFunc("sys.exc_info",[])]))
        _finally_except_suite = suite(any_stmt(raise_stmt(r)))
        FINALLY_BLOCK = any_stmt(try_stmt(_finally, except_clause(any_test(Name("Exception"))), _finally_except_suite))

        # for each try...except...else block seek for break, return and continue statements and insert a finally block before them
        # unless these flow statements occur in for or while statements class definitions and closures. Put a finally block at the end
        # of each toplevel block.
        if not _else:
            _blocks = _try_suite+_except
        else:
            _blocks = _except+_else
        while _blocks:
            block = _blocks.pop()
            if block[1][0] == symbol.simple_stmt:
                if find_one_of(block,[symbol.break_stmt, symbol.continue_stmt, symbol.return_stmt]):
                    _suite = suite(*[FINALLY_BLOCK, any_stmt(block[1])])
                else:
                   _suite = suite(*[any_stmt(block[1]), FINALLY_BLOCK])
                del block[:]
                block+=_suite
            else:
                n = len(block)
                for i in range(n)[:0:-1]:
                    stm = block[i]
                    if find_node(stm, symbol.flow_stmt):
                        if stm[1][0] == symbol.compound_stmt:
                            # be carefull when you define new statements in subfibers
                            if stm[1][1][0] not in ( symbol.funcdef, symbol.classdef):
                                _suite = find_node(stm, symbol.suite)
                                _blocks.append(_suite)
                        else:
                            if find_one_of(stm,[symbol.break_stmt, symbol.continue_stmt, symbol.return_stmt]):
                                block.insert(i, FINALLY_BLOCK)
                block.insert(len(block)-1, FINALLY_BLOCK)
        except_for_finally = copy.deepcopy(finally_exc)
        finally_block = find_all(except_for_finally, symbol.suite)[2]
        del finally_block[:]
        finally_block+=suite(FINALLY_BLOCK)
        if _except == []:
            _inner_try = find_node(node,symbol.suite)
        else:
            _inner_try = suite(any_stmt(node[:-3]))
        res = try_stmt(_inner_try,except_clause(any_test(Name("Exception"))),except_for_finally)
        del node[:]
        node+=res
        return res


    @transform
    def with_stmt(self, node):
        '''
        with_stmt: 'with' test [ with_var ] ':' suite
        with_var: ('as' | NAME) expr
        '''
        _EXPR  = find_node(node, symbol.test)
        _BLOCK = find_node(node, symbol.suite, level = 1)
        if find_node(_BLOCK, symbol.pass_stmt, level = 2):
            _BLOCK = normalize(_BLOCK)

        _with_var = find_node(node, symbol.with_var)
        if _with_var:
            if len(_with_var)<3:
                _VAR = any_test(_with_var[1])
            else:
                _VAR = any_test(_with_var[2])
        else:
            _VAR = any_test(new_name("VAR_"))

        target="""
        mgr   = (<EXPR>)
        <exit>  = mgr.__exit__  # Not calling it yet
        <value> = mgr.__enter__()
        <exc> = True
        try:
            try:
                optional <VAR>:
                    <VAR> = <value>  # Only if "as VAR" is present
                #<VAR> = <value>
                <BLOCK>
            except:
                # The exceptional case is handled here
                <exc> = False
                if not <exit>(*sys.exc_info()):
                    raise
                # The exception is swallowed if exit() returns true
        finally:
            # The normal and non-local-goto cases are handled here
            if <exc>:
                <exit>(None, None, None)
        """

        cst = macro_fiber.macro(target, self).expand({"exc": any_test(new_name("exc_")),
                                                      "exit": any_test(new_name("exit_")),
                                                      "value": any_test(new_name("value_")),
                                                      "BLOCK":_BLOCK,
                                                      "VAR":_VAR,
                                                      "EXPR":_EXPR},
                                                      returns = symbol.compound_stmt)
        return cst



__publish__ = ["any","all","enhanced_generator","sys","FinallyException", "GeneratorExit", "YieldResult","puts"]

if __name__ == '__main__':
    import fiber
    (options,args) = opt.parse_args()
    fiber.options   = options.__dict__
    #args = [r"test\test_with2.py"]
    if args:
        py_module = args[-1]
        #import profile
        #profile.run("EasyExtend.run_module(py_module, fiber, **options.__dict__)")
        EasyExtend.run_module(py_module, fiber)
    else:
        console = EasyExtend.create_console(fiber.fiber_name, fiber)
        console.interact()

