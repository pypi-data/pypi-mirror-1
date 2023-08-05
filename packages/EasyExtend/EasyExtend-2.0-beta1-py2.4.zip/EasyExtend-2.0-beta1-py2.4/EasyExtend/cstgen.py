'''
High level API for CST synthess.

This module is modelled after the AST node API ( see chap. 19.3.1 of the Python docs)
'''

from cst import*

def _wrap_arg(arg):
    if arg in (True, False):
        return any_test(Name(str(arg)))
    if isinstance(arg,int):
        return any_test(Number(arg))
    elif isinstance(arg,str):
        if arg[0] in ("'",'"'):
            return any_test(String(arg[1:-1]))
        else:
            return any_test(Name(arg))
    elif isinstance(arg,list):
        return any_test(arg)

def CST_Comparison(arg1, op, arg2):
    expr1 = find_node(_wrap_arg(arg1), py_symbol.expr)
    expr2 = find_node(_wrap_arg(arg2), py_symbol.expr)
    return any_test(comparison(expr1, comp_op(op), expr2))

def CST_Assign(name, value):
    if isinstance(name, str):
        arg1 = testlist(any_test(Name(name)))
    else:
        arg1 = testlist(any_test(name))
    arg2 = testlist(_wrap_arg(value))
    return expr_stmt(arg1,'=',arg2)

def CST_AugAssign(var, augass, val):
    v1 = testlist(any_test(Name(var)))
    v2 = testlist(any_test(val))
    if isinstance(augass, list):
        op = augass
    else:
        op = augassign(augass)
    return expr_stmt(v1,op,v2)

def CST_Power(a, n):
    return power(any_node(a, py_symbol.atom), any_node(n, py_symbol.factor))

def CST_Add(fst, snd, *args):
    addargs = []
    allargs = [fst,snd]+list(args)
    for item in allargs[:-1]:
        addargs.append(any_node(item, py_symbol.term))
        addargs.append("+")
    addargs.append(any_node(allargs[-1], py_symbol.term))
    return arith_expr(*addargs)

def CST_Sub(fst, snd, *args):
    addargs = []
    allargs = [fst,snd]+list(args)
    for item in allargs[:-1]:
        addargs.append(any_node(item, py_symbol.term))
        addargs.append("-")
    addargs.append(any_node(allargs[-1], py_symbol.term))
    return arith_expr(*addargs)

def CST_Mul(fst, snd, *args):
    addargs = []
    allargs = [fst,snd]+list(args)
    for item in allargs[:-1]:
        addargs.append(any_node(item, py_symbol.factor))
        addargs.append("*")
    addargs.append(any_node(allargs[-1], py_symbol.factor))
    return term(*addargs)

def CST_Div(fst, snd, *args):
    addargs = []
    allargs = [fst,snd]+list(args)
    for item in allargs[:-1]:
        addargs.append(any_node(item, py_symbol.factor))
        addargs.append("/")
    addargs.append(any_node(allargs[-1], py_symbol.factor))
    return term(*addargs)

def CST_FloorDiv(fst, snd, *args):
    addargs = []
    allargs = [fst,snd]+list(args)
    for item in allargs[:-1]:
        addargs.append(any_node(item, py_symbol.factor))
        addargs.append("//")
    addargs.append(any_node(allargs[-1], py_symbol.factor))
    return term(*addargs)

def CST_BitAnd(fst, snd, *args):
    allargs = [any_node(arg, py_symbol.shift_expr) for arg in [fst,snd]+list(args)]
    return and_expr(*allargs)

def CST_BitOr(fst, snd, *args):
    allargs = [any_node(arg, py_symbol.xor_expr) for arg in [fst,snd]+list(args)]
    return expr(*allargs)

def CST_BitXor(fst, snd, *args):
    allargs = [any_node(arg, py_symbol.and_expr) for arg in [fst,snd]+list(args)]
    return xor_expr(*allargs)

def CST_If(*args,**kwd):
    _else = kwd.get("_else")
    _ifargs = []
    for _t,_s in zip(args[::2],args[1::2]):
        _ifargs.append(any_test(_t))

def CST_Not(expr):
    return not_test("not", any_node(expr, py_symbol.not_test))

def CST_And(fst,snd,*args):
    allargs = [any_node(arg, py_symbol.not_test) for arg in [fst,snd]+list(args)]
    return and_test(*allargs)

def CST_Or(fst,snd,*args):
    allargs = [any_node(arg, py_symbol.and_test) for arg in [fst,snd]+list(args)]
    return test(*allargs)

def CST_Del(*args):
    _args = []
    for arg in args:
        _args.append(any_node(arg, py_symbol.expr))
    return del_stmt(exprlist(*_args))

def CST_GetItem(name, arg):
    if isinstance(name, str):
        name = Name(name)
    return power(atom(name),trailer("[",subscriptlist(subscript(_wrap_arg(arg))),"]"))


def CST_CallFunc(name_or_atom, args = [], star_args = None, dstar_args = None):
    '''
    Instead of a name an atom is allowed as well.
    '''
    _arglist = []
    for arg in args:
        if isinstance(arg,tuple):
            assert len(arg)==3
            _param = [py_symbol.argument, any_test(Name(arg[0])),Symbol(py_token.EQUAL, '=')]
            _param.append(_wrap_arg(arg[2]))
            _arglist.append(_param)
        else:
            _arglist.append(argument(_wrap_arg(arg)))

    "arglist: (argument ',')* (argument [',']| '*' test [',' '**' test] | '**' test) "
    if star_args:
        _arglist.append('*')
        _arglist.append(any_test(star_args))
    if dstar_args:
        _arglist.append('**')
        _arglist.append(any_test(dstar_args))
    if _arglist:
        _params = trailer("(",arglist(*_arglist),")")
    else:
        _params = trailer("(",")")
    if isinstance(name_or_atom, list):
        if name_or_atom[0]%512 == py_symbol.atom:
            _args = [name_or_atom]+[_params]
        elif name_or_atom[0]%512 == py_token.NAME:
            _args = [atom(name_or_atom)]+[_params]
        else:
            raise ValueError("Cannot handle function name %s"%name_or_atom)
        return power(*_args)
    elif name_or_atom.find(".")>0:
        names = name_or_atom.split(".")
        _args = [atom(Name(names[0]))]+[trailer(".",n) for n in names[1:]]+[_params]
        return power(*_args)
    else:
        return power(atom(Name(name_or_atom)),_params)


def CST_GetAttr(expr, name):
    '''
    (EXPR, str | NAME ) -> CST (expr.name) of power
    '''
    if isinstance(name, str):
        name = Name(name)
    elif name[0] == 1:
        pass
    else:
        name = any_node(name, py_token.NAME)
    return power(atom("(",testlist_gexp(any_test(expr)),")"),trailer(".",name))

def CST_List(*args):
    '''
    (EXPR, EXPR, ...) -> CST( [] ) of atom
    '''
    if not args:
        return atom("[","]")
    else:
        return atom("[",[py_symbol.listmaker]+[_wrap_arg(arg) for arg in args],"]")

def CST_Tuple(*args):
    '''
    (EXPR, EXPR, ...) -> CST( () ) of atom
    '''
    if not args:
        return atom("(",")")
    else:
        return atom("(",testlist_gexp(*([_wrap_arg(arg) for arg in args]+[","])),")")

def CST_Dict(**dct):
    '''
    {EXPR:EXPR, ...) -> CST( {} ) of atom
    '''
    if not dct:
        return atom("{","}")
    args = []
    for key, value in dct.items():
        args.append(_wrap_arg(key))
        args.append(_wrap_arg(value))
    return atom("{",dictmaker(*args),"}")

def CST_ParametersFromSignature(sig):
    return CST_FuncParameters(sig['args'],
        defaults = sig['defaults'],
        star_args=sig['star_args'],
        dstar_args=sig['dstar_args'])


def CST_FuncParameters(argnames, defaults = {}, star_args=None, dstar_args=None):
    def _wrap_name(name):
        if isinstance(name, str):
            return Name(name)
        return name

    _argnames = [fpdef(_wrap_name(arg)) for arg in argnames]
    _star_args= []
    if star_args:
        _star_args = ['*', star_args]
    _dstar_args= []
    if dstar_args:
        _dstar_args = ['**', dstar_args]
    _defaults = []
    for key,val in defaults.items():
        _defaults+=[fpdef(Name(key)),_wrap_arg(val)]
    _all = _argnames+_defaults+_star_args+_dstar_args
    return parameters(varargslist(*_all))


def CST_Function(name, SUITE, argnames, defaults={}, star_args=None, dstar_args=None):
    return any_stmt(funcdef(name, CST_FuncParameters(argnames, defaults, star_args, dstar_args), SUITE))

def CST_Subscript(expression, sub, *subs):
    '''
    Maps to expr[sub1,sub2,...,subn] only
    '''
    SUBSCR = [py_symbol.subscriptlist, subscript(_wrap_arg(sub))]+[subscript(_wrap_arg(arg)) for arg in subs]
    return power(atom('(',testlist_gexp(_wrap_arg(expression)),')'),trailer('[',SUBSCR,']'))

def CST_Return(*args):
    '''
    (EXPR, EXPR, ... ) -> CST ( return_stmt )
    '''
    return reture_stmt(testlist(*[_wrap_arg(arg) for arg in args]))

def CST_Eval(arg):
    return eval_input(any_node(arg, py_smbol.testlist))

def CST_Except(arg1, arg2 = None):
    if arg2:
        return except_clause(_wrap_arg(arg1),_wrap_arg(arg2))
    else:
        return except_clause(_wrap_arg(arg1))

def CST_TryExcept(try_suite, else_suite = None, *args):
    assert len(args)%2 == 0, "pairs of (except_clause, suite) expected"
    try_except_args = [try_suite]
    for i in range(len(args))[::2]:
        arg = args[i]
        if isinstance(arg, list):
            if arg%512 == py_symbol.except_clause:
                try_except_args.append(arg)
            else:
                try_except_args.append(CST_Except(arg))
        try_except_args.append(args[i+1])
    if else_suite:
        try_except_args.append(else_suite)
    return try_stmt(*try_except_args)


def CST_TryFinally(try_suite, finally_suite):
    return try_stmt(try_suite, 'finally', finally_suite)

def CST_Import(*args):
    raise NotImplementedError

def CST_While(*args):
    raise NotImplementedError

def CST_For(*args):
    raise NotImplementedError

def CST_ListComp(*args):
    raise NotImplementedError


# import late since cstgen is also used by csttools

from csttools import any_test, any_stmt, any_expr, any_node, find_node, power_merge
