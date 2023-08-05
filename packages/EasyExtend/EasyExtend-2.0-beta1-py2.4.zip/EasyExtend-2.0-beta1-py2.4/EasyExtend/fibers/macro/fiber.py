from conf import*
import EasyExtend   # EasyExtend package
import PyGrammar    # contains fiber specific DFA tables used by the parser
from EasyExtend.csttools import*
from EasyExtend.eetransformer import*
from EasyExtend.eecompiler import EECompiler
from EasyExtend.parser.PyParser import PyParser
import copy
import random
import sys


# This class is for type inspection only.
class node_wrapped:
    def __init__(self, node):
        self.node = node

class Tunnel(object):
    def __init__(self):
        self._items = {}

    def push_single(self, key, node):
        self._items[key] = node
        return CST_CallFunc("self.tunnel.keep_node",[key])

    def push_double(self, key, node):
        self._items[key] = node_wrapped(node)
        return CST_CallFunc("self.tunnel.keep_node",[key])

    def keep_node(self, key):
        return self._items[key]


class macro(object):
    eecompiler = None
    interactive = False
    def __init__(self, target, transformer=None):
        if callable(target):
            try:
                target = target.__doc__
            except AttributeError:
                raise TypeError, "Callable not adaequate to represent source code"
        self.foreign_trans = transformer
        self._issuite = (target.find("\n")>=0)
        self.target = prepare_source(target)
        import fiber
        self.fiber = fiber
        self.eecompiler = EECompiler(fiber)

    def expand(self, symbol_map, locals = {}, returns = None, **kwd):
        for key,val in symbol_map.items():
            if val:
                symbol_map[key] = list(val)
        if self._issuite:
            cst = self.eecompiler.eeparse_suite(self.target)
        else:
            cst = self.eecompiler.eeparse_expr(self.target)
        kwd["symbol_map"] = symbol_map
        kwd["locals"]     = locals
        kwd["foreign"]    = self.foreign_trans
        if self.interactive:
            transformer = InteractiveTransformer(self.fiber, **kwd)
        else:
            transformer = FiberTransformer(self.fiber, **kwd)
        # print "DEBUG: expand", transformer
        stmts = find_all(cst, symbol.stmt, level=0)
        if len(stmts)>1:                                                    # only single statements can be
            cst = any_stmt(if_stmt(any_test(Name("True")),suite(*stmts)))   # handled by the expander.
            transformer.run(cst)
            # cst = find_node(cst, symbol.suite)
        else:
            transformer.run(cst)
        transformer.terminate()
        if returns:
            res = find_node(cst, returns)
            if res:
                return res
            else:
                raise ValueError, "cannot return node of type '%s' after macro expansion"%returns
        return cst

def meval(source, **kwd):
    from EasyExtend.parser.PyParser import PyParser
    for key, val in kwd.items():
        if isinstance(val, (tuple, list)):
            kwd[key] = [find_node(PyParser.expr(X).tolist(), py_symbol.test) for X in val]
        else:
            kwd[key] = find_node(PyParser.expr(val).tolist(), py_symbol.test)
    return unparse(macro(source).expand(kwd, globals())).strip()


def listify(*args):
    '''
    @param *args: argument tuple.
    '''
    return list(args)

from EasyExtend.parser.PyParser import PyParser

def env(arg):
    '''
    @param arg: argument to be wrapped into test node.
    @type arg: One of int, long, str, list, tuple, dict, NoneType.
    '''
    if isinstance(arg, (int, long, float)):
        return any_test(Number(arg))
    elif isinstance(arg, basestring):
        return any_test(String(arg))
    elif isinstance(arg, (list, tuple, dict)):
        return find_node(PyParser.expr(str(arg)).tolist(), py_symbol.test)
    elif arg in (None, True, False):
        return any_test(Name(str(arg)))
    else:
        raise TypeError, "Type %s of %s not supported by env."%(type(arg), arg)


__publish__ = ["macro", "prepare_source", "listify", "env"]

class FiberTransformer(Transformer):
    '''
    Defines fiber specific transformations
    '''
    tunnel = Tunnel()
    def __init__(self, fiber, **kwd):
        super(FiberTransformer,self).__init__(fiber, **kwd)
        self.symbol_map   = kwd.get("symbol_map",{})
        self._double_wrap = kwd.get("wrap")
        self.foreign      = kwd.get("foreign")
        self._locals      = kwd.get("locals",{})
        self._locals.update(self.fiber.__dict__)
        #self.tunnel = Tunnel()
        self._single_wrap = False

    def do_tunnel(self, nvar_value, double = False):
        key = int(10000000*random.random())
        if double:
            return self.tunnel.push_double(key, nvar_value)
        else:
            return self.tunnel.push_single(key, nvar_value)

    def notify(self):
        if self.symbol_map:
            return super(FiberTransformer, self).notify()
        return False

    @transform
    def cit(self, node, locals = {}):
        "cit: 'cit' '(' test ')'"
        locals.update(self._locals)
        locals["self"] = self
        _test = node[2]
        # node_var is of type atom. We likely cannot replace node_var by a statement/expression
        # within power by another atom. Therefore we tunnel the nvar_val within a tunnel.keep_node function
        # call which is of type power. Then we merge this power node with the power node containing the node_var
        # that was just transformed.
        for nodeA in find_all(_test, symbol.power):
            if find_node(nodeA, symbol.node_var, level=1):
                nodeB = nodeA[:]
                facNB = [symbol.factor,nodeB]
                self._single_wrap = True
                self.run(facNB)
                self._single_wrap = False
                nodeC = power_merge(nodeA, facNB[1])
                nodeA[1:] = nodeC[1:]
        self.run(_test)
        code = unparse(_test).strip()
        try:
            res  = eval(code, locals)
            # used by transform_as_if_stmt
            if self._double_wrap:
                res  = self.do_tunnel(res, double=True)
        except Exception, e:
            #print "DEBUG", _test
            raise ValueError, str(e)+"\nCannot evaluate code: %s"%code
        return make_node(res)

    @transform
    def argument(self, node):
        "argument: cit | [test '='] test [gen_for] # Really [keyword '='] test"
        # we need to care for carefull replacement of cit.
        if self.is_node(node[1], symbol.cit):
            cit_node = any_test([symbol.atom,node[1]])
            self.run(testlist(cit_node))
            return argument(cit_node)

    @transform
    def node_var(self, node):
        '''
        node_var: '<' NAME '>'
        '''
        assert self.symbol_map != {}, "symbol_map empty. Transformer not properly initialized"
        nvar_name  = node[2][1]

        # <*x> -> listify(*<x>)
        if nvar_name == '*':
            del node[2]
            n = [symbol.atom, node]
            _listified = CST_CallFunc("listify",star_args=n)
            self.run(_listified)
            return _listified

        nvar_value = self.symbol_map.get(nvar_name)
        if not nvar_value:
            raise ValueError, "node %s not found"%nvar_name
        if self._single_wrap:
            return self.do_tunnel(nvar_value)
        if self.contains_node(nvar_value, (symbol.expr, symbol.test)):
            return atomize(nvar_value)
        if self.is_node(nvar_value, symbol.suite):
            # print "DEBUG", "node_var out",pprint(target)
            return tuple(find_all(nvar_value, symbol.stmt, level = 0))
        return nvar_value

    @transform
    def arglist(self, node):
        '''
        Replace func(*<test>) by expansion of <test>:

                func(<test>[1], <test>[2], ..., <test>[k])

        Also replace func(<*test>) by expansion of <test>:

                func([<test>[1], <test>[2], ..., <test>[k]])

        The same effect can be achieved using listify():

                func(listify(*<test>))  ==>  func([<test>[1], <test>[2], ..., <test>[k]])
        '''
        # sprint "DEBUG", "arglist",node
        if find_node(node, symbol.node_var):
            for i,sub in enumerate(node[1:]):
                if self.is_node(sub, token.STAR):
                    _node_var = find_node(node[1:][i+1], symbol.node_var)
                    if _node_var:
                        name = find_node(_node_var, token.NAME, level=1)[1]
                        if self.symbol_map == {}:
                            raise ValueError, "symbol_map empty. Transformer not properly initialized"
                        target = self.symbol_map.get(name)
                        n = len(target)
                        args = []
                        del node[i+1:i+3]
                        for k in range(n)[::-1]:
                            T = any_test(power([symbol.atom,_node_var],trailer("[",subscriptlist(subscript(any_test(Number(k)))),"]")))
                            arg = self.cit([symbol.cit,Name('cit'),T])
                            node.insert(i+1,[token.COMMA,","])
                            node.insert(i+1,argument(any_test(arg)))
                    break

    @transform
    def suite(self, node):
        """
        Run optional statement if available and add appropriate semi-statements to compound statement.
        Finally remove optional_stmt node.
        """                                                    #         L1        L2          L3
        if find_node(node, symbol.optional_stmt, level = 3):   # suite->stmt->compound_stmt->optional_stmt
            _stmts = []
            this_stmts = find_all(node, symbol.stmt, level = 1)
            for i, _stmt in enumerate(this_stmts):
                _optional = find_node(_stmt, symbol.optional_stmt, level=1)
                if _optional:
                    for sub in self.optional_stmt(_stmt):
                        self.run(any_stmt(sub))
                        _semi_stmt = find_node(sub, symbol.semi_stmt, level = 1)
                        if _semi_stmt:
                            try:
                                last = _stmts[-1]
                                compound = find_one_of(last, ( symbol.if_stmt, symbol.for_stmt,
                                                               symbol.try_stmt, symbol.while_stmt ),
                                                       level = 1)
                                compound+=_semi_stmt[1][1:]
                            except (TypeError, IndexError):
                                raise TranslationError, "No corresponding compound statement found for semi-stmt"
                        else:
                            _stmts.append(sub)
                    remove_node(node, _optional, level=1)
                else:
                    _stmts.append(_stmt)
            node = suite(*_stmts)


    @transform
    def optional_stmt(self, node):
        "optional_stmt: 'optional' exprlist ['in' testlist] ':' suite"
        #print "DEBUG", "optional_stmt",node
        if find_node(node, symbol.testlist, level=2):
            return self.transform_as_for_stmt(node)
        else:
            return self.transform_as_if_stmt(node)


    def transform_as_for_stmt(self, node):
        """
        1) Transform the part 'exprlist in testlist' into a listcomp and evaluate it.
           Example:
                 optional i in range(cit len(<test>))

                               ===>

                 [i for i in range(cit len(<test>))]

        2) Macro-expand the listcomp, compile it and evaluate it.

        3) The 'suite' of the optional statement is parametrized by the items of the evaluated
           listcomp. The listcomp is turned into a list of local variables.

           Example:                                    eval.retrans.expand
               [i for i in range(cit len(<test>))]  ---------------------> [0,1,2]
                                                       make-var
                                     [0,1,2]          ---------->   [{'i':0}, {'i':1}, {'i':2}]

        4) Expand suite 3-times with var = {'i': j}, j in [0,1,2]
           and return the expanded suites.
        """
        _testlist = find_node(node, symbol.testlist)
        _exprlist = find_node(node, symbol.exprlist)
        exl = unparse(_exprlist).strip()
        tl  = unparse(_testlist).strip()
        varnames  = [s.strip() for s in exl.split(",")]
        variables = []
        try:
            S = macro("[(%s) for %s in %s ]"%(exl,exl,tl)).expand(self.symbol_map, locals = self._locals, wrap = True)
            items = eval(unparse(S).strip())
        except TypeError:
            S = macro("[(%s) for %s in %s ]"%(exl,exl,tl)).expand(self.symbol_map, locals = self._locals)
            items = eval(unparse(S).strip())
        for j,item in enumerate(items):
            if type(item) == type(()):
                newvar = {}
                for i, part in enumerate(item):
                    if isinstance(part, node_wrapped):
                        part = part.node
                    newvar[varnames[i]] = part
                variables.append(newvar)
            elif isinstance(item, node_wrapped):
                variables.append( {varnames[0]:item.node} )
            else:
                variables.append( {varnames[0]:item} )
        return self.create_suite_versions(node, variables)


    def create_suite_versions(self, node, variables):
        res    = []
        _suite = find_node(node, symbol.suite)
        for var in variables:
            cloned_suite = copy.deepcopy(_suite)
            self.run(cloned_suite, locals=var)
            res+=find_all(cloned_suite, symbol.stmt, level = 1)
        # for item in res:
        #    unparse(item)
        return tuple(res)


    def transform_as_if_stmt(self, node):
        '''
        optional exprlist:
            SUITE

        Need to evaluate exprlist for determining whether SUITE is part of the surrounding statement.
        '''
        compile_exprlist = False
        _exprlist = find_node(node, symbol.exprlist)
        if find_node(_exprlist, symbol.cit):
            exl = unparse(_exprlist).strip()
            S = macro(exl, foreign=self.foreign).expand(self.symbol_map, locals = self._locals, wrap = True)
            cond = eval(unparse(S))
        else:
            # does node_var exist...?
            _nvar = find_node(_exprlist, symbol.node_var)
            if _nvar:
                name = find_node(_nvar, token.NAME, level=1)[1]
                if self.symbol_map.get(name):
                    cond = True
                else:
                    cond = False
            else:
                cond = eval(unparse(_exprlist))
        if cond:
            variables = [{}]
            return self.create_suite_versions(node, variables)
        return (any_stmt(pass_stmt()),)


class InteractiveTransformer(FiberTransformer):
    def __init__(self, *args, **kwd):
        macro.interactive = True
        super(InteractiveTransformer,self).__init__(*args, **kwd)

    def notify(self):
        return Transformer.notify(self)


if __name__ == '__main__':
    import fiber
    (options,args) = opt.parse_args()
    fiber.options   = options.__dict__
    if args:
        py_module = args[-1]
        EasyExtend.run_module(py_module, fiber)
    else:
        #from fibertest.test_macro3 import TestMacro5
        #m3 = TestMacro5()
        #m3.setUp()
        #m3.test_pure_option()
        #print meval("range(cit len(<test>))",test = ("0","2"))
        macro.interactive = True
        __publish__.append("meval")
        console = EasyExtend.create_console("MacroFiber", fiber)
        console.interact()


