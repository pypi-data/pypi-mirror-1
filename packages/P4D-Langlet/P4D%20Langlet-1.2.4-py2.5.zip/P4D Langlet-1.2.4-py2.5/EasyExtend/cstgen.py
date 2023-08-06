from cst import*


def CST_Comparison(arg1, op, arg2):
    "Comparison: expr comp_op expr -> test"
    expr1 = find_node(wrap_arg(arg1), py_symbol.expr)
    expr2 = find_node(wrap_arg(arg2), py_symbol.expr)
    return any_test(comparison(expr1, comp_op(op), expr2))


def CST_Assign(name, value):
    "CST_Assign: expr (',' expr)* '=' expr (',' expr)*  -> expr_stmt"
    if isinstance(name, str):
        arg1 = testlist(any_test(Name(name)))
    else:
        arg1 = testlist(any_test(name))
    arg2 = testlist(wrap_arg(value))
    return expr_stmt(arg1,'=',arg2)

def CST_AugAssign(var, augass, val):
    "CST_AugAssign: expr augassign expr   -> expr_stmt"
    v1 = testlist(any_test(Name(var)))
    v2 = testlist(any_test(val))
    if isinstance(augass, list):
        op = augass
    else:
        op = augassign(augass)
    return expr_stmt(v1,op,v2)


def CST_Power(a, n):
    "Power: atom factor -> power"
    return power(any_node(a, py_symbol.atom), any_node(n, py_symbol.factor))

def CST_Add(fst, snd, *args):
    "Add: term ('+' term)+ -> arith_expr"
    addargs = []
    allargs = [fst,snd]+list(args)
    for item in allargs[:-1]:
        addargs.append(any_node(item, py_symbol.term))
        addargs.append("+")
    addargs.append(any_node(allargs[-1], py_symbol.term))
    return arith_expr(*addargs)


def CST_Sub(fst, snd, *args):
    "Sub: term ('-' term)+ -> arith_expr"
    addargs = []
    allargs = [fst,snd]+list(args)
    for item in allargs[:-1]:
        addargs.append(any_node(item, py_symbol.term))
        addargs.append("-")
    addargs.append(any_node(allargs[-1], py_symbol.term))
    return arith_expr(*addargs)


def CST_Mul(fst, snd, *args):
    "Mul: factor ('+' factor)+ -> term"
    addargs = []
    allargs = [fst,snd]+list(args)
    for item in allargs[:-1]:
        addargs.append(any_node(item, py_symbol.factor))
        addargs.append("*")
    addargs.append(any_node(allargs[-1], py_symbol.factor))
    return term(*addargs)


def CST_Div(fst, snd, *args):
    "CST_Div: factor ('/' factor)+ -> term"
    addargs = []
    allargs = [fst,snd]+list(args)
    for item in allargs[:-1]:
        addargs.append(any_node(item, py_symbol.factor))
        addargs.append("/")
    addargs.append(any_node(allargs[-1], py_symbol.factor))
    return term(*addargs)

def CST_FloorDiv(fst, snd, *args):
    "CST_FloorDiv: expr ( '//' expr)+ -> expr"
    addargs = []
    allargs = [fst,snd]+list(args)
    for item in allargs[:-1]:
        addargs.append(any_node(item, py_symbol.factor))
        addargs.append("//")
    addargs.append(any_node(allargs[-1], py_symbol.factor))
    return term(*addargs)

def CST_BitAnd(fst, snd, *args):
    "CST_BitOr: expr ( '&' expr)+ -> expr"
    allargs = [any_node(arg, py_symbol.shift_expr) for arg in [fst,snd]+list(args)]
    return and_expr(*allargs)

def CST_BitOr(fst, snd, *args):
    "CST_BitOr: expr ( '|' expr)+ -> expr"
    allargs = [any_node(arg, py_symbol.xor_expr) for arg in [fst,snd]+list(args)]
    return expr(*allargs)

def CST_BitXor(fst, snd, *args):
    "CST_BitXor: expr ( '^' expr)+ -> expr"
    allargs = [any_node(arg, py_symbol.and_expr) for arg in [fst,snd]+list(args)]
    return xor_expr(*allargs)

def CST_If(*args,**kwd):
    # TODO: to be finished
    #_else = kwd.get("_else")
    _ifargs = []
    for _t,_s in zip(args[::2],args[1::2]):
        _ifargs.append(any_test(_t))

def CST_Not(expr):
    "CST_Not: 'not' expr -> not_test"
    return not_test("not", any_node(expr, py_symbol.not_test))

def CST_And(fst,snd,*args):
    "CST_And: expr ( 'and' expr)+ -> and_test"
    allargs = [any_node(arg, py_symbol.not_test) for arg in [fst,snd]+list(args)]
    return and_test(*allargs)

def CST_Or(fst,snd,*args):
    "CST_And: expr ( 'or' expr)+ -> or_test"
    allargs = [any_node(arg, py_symbol.and_test) for arg in [fst,snd]+list(args)]
    return test(or_test(*allargs))

def CST_Del(*args):
    _args = []
    for arg in args:
        _args.append(any_node(arg, py_symbol.expr))
    return del_stmt(exprlist(*_args))

def CST_GetItem(name, arg):
    if isinstance(name, str):
        name = Name(name)
    return power(atom(name),trailer("[",subscriptlist(subscript(wrap_arg(arg))),"]"))

def CST_CallFuncWithArglist(name_or_atom, arglist):
    _params = trailer("(",arglist,")")
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


def CST_CallFunc(name_or_atom, args = [], star_args = None, dstar_args = None):
    '''
    Instead of a name an atom is allowed as well.
    '''
    _arglist = []
    for arg in args:
        if isinstance(arg,tuple):
            assert len(arg)==3, arg
            _param = [py_symbol.argument, any_test(Name(arg[0])),Symbol(py_token.EQUAL, '=')]
            _param.append(wrap_arg(arg[2]))
            _arglist.append(_param)
        else:
            _arglist.append(argument(wrap_arg(arg)))

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


def CST_GetAttr(expr, *args):
    '''
    (A(EXPR), B, C(EXPR), ...) -> CST (A(EXPR1).B.C(EXPR). ... ) of power
    '''
    if isinstance(expr, str):
        expr = Name(expr)
    trailers = []
    for arg in args:
        if isinstance(arg, str):
            trailers.append(trailer(".",Name(arg)))
        elif arg[0]%512 == 1:
            trailers.append(trailer(".", arg))
        else:
            call = find_node(arg, py_symbol.power)[1:]
            assert is_node(call[0], py_symbol.atom)
            trailers.append(".")
            trailers.append(call[0][1])
            for item in call[1:]:
                assert is_node(item, py_symbol.trailer)
                trailers.insert(0,item)
    return power(atom("(",testlist_gexp(any_test(expr)),")"),*trailers)

def CST_List(*args):
    '''
    CST_List: '[' ']' | '[' expr (',' expr)* ']'   -> atom
    '''
    if not args:
        return atom("[","]")
    else:
        return atom("[",listmaker(*[wrap_arg(arg) for arg in args]),"]")

def CST_Tuple(*args):
    '''
    CST_Tuple: '(' ')' | '(' expr (',' expr)* ')'   -> atom
    '''
    if not args:
        return atom("(",")")
    else:
        return atom("(",testlist_gexp(*([wrap_arg(arg) for arg in args]+[","])),")")

def CST_Dict(pairs = None, **dct):
    '''
    CST_Dict: '{' '}' | '{' expr ':' expr (',' expr ':' expr )* '}'   -> atom
    '''
    if dct:
        pairs = dct.items()
    if pairs is None:
        return atom("{","}")
    args = []
    for key, value in pairs:
        args.append(wrap_arg(key))
        args.append(wrap_arg(value))
    return atom("{",dictmaker(*args),"}")

def CST_ParametersFromSignature(sig):
    return CST_FuncParameters(sig['args'],
        defaults = sig['defaults'],
        star_args=sig['star_args'],
        dstar_args=sig['dstar_args'])

def CST_Lambda(body, argnames, defaults = {}, star_args=None, dstar_args=None):
    if argnames:
        _param = find_node(CST_FuncParameters(argnames, defaults, star_args, dstar_args), py_symbol.varargslist)
        if _param:
            return lambdef(_param, any_test(body))
    return lambdef((),any_test(body))

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
        _defaults+=[fpdef(Name(key)),wrap_arg(val)]
    _all = _argnames+_defaults+_star_args+_dstar_args
    if _all:
        return parameters(varargslist(*_all))
    else:
        return parameters()


def CST_Function(name, BLOCK, argnames, defaults={}, star_args=None, dstar_args=None):
    def _wrap_name(name):
        if isinstance(name, str):
            return Name(name)
        return name
    return any_stmt(funcdef(_wrap_name(name), CST_FuncParameters(argnames, defaults, star_args, dstar_args), BLOCK))

def CST_Subscript(expression, sub, *subs):
    '''
    Maps to expr[sub1,sub2,...,subn] only
    '''
    SUBSCR = [py_symbol.subscriptlist, subscript(wrap_arg(sub))]+[subscript(wrap_arg(arg)) for arg in subs]
    return power(atom('(',testlist_gexp(wrap_arg(expression)),')'),trailer('[',SUBSCR,']'))

def CST_Return(*args):
    '''
    (EXPR, EXPR, ... ) -> CST ( return_stmt )
    '''
    return return_stmt(testlist(*[wrap_arg(arg) for arg in args]))

def CST_Eval(arg):
    return eval_input(any_node(arg, py_symbol.testlist))

def CST_Except(arg1, arg2 = None):
    if arg2:
        return except_clause(wrap_arg(arg1),wrap_arg(arg2))
    else:
        return except_clause(wrap_arg(arg1))

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

def CST_Import(module):
    return import_name(dotted_as_names(dotted_as_name(dotted_name(*[mod for mod in module.split(".")]))))

def CST_ImportFrom(from_module, *names):
    path = dotted_name(*[Name(mod) for mod in from_module.split(".")])
    if names[0] == "*":
        return import_from(path, '*')
    else:
        return import_from(path, import_as_name(*names))

def CST_While(*args):
    arg = wrap_arg(args[0])
    return while_stmt(*((arg,)+args[1:]))

def CST_For(*args):
    raise NotImplementedError

def CST_ListComp(*args):
    return atom("[",listmaker(wrap_arg(args[0]), args[1]),"]")


# import late since cstgen is also used by csttools

from csttools import any_test, any_stmt, any_expr, any_node, find_node, power_merge, wrap_arg, is_node




