'''
The cst module translates Python grammar rules into functions that can be combined
in order to create Python CSTs expressed in list form. The specification of each
function is therefore determined by the grammar rule string. This can be retrieved
from the docstring.

Example ::

   The grammar rule

             single_input:: NEWLINE | simple_stmt | compound_stmt NEWLINE

   is translated to a function single_input(*args) that accepts as input
   either the value NEWLINE(), a simple_stmt node or a
   compound_stmt node.

When the compound_stmt node is added you shall not add the NEWLINE node as
well because the presence can be deduced by the function from the grammar rule.

Any rule function checks each input node. They are implemented to be NOT
redundancy tolerant i.e. each terminal py_symbol that can be omitted shall be
omitted. Only those terminals that are necessary to establish more context
information are mandatory.

Examples ::

    funcdef: [decorators] 'def' NAME parameters ':' suite

        'def' and ':' shall be dropped

    fpdef: NAME | '(' fplist ')'

        '(' and ')' shall be dropped.

    raise_stmt: 'raise' [test [',' test [',' test]]]

        the 'raise' keyword as well as all colons shall be dropped

    import_from: 'from' dotted_name 'import' ('*' | '(' import_as_names ')' | import_as_names)

        The keywords 'from' and 'import' shall be dropped. Using either '*' '(' or import_as_names
        as subsequent py_symbol is mandatory.
'''

# URL:     http://www.fiber-space.de
# Author:  Kay Schluehr <easyextend@fiber-space.de>
# Date:    10 May 2006


import symbol as py_symbol
import token as py_token

MAX_PY_SYMBOL = 339          # maximal node_id of Python 2.5 symbols. Change this for other releases!
MAX_PY_TOKEN  = 60
LANGLET_OFFSET_SCALE = 512   # used to discriminate langlets
PY_NT_OFFSET = 256


# helper functions

def toText(node_id):
    '''
    Returns textual representation of a node id.
    '''
    assert isinstance(node_id, int), node_id
    div, rest = divmod(node_id, LANGLET_OFFSET_SCALE)
    if rest >= PY_NT_OFFSET:
        return py_symbol.sym_name[rest]
    else:
        return py_token.tok_name[rest]

def py_cst(f):
    '''
    Decorator used to filter arguments of cst module functions on langlet-specific nodes.
    If a node was found that could be projected into Pythons node range apply projection
    by LANGLET_OFFSET_SCALE.
    '''
    def cstfunc(*args):
        for arg in args:
            if isinstance(arg, list):
                if arg[0]>LANGLET_OFFSET_SCALE:
                    rest = arg[0]%LANGLET_OFFSET_SCALE
                    if rest<=MAX_PY_SYMBOL:
                        arg[0] = rest
        return f(*args)
    return cstfunc


class CSTBuilder(object):
    def __init__(self, langlet):
        import EasyExtend.trail.nfatracing as nfatools
        self.NFATracer = nfatools.NFATracer
        self.nfamodule = langlet.parse_nfa
        self.token     = langlet.parse_token
        self.symbol    = langlet.parse_symbol
        self.langlet   = langlet
        self.token_chars = dict((y,x) for (x,y) in self.token.token_map.items())

    def builder(self, nid, name, doc):
        #@py_cst
        def cstbuilder(*args):
            return self.build_cst(nid, *args)
        cstbuilder.__doc__ = doc
        cstbuilder.__name__= name
        return cstbuilder

    def factory(self):
        funcs = {}
        for attr in dir(self.symbol):
            val = getattr(self.symbol, attr)
            if isinstance(val, int):
                doc = self.nfamodule.nfas[val][1]
                funcs[attr] = self.builder(val, attr, doc)
        return funcs


    def build_cst(self, nid, *args):
        tracer = self.NFATracer(self.nfamodule.nfas)
        nodelist = [nid]
        i = 0
        s = nid
        while i<len(args):
            arg = args[i]
            selection = tracer.select(s)
            if arg[0] in selection:
                nodelist.append(arg)
                s = arg[0]
                i+=1
                continue
            Token = [a for a in selection if a is not None and ( isinstance(a,str) or a%512<256)]
            if len(Token) == 1:
                s = Token[0]
                if isinstance(s, str):
                    nodelist.append([1,s])
                else:
                    nodelist.append([s, self.token_chars[s]])
            elif arg in self.token.token_map.keys():
                s = self.token.token_map[arg]
                if s in selection:
                    nodelist.append([s, arg])
                else:
                    raise ValueError("Unexpected input argument '%s'. Selectable node ids are %s."%(arg, selection))
            else:
                raise ValueError("Unexpected input argument '%s'. Selectable node ids are %s."%(arg, selection))
            i+=1
        return nodelist


# some py_token wrappers

def Symbol(tok, sym):
    return [tok, sym]

def Name(name):
    return [py_token.NAME, name]

def Number(number):
    return [py_token.NUMBER, str(number)]

def String(string):
    return [py_token.STRING, '"'+string+'"']


# grammar node wrappers

@py_cst
def single_input(*args):
    '''single_input: NEWLINE | simple_stmt | compound_stmt NEWLINE'''
    nodelist = [py_symbol.single_input]
    if not args:
        nodelist.append(NEWLINE())
    elif args[0][0] == py_symbol.simple_stmt:
        nodelist.append(args[0])
    elif args[0][0] == py_symbol.compound_stmt:
        nodelist.append(args[0])
        nodelist.append(NEWLINE())
    else:
        raise ValueError,"args must be either empty a simple_stmt or a compound_stmt"
    return nodelist

@py_cst
def file_input(*args):
    '''file_input: (NEWLINE | stmt)* ENDMARKER'''
    nodelist = [py_symbol.file_input]
    for arg in args:
        if arg == "\n":
            nodelist.append(NEWLINE())
        elif arg[0] in ( py_symbol.stmt, py_token.NEWLINE):
            nodelist.append(arg)
        else:
            raise ValueError,"arg must be either NEWLINE or stmt. %s found"%(toText(arg[0]),)
    nodelist.append(NEWLINE())
    nodelist.append(ENDMARKER())
    return nodelist

@py_cst
def eval_input(*args):
    '''eval_input: testlist NEWLINE* ENDMARKER'''
    nodelist = [py_symbol.eval_input]
    assert args[0][0] == py_symbol.testlist, toText(args[0][0])
    nodelist.append(args[0])
    for arg in args[1:]:
        if arg == "\n":
            nodelist.append(NEWLINE())
        else:
            raise ValueError,"arg must be either '\n' a stmt. %s found"%(toText(arg[0]),)
    nodelist.append(ENDMARKER())
    return nodelist

@py_cst
def decorator(*args):
    """decorator: '@' dotted_name [ '(' [arglist] ')' ] NEWLINE"""
    nodelist = [py_symbol.decorator]
    assert args[0][0] == py_symbol.dotted_name, toText(args[0][0])
    nodelist.append(Symbol(py_token.AT,"@"))
    nodelist.append(args[0])
    if len(args)>1:
        assert args[1] == "("
        nodelist.append(Symbol(py_token.LPAR,"("))
        if not args[2] == ")":
            assert args[2][0] == py_symbol.arglist, toText(args[2][0])
            nodelist.append(args[2])
        nodelist.append(Symbol(py_token.RPAR,")"))
    nodelist.append(NEWLINE())
    return nodelist

@py_cst
def decorators(*args):
    '''decorators: decorator+'''
    nodelist = [py_symbol.decorators]
    assert len(args)
    for arg in args:
        assert arg[0] == py_symbol.decorator
        nodelist.append(arg)
    return nodelist

@py_cst
def funcdef(*args):
    """funcdef: [decorators] 'def' NAME parameters ':' suite"""
    nodelist = [py_symbol.funcdef]
    if args[0][0] == py_symbol.decorators:
        nodelist.append(args[0])
        args = args[1:]
    nodelist.append(Symbol(py_token.NAME, "def"))
    assert args[0][0] == py_token.NAME ,toText(args[0][0])
    nodelist.append(args[0])
    assert args[1][0] == py_symbol.parameters, toText(args[1][0])
    nodelist.append(args[1])
    nodelist.append(Symbol(py_token.COLON, ':'))
    assert args[2][0] == py_symbol.suite, toText(args[2][0])
    nodelist.append(args[2])
    return nodelist

@py_cst
def parameters(*args):
    "parameters: '(' [varargslist] ')'"
    nodelist = [py_symbol.parameters]
    nodelist.append( Symbol(py_token.LPAR, "("))
    if args:
        assert args[0][0] == py_symbol.varargslist, toText(args[0][0])
        nodelist.append( args[0] )
    nodelist.append( Symbol(py_token.RPAR, ")"))
    return nodelist

@py_cst
def varargslist(*args):
    """varargslist: (fpdef ['=' test] ',')* ('*' NAME [',' '**' NAME] | '**' NAME)
                  | fpdef ['=' test] (',' fpdef ['=' test])* [',']
    """
    nodelist = [py_symbol.varargslist]
    def stared(args):
        if args[0] == "**":
            nodelist.append(Symbol(py_token.DOUBLESTAR,"**"))
            nodelist.append(Symbol(py_token.NAME,args[1]))
        elif args[0] == "*":
            nodelist.append(Symbol(py_token.STAR,"*"))
            nodelist.append(Symbol(py_token.NAME,args[1]))
            if len(args)>2:
                assert args[2] == "**"
                nodelist.append(Symbol(py_token.COMMA,","))
                nodelist.append(Symbol(py_token.DOUBLESTAR,"**"))
                nodelist.append(Symbol(py_token.NAME,args[3]))

    if args[0] in ("*","**"):
        stared(args)
        return nodelist
    else:
        i = 0
        while i<len(args):
            if args[i] in ("*","**"):
                stared(args[i:])
                return nodelist
            elif args[i][0] == py_symbol.fpdef:
                nodelist.append(args[i])
                if (i+1)<len(args):
                    if args[i+1][0] != py_symbol.test:
                        nodelist.append(Symbol(py_token.COMMA,","))
                        i+=1
                        continue
            elif args[i][0] == py_symbol.test:
                nodelist.append(Symbol(py_token.EQUAL, "="))
                nodelist.append(args[i])
                nodelist.append(Symbol(py_token.COMMA,","))
            else:
                raise ValueError,"fpdef expected"
            i+=1
    try:
        if nodelist[-1][0] == py_token.COMMA:
            del nodelist[-1]
    except TypeError:
        print nodelist[-1]
    return nodelist

@py_cst
def fpdef(*args):
    "fpdef: NAME | '(' fplist ')'"
    arg = args[0]
    nodelist = [py_symbol.fpdef]
    if arg[0] == py_symbol.fplist:
        nodelist.append( Symbol(py_token.LPAR, name))
        nodelist.append( arg )
        nodelist.append( Symbol(py_token.RPAR, name))
    elif arg[0] == py_token.NAME:
        nodelist.append( arg )
    else:
        raise ValueError, "arg must be fplist or NAME"
    return nodelist

@py_cst
def fplist(*args):
    "fplist: fpdef (',' fpdef)* [',']"
    nodelist = [py_symbol.fplist]
    if len(args)==1:
        assert args[0][0] == py_symbol.fpdef, toText(args[0][0])
        return [nodelist]+[args[0]]
    for arg in args:
        if arg == ",":
            nodelist.append(Symbol(py_token.COMMA, ","))
            return nodelist
        assert arg[0] == py_symbol.fpdef, toText(arg[0])
        nodelist.append(arg)
        nodelist.append(Symbol(py_token.COMMA, ","))
    del nodelist[-1]
    return nodelist

@py_cst
def stmt(*args):
    " stmt: simple_stmt | compound_stmt "
    arg = args[0]
    nodelist = [py_symbol.stmt]
    assert arg[0] in ( py_symbol.simple_stmt, py_symbol.compound_stmt)
    nodelist.append(arg)
    return nodelist

@py_cst
def simple_stmt(*args):
    " simple_stmt: small_stmt (';' small_stmt)* [';'] NEWLINE "
    nodelist = [py_symbol.simple_stmt]
    for arg in args:
        assert arg[0] == py_symbol.small_stmt, toText(arg[0])
        nodelist.append(arg)
        nodelist.append(Symbol(py_token.SEMI,";"))
    nodelist.append(NEWLINE())
    return nodelist

@py_cst
def small_stmt(*args):
    " small_stmt: expr_stmt | print_stmt  | del_stmt | pass_stmt | flow_stmt | import_stmt | global_stmt | exec_stmt | assert_stmt"
    arg = args[0]
    assert arg[0] in ( py_symbol.expr_stmt, py_symbol.print_stmt, py_symbol.del_stmt, py_symbol.pass_stmt,
                        py_symbol.flow_stmt, py_symbol.import_stmt, py_symbol.global_stmt, py_symbol.exec_stmt, py_symbol.assert_stmt)
    return [py_symbol.small_stmt, arg]

@py_cst
def expr_stmt(*args):
    " expr_stmt: testlist (augassign testlist | ('=' testlist)*) "
    nodelist = [py_symbol.expr_stmt]
    assert args[0][0] == py_symbol.testlist, toText(args[0][0])
    nodelist.append(args[0])
    if len(args) == 1:
        return nodelist
    if args[1][0] == py_symbol.augassign:
        nodelist.append(args[1])
        assert args[2][0] == py_symbol.testlist, toText(args[2][0])
        nodelist.append(args[2])
    else:
        for arg in args[1:]:
            if arg == "=":
                nodelist.append(Symbol(py_token.EQUAL,"="))
                continue
            assert arg[0] == py_symbol.testlist, toText(arg[0])
            nodelist.append(arg)
    return nodelist


AUGASSIGN_MAP = {
    "&=" : py_token.AMPEREQUAL,
    "^=" : py_token.CIRCUMFLEXEQUAL,
    "//=" : py_token.DOUBLESLASHEQUAL,
    "**=" : py_token.DOUBLESTAREQUAL,
    "<<=" : py_token.LEFTSHIFTEQUAL,
    "-=" : py_token.MINEQUAL,
    "%=" : py_token.PERCENTEQUAL,
    "+=" : py_token.PLUSEQUAL,
    ">>=" : py_token.RIGHTSHIFTEQUAL,
    "/=" : py_token.SLASHEQUAL,
    "*=" : py_token.STAREQUAL,
    "|=" : py_token.VBAREQUAL
    }

@py_cst
def augassign(*args):
    "augassign: '+=' | '-=' | '*=' | '/=' | '%=' | '&=' | '|=' | '^=' | '<<=' | '>>=' | '**=' | '//='  "
    arg = args[0]
    return [py_symbol.augassign,[AUGASSIGN_MAP[arg],arg]]

@py_cst
def print_stmt(*args):
    "print_stmt: 'print' ( '>>' test [ (',' test)+ [','] ] | [ test (',' test)* [','] ] )"
    nodelist = [py_symbol.print_stmt, [py_token.NAME, "print"]]
    if args:
        if args[0] == ">>":
            nodelist.append([py_token.RIGHTSHIFT,">>"])
            assert args[1][0] == py_symbol.test, toText(args[1][0])
            nodelist.append(args[1])
            for arg in args[2:]:
                nodelist.append([py_token.COMMA,","])
                if arg == ",":
                    break
                assert arg[0] == py_symbol.test, toText(arg[0])
                nodelist.append(arg)
        else:
            assert args[1][0] == py_symbol.test, toText(args[1][0])
            nodelist.append(args[1])
            for arg in args[2:]:
                nodelist.append([py_token.COMMA,","])
                if arg == ",":
                    break
                assert arg[0] == py_symbol.test, toText(arg[0])
                nodelist.append(arg)
    return nodelist

@py_cst
def del_stmt(*args):
    " del_stmt: 'del' exprlist "
    arg = args[0]
    nodelist = [py_symbol.del_stmt]
    nodelist.append(Symbol(py_token.NAME,"del"))
    assert arg[0] == py_symbol.exprlist, toText(arg[0])
    nodelist.append(arg)
    return nodelist

@py_cst
def pass_stmt(*args):
    " pass_stmt: 'pass' "
    return [py_symbol.pass_stmt, Symbol(py_token.NAME,"pass")]

@py_cst
def flow_stmt(*args):
    " flow_stmt: break_stmt | continue_stmt | return_stmt | raise_stmt | yield_stmt"
    arg = args[0]
    assert arg[0] in ( py_symbol.break_stmt, py_symbol.continue_stmt, py_symbol.return_stmt,
                        py_symbol.raise_stmt, py_symbol.yield_stmt)
    return [py_symbol.flow_stmt, arg]

@py_cst
def break_stmt(*args):
    " break_stmt: 'break' "
    return [py_symbol.break_stmt, Symbol(py_token.NAME,"break")]

@py_cst
def continue_stmt(*args):
    " continue_stmt: 'continue' "
    return [py_symbol.continue_stmt, Symbol(py_token.NAME,"continue")]

@py_cst
def return_stmt(*args):
    " return_stmt: 'return' [testlist] "
    if args:
        assert args[0][0] == py_symbol.testlist, toText(args[0][0])
        return [py_symbol.return_stmt,Symbol(py_token.NAME,"return"),args[0]]
    else:
        return [py_symbol.return_stmt,Symbol(py_token.NAME,"return")]

@py_cst
def yield_expr(*args):
    "yield_expr: 'yield' [testlist] "
    if args:
        arg = args[0]
        assert arg[0] == py_symbol.testlist, toText(arg[0])
        return [py_symbol.yield_stmt,Symbol(py_token.NAME,"yield"),arg]
    else:
        return [py_symbol.yield_stmt,Symbol(py_token.NAME,"yield")]

@py_cst
def yield_stmt(*args):
    "yield_stmt: yield_expr "
    assert args[0] == py_symbol.yield_expr, toText(args[0][0])
    return [py_symbol.yield_stmt,args[0]]

@py_cst
def raise_stmt(*args):
    "raise_stmt: 'raise' [test [',' test [',' test]]]"
    nodelist = [py_symbol.raise_stmt,[py_token.NAME,"raise"]]
    assert len(args)<=3
    if args:
        assert args[0][0] == py_symbol.test, toText(args[0][0])
        nodelist.append(args[0])
        for arg in args[1:]:
            assert arg[0] == py_symbol.test, toText(arg[0])
            nodelist.append([py_token.COMMA,","])
            nodelist.append(arg)
    return nodelist

@py_cst
def import_stmt(*args):
    "import_stmt: import_name | import_from "
    arg = args[0]
    assert arg[0] in (py_symbol.import_name, py_symbol.import_from)
    return [py_symbol.import_stmt,arg]

@py_cst
def import_name(*args):
    "import_name: 'import' dotted_as_names"
    arg = args[0]
    assert arg[0] == py_symbol.dotted_as_names, toText(arg[0])
    return [py_symbol.import_name, [py_token.NAME,"import"],arg]

@py_cst
def import_from(*args):
    "import_from: ('from' ('.'* dotted_name | '.'+) 'import' ('*' | '(' import_as_names ')' | import_as_names))"
    nodelist = [py_symbol.import_from]
    i = 0
    nodelist.append([py_token.NAME,"from"])
    if isinstance(args[0], str) and args[0].startswith("."):
        for dot in args[0]:
            nodelist.append([py_token.DOT,"."])
        i += 1
    if args[i][0] == py_symbol.dotted_name:
        nodelist.append(args[i])
        i += 1
    nodelist.append([py_token.NAME,"import"])
    if args[i] == "*":
        nodelist.append([py_token.STAR,"*"])
    elif args[i] == "(":
        nodelist.append([py_token.LPAR,"("])
        assert args[i+1][0] == py_symbol.import_as_names, toText(args[i+1][0])
        nodelist.append(args[i+1])
        nodelist.append([py_token.RPAR,")"])
    else:
        assert args[i][0] == py_symbol.import_as_names, toText(args[i][0])
        nodelist.append(args[i])
    return nodelist

@py_cst
def import_as_name(*args):
    "import_as_name: NAME ['as' NAME]"
    assert len(args) == 1 or len(args) == 2
    nodelist = [py_symbol.import_as_name]
    for i,arg in enumerate(args):
        if i == 1:
            nodelist.append(Name("as"))
        if isinstance(arg, str):
            nodelist.append(Name(arg))
        else:
            assert arg == py_token.NAME
            nodelist.append(arg)
    return nodelist

@py_cst
def import_as_names(*args):
    "import_as_names: import_as_name (',' import_as_name)* [','] "
    nodelist = [py_symbol.import_as_names]
    for arg in args:
        if arg[0] == py_token.COMMA:
            nodelist.append(arg)
            return nodelist
        assert arg[0] == py_symbol.import_as_name, toText(arg[0])
        nodelist.append(arg)
    return nodelist

@py_cst
def dotted_as_name(*args):
    "dotted_as_name: dotted_name [('as'|NAME) NAME] "
    nodelist = [py_symbol.dotted_as_name]
    assert args[0][0] == py_symbol.dotted_name, toText(args[0][0])
    nodelist.append(args[0])
    if len(args) == 3:
        nodelist.append([py_token.NAME,args[1]])
        nodelist.append([py_token.NAME,args[2]])
    return nodelist

@py_cst
def dotted_as_names(*args):
    "dotted_as_names: dotted_as_name (',' dotted_as_name)* "
    nodelist = [py_symbol.dotted_as_names]
    assert args[0][0] == py_symbol.dotted_as_name, toText(args[0][0])
    nodelist.append(args[0])
    if len(args)>1:
        for arg in args[1:]:
            nodelist.append(Symbol(py_token.COMMA,","))
            assert args[0] == py_symbol.dotted_as_name, toText(args[0])
            nodelist.append(arg)
    return nodelist

@py_cst
def dotted_name(*args):
    "dotted_name: NAME ('.' NAME)* "
    nodelist = [py_symbol.dotted_name]
    nodelist.append(Symbol(py_token.NAME,args[0]))
    if len(args)>1:
        for arg in args[1:]:
            nodelist.append(Symbol(py_token.DOT,"."))
            nodelist.append(Symbol(py_token.NAME,arg))
    return nodelist

@py_cst
def global_stmt(*args):
    "global_stmt: 'global' NAME (',' NAME)* "
    nodelist = [py_symbol.global_stmt,[py_token,NAME,"global"]]
    assert args[0][0] == py_symbol.test, toText(args[0][0])
    nodelist.append(args[0])
    for arg in args[1:]:
        nodelist.append([py_token.COMMA,","])
        assert arg[0] == py_symbol.test, toText(arg[0])
        nodelist.append(arg)
    return nodelist

@py_cst
def assert_stmt(*args):
    "assert_stmt: 'assert' test [',' test]"
    nodelist = [py_symbol.assert_stmt]
    nodelist.append([py_token.NAME,"assert"])
    assert args[0][0] == py_symbol.test, toText(args[0][0])
    nodelist.append(args[0])
    if len(args)>1:
        assert args[1][0] == py_symbol.test, toText(args[1][0])
        nodelist.append([py_symbol.COLON,","])
        nodelist.append(args[1])
    return nodelist

@py_cst
def exec_stmt(*args):
    "exec_stmt: 'exec' expr ['in' test [',' test]]"
    nodelist = [py_symbol.exec_stmt,[py_token.NAME,"exec"]]
    assert args[0][0] == symbo.expr
    nodelist.append(args[0])
    if len(args)>1:
        nodelist.append([py_token.NAME,"in"])
        assert args[1][0] == py_symbol.test, toText(args[1][0])
        nodelist.append(args[1])
        if len(args)>2:
            nodelist.append([py_token.COMMA,","])
            assert args[2][0] == py_symbol.test, toText(args[2][0])
            nodelist.append(args[2])
    return nodelist

@py_cst
def compound_stmt(*args):
    "compound_stmt: if_stmt | while_stmt | for_stmt | try_stmt | funcdef | classdef "
    stmt = args[0]
    assert stmt[0] in ( py_symbol.if_stmt, py_symbol.while_stmt, py_symbol.for_stmt, py_symbol.try_stmt,
                        py_symbol.classdef, py_symbol.funcdef)
    return [py_symbol.compound_stmt, stmt]

@py_cst
def if_stmt(*args):
    "if_stmt: 'if' test ':' suite ('elif' test ':' suite)* ['else' ':' suite] "
    nodelist = [py_symbol.if_stmt]
    else_branch = None
    if len(args)%2==1:
        else_branch = args[-1]
    assert args[0][0] == py_symbol.test, toText(args[0][0])
    assert args[1][0] == py_symbol.suite, toText(args[1][0])
    nodelist.append(Symbol(py_token.NAME,"if"))
    nodelist.append(args[0])
    nodelist.append(Symbol(py_token.COLON,":"))
    nodelist.append(args[1])
    for t,s in [[args[i],args[i+1]] for i in range(len(args)-len(args)%2)[2::2]]:
        assert t[0] == py_symbol.test, toText(t[0])
        assert s[0] == py_symbol.suite, toText(s[0])
        nodelist.append(Symbol(py_token.NAME,"elif"))
        nodelist.append(t)
        nodelist.append(Symbol(py_token.COLON,":"))
        nodelist.append(s)
    if else_branch:
        assert else_branch[0] == py_symbol.suite, toText(else_branch[0])
        nodelist.append(Symbol(py_token.NAME,"else"))
        nodelist.append(Symbol(py_token.COLON,":"))
        nodelist.append(else_branch)
    return nodelist

@py_cst
def while_stmt(*args):
    "while_stmt: 'while' test ':' suite ['else' ':' suite]"
    nodelist = [py_symbol.while_stmt]
    assert args[0][0] == py_symbol.test, toText(args[0][0])
    assert args[1][0] == py_symbol.suite, toText(args[1][0])
    nodelist.append(Symbol(py_token.NAME,"while"))
    nodelist.append(args[0])
    nodelist.append(Symbol(py_token.COLON,":"))
    nodelist.append(args[1])
    if len(args)>=3:
        assert args[2][0] == py_symbol.suite, toText(args[2][0])
        nodelist.append(Symbol(py_token.NAME,"else"))
        nodelist.append(Symbol(py_token.COLON,":"))
        nodelist.append(args[2])
    return nodelist

@py_cst
def for_stmt(*args):
    "for_stmt: 'for' exprlist 'in' testlist ':' suite ['else' ':' suite] "
    nodelist = [py_symbol.for_stmt]
    assert args[0][0] == py_symbol.exprlist, toText(args[0][0])
    assert args[1][0] == py_symbol.testlist, toText(args[1][0])
    nodelist.append(Symbol(py_token.NAME,"for"))
    nodelist.append(args[0])
    nodelist.append(Symbol(py_token.COLON,":"))
    nodelist.append(args[1])
    if len(args)>=3:
        assert args[2] == py_symbol.suite, toText(args[2])
        nodelist.append(Symbol(py_token.NAME,"else"))
        nodelist.append(Symbol(py_token.COLON,":"))
        nodelist.append(args[2])
    return nodelist

@py_cst
def try_stmt(*args):
    """try_stmt: ('try' ':' suite (except_clause ':' suite)+ ['else' ':' suite] ['finally' ':' suite] |
                  'try' ':' suite 'finally' ':' suite)
    """
    nodelist = [py_symbol.try_stmt]
    nodelist.append([py_token.NAME,"try"])
    nodelist.append([py_token.COLON,":"])
    assert args[0][0] == py_symbol.suite, toText(args[0][0])
    nodelist.append(args[0])
    i = 1
    while i<len(args):
        arg = args[i]
        if arg == "finally":
            assert args[i+1][0] == py_symbol.suite, toText(args[i+1][0])
            nodelist.append([py_token.NAME,"finally"])
            nodelist.append([py_token.COLON,":"])
            nodelist.append(args[i+1])
            return nodelist
        elif arg == "else":
            assert args[i+1][0] == py_symbol.suite, toText(args[i+1][0])
            nodelist.append([py_token.NAME,"else"])
            nodelist.append([py_token.COLON,":"])
            nodelist.append(args[i+1])
        else:
            assert arg[0] == py_symbol.except_clause, toText(arg[0])
            nodelist.append(arg)
            nodelist.append([py_token.COLON,":"])
            i+=1
            assert args[i][0] == py_symbol.suite, toText(args[i][0])
            nodelist.append(args[i])
        i+=1
    return nodelist

@py_cst
def with_stmt(*args):
    "with_stmt: 'with' test [ with_var ] ':' suite"
    nodelist = [py_symol.with_stmt, [py_token.NAME, "with"]]
    assert args[0][0] == py_symbol.test, toText(args[0][0])
    nodelist.append(args[0])
    i = 1
    if args[i][0] == py_symbol.with_var:
        nodelist.append(args[i])
        i+=1
    assert args[i][0] == py_symbol.suite, toText(args[i][0])
    nodelist.append([py_token.COLON,":"])
    nodelist.append(args[i])
    return nodelist


@py_cst
def with_var(*args):
    "with_var: ('as' | NAME) expr"
    nodelist = [py_symol.with_var]
    if args[0] == "as":
        nodelist.append([py_token.NAME,"as"])
    else:
        assert args[0][0] == py_token.NAME, toText(args[0][0])
        nodelist.append(args[0])
    assert args[1][0] == py_symbol.expr
    nodelist.append(args[1])
    return nodelist

@py_cst
def except_clause(*args):
    "except_clause: 'except' [test [',' test]] "
    nodelist = [py_symbol.except_clause,[py_token.NAME,"except"]]
    if args:
        assert args[0][0] == py_symbol.test, toText(args[0][0])
        nodelist.append(args[0])
    if len(args)>1:
        assert args[1][0] == py_symbol.test, toText(args[1][0])
        nodelist.append([py_symbol.COLON,","])
        nodelist.append(args[1])
    return nodelist

@py_cst
def suite(*args):
    "suite: simple_stmt | NEWLINE INDENT stmt+ DEDENT "
    nodelist = [py_symbol.suite]
    if args[0][0] == py_symbol.simple_stmt:
        nodelist.append(args[0])
    else:
        nodelist.append(NEWLINE())
        nodelist.append(INDENT())
        for arg in args:
            assert arg[0] == py_symbol.stmt, toText(arg[0])
            nodelist.append(arg)
        nodelist.append(DEDENT())
    return nodelist


def NEWLINE():
    return Symbol(py_token.NEWLINE,'')

def INDENT():
    return Symbol(py_token.INDENT,'')

def DEDENT():
    return Symbol(py_token.DEDENT,'')

def ENDMARKER():
    return Symbol(py_token.ENDMARKER,'')

@py_cst
def old_test(*args):
    "old_test: or_test | old_lambdef"
    assert args[0][0] in (py_symbol.old_lambdef, py_symbol.old_test)
    return [py_symbol.old_test, args[0]]

@py_cst
def old_lambdef(*args):
    "old_lambdef: 'lambda' [varargslist] ':' old_test"
    if len(args) == 2:
        _varargs, _test = args
    else:
        _test = args[0]
        _varargs = ()
    nodelist = [py_symbol.old_lambdef]
    nodelist.append(Symbol(py_token.NAME, "lambda"))
    if _varargs:
        assert _varargs[0] == py_symbol.varargslist
        nodelist.append(_varargs)
    nodelist.append(Symbol(py_token.COLON, ':'))
    assert _test[0]==py_symbol.test, toText(_test[0])
    nodelist.append(_test)
    return nodelist


@py_cst
def test(*args):
    "test: or_test ['if' or_test 'else' test] | lambdef "
    assert (args[0][0] == py_symbol.lambdef) or (args[0][0] == py_symbol.or_test), toText(args[0][0])
    nodelist = [py_symbol.test]
    nodelist.append(args[0])
    if len(args)>1:
        assert args[1][0] == py_symbol.or_test, toText(args[1][0])
        nodelist.append(Name("if"))
        nodelist.append(args[1])
        nodelist.append(Name("else"))
        assert args[2][0] == py_symbol.test, toText(args[1][0])
        nodelist.append(args[2])
    return nodelist

@py_cst
def or_test(*args):
    "or_test: and_test ('or' and_test)* "
    assert args[0][0] == py_symbol.and_test
    nodelist = [py_symbol.or_test]
    nodelist.append(args[0])
    for arg in args[1:]:
        nodelist.append([py_token.NAME, 'or'])
        assert arg[0] == py_symbol.and_test, toText(arg[0])
        nodelist.append(arg)
    return nodelist


@py_cst
def testlist(*args):
    "testlist: test (',' test)* [','] "
    nodelist = [py_symbol.testlist]
    i = 1
    assert args[0][0] == py_symbol.test, toText(args[0][0])
    nodelist.append(args[0])
    while i<len(args):
        arg = args[i]
        if arg == ",":
            nodelist.append([py_token.COMMA, ","])
            return nodelist
        nodelist.append(Symbol(py_token.COMMA, ","))
        assert arg[0] == py_symbol.test, toText(arg[0])
        nodelist.append(arg)
        i+=1
    return nodelist

@py_cst
def testlist_safe(*args):
    "testlist_safe: old_test [(',' old_test)+ [',']]"
    nodelist = [py_symbol.testlist_safe]
    for arg in args:
        assert arg[0] == py_symbol.old_test, toText(arg[0])
        nodelist.append(arg)
        nodelist.append([py_token.COMMA,","])
    return nodelist

@py_cst
def and_test(*args):
    "and_test: not_test ('and' not_test)* "
    assert args[0][0] == py_symbol.not_test, toText(args[0][0])
    nodelist = [py_symbol.and_test]
    nodelist.append(args[0])
    for arg in args[1:]:
        nodelist.append(Symbol(py_token.NAME, 'and'))
        assert arg[0] == py_symbol.not_test, toText(arg[0])
        nodelist.append(arg)
    return nodelist

@py_cst
def not_test(*args):
    "not_test: 'not' not_test | comparison "
    nodelist = [py_symbol.not_test]
    if args[0] == "not":
        nodelist.append(Symbol(py_token.NAME, 'not'))
        assert args[1][0] == py_symbol.not_test, toText(args[1][0])
        nodelist.append(args[1])
    else:
         assert args[0][0] == py_symbol.comparison, toText(args[0][0])
         nodelist.append(args[0])
    return nodelist


def comp_op(comp):
    nodelist = [py_symbol.comp_op]
    comp = comp.strip()
    if comp == "<":
        nodelist.append(Symbol(py_token.LESS, '<'))
    elif comp == ">":
        nodelist.append(Symbol(py_token.GREATER, '>'))
    elif comp == "==":
        nodelist.append(Symbol(py_token.EQEQUAL, '=='))
    elif comp == ">=":
        nodelist.append(Symbol(py_token.GREATEREQUAL, '>='))
    elif comp == "<=":
        nodelist.append(Symbol(py_token.LESSEQUAL, '<='))
    elif comp == "<=":
        nodelist.append(Symbol(py_token.NOTEQUAL, '<>'))
    elif comp == "!=":
        nodelist.append(Symbol(py_token.NOTEQUAL, '!='))
    elif comp in ("in","not","is"):
        nodelist.append(Symbol(py_token.NAME, comp))
    elif comp in ("not in","is not"):
        for c in cmp.split():
            nodelist.append(Symbol(py_token.NAME, c))
    else:
        raise ValueError, "Cannot assign comparison %s"%cmp
    return nodelist


@py_cst
def comparison(*args):
    " comparison: expr (comp_op expr)* "
    " comp_op: '<'|'>'|'=='|'>='|'<='|'<>'|'!='|'in'|'not' 'in'|'is' 'not'|'is' "
    nodelist = [py_symbol.comparison]
    assert args[0][0] == py_symbol.expr, toText(args[0][0])
    nodelist.append(args[0])
    for i in range(1,len(args),2):
        if isinstance(args[i],str):
            nodelist.append(comp_op(args[i]))
        else:
            assert args[i][0] == py_symbol.comp_op, toText(args[i][0])
            nodelist.append(args[i])
        assert args[i+1][0] == py_symbol.expr, toText(args[i+1][0])
        nodelist.append(args[i+1])
    return nodelist

@py_cst
def expr(*args):
    "expr: xor_expr ('|' xor_expr)* "
    nodelist = [py_symbol.expr]
    for node in args:
        if node[0]!=py_symbol.xor_expr:
            nodelist.append([py_symbol.xor_expr, node])
        else:
            nodelist.append(node)
        nodelist.append(Symbol(py_token.VBAR, '|'))
    del nodelist[-1]
    return nodelist

@py_cst
def xor_expr(*args):
    "xor_expr: and_expr ('^' and_expr)* "
    nodelist = [py_symbol.xor_expr]
    for node in args:
        if node[0]!=py_symbol.and_expr:
            nodelist.append([py_symbol.and_expr, node])
        else:
            nodelist.append(node)
        nodelist.append(Symbol(py_token.CIRCUMFLEX, '^'))
    del nodelist[-1]
    return nodelist

@py_cst
def and_expr(*args):
    "and_expr: shift_expr ('&' shift_expr)* "
    nodelist = [py_symbol.and_expr]
    for node in args:
        if node[0]!=py_symbol.shift_expr:
            nodelist.append([py_symbol.shift_expr, node])
        else:
            nodelist.append(node)
        nodelist.append(Symbol(py_token.AMPER, '&'))
    del nodelist[-1]
    return nodelist

@py_cst
def shift_expr(*args):
    "shift_expr: arith_expr (('<<'|'>>') arith_expr)* "
    nodelist = [py_symbol.shift_expr]
    nodes = args[::2]
    ops   = args[1::2]
    for i,node in enumerate(nodes):
        if node[0]!=py_symbol.arith_expr:
            nodelist.append([py_symbol.arith_expr, node])
        else:
            nodelist.append(node)
        try:
            if ops[i] == ">>":
                nodelist.append(Symbol(py_token.RIGHTSHIFT, ">>"))
            elif ops[i] == "<<":
                nodelist.append(Symbol(py_token.LEFTSHIFT, "<<"))
            else:
                raise ValueError, "Operator must be either LEFTSHIFT or RIGHTSHIFT"
        except IndexError:
            break
    return nodelist


@py_cst
def arith_expr(*args):
    "arith_expr: term (('+'|'-') term)* "
    nodelist = [py_symbol.arith_expr]
    nodes = args[::2]
    ops   = args[1::2]
    for i,node in enumerate(nodes):
        if node[0]!=py_symbol.term:
            nodelist.append([py_symbol.term, node])
        else:
            nodelist.append(node)
        try:
            if ops[i] == "+":
                nodelist.append(Symbol(py_token.PLUS, "+"))
            elif ops[i] == "-":
                nodelist.append(Symbol(py_token.MINUS, "-"))
            else:
                raise ValueError, "Operator must be either PLUS or MINUS, %s found"%ops[i]
        except IndexError:
            break
    return nodelist

@py_cst
def term(*args):
    "term: factor (('*'|'/'|'%'|'//') factor)* "
    nodelist = [py_symbol.term]
    nodes = args[::2]
    ops   = args[1::2]
    for i,node in enumerate(nodes):
        if node[0]!=py_symbol.factor:
            nodelist.append([py_symbol.factor, node])
        else:
            nodelist.append(node)
        try:
            if ops[i] == "*":
                nodelist.append(Symbol(py_token.STAR, "*"))
            elif ops[i] == "/":
                nodelist.append(Symbol(py_token.SLASH, "/"))
            elif ops[i] == "%":
                nodelist.append(Symbol(py_token.PERCENT, "%"))
            elif ops[i] == "//":
                nodelist.append(Symbol(py_token.DOUBLESLASH, "//"))
            else:
                raise ValueError, "Operator must be either STAR or SLASH or PERCENT or DOUBLESLASH"
        except IndexError:
            break
    return nodelist

@py_cst
def factor(*args):
    "factor: ('+'|'-'|'~') factor | power "
    nodelist = [py_symbol.factor]
    ops = None
    if isinstance(args[0],str):
        ops = args[0]
        node = args[1]
    else:
        node = args[0]
    if ops:
        try:
            if ops == "+":
                nodelist.append(Symbol(py_token.PLUS, "*"))
            elif ops == "-":
                nodelist.append(Symbol(py_token.MINUS, "-"))
            elif ops == "~":
                nodelist.append(Symbol(py_token.TILDE, "~"))
            else:
                raise ValueError, "Operator must be eithe PLUS or MINUS or TILDE"
        except IndexError:
            pass
    if len(nodelist)==1:
        assert node[0] == py_symbol.power, toText(node[0])
    else:
        assert node[0] == py_symbol.factor, toText(node[0])
    nodelist.append(node)
    return nodelist

@py_cst
def power(*args):
    "power: atom trailer* ['**' factor] "
    nodelist = [py_symbol.power]
    assert args[0][0] == py_symbol.atom, toText(args[0][0])
    nodelist.append(args[0])
    for i,arg in enumerate(args[1:]):
        if arg[0] == py_symbol.trailer:
            nodelist.append(arg)
        elif arg[0] == py_symbol.factor:
            nodelist.append(Symbol(py_token.DOUBLESTAR, "**"))
            nodelist.append(arg)
        elif arg == '**':
            continue
        else:
            raise ValueError("Node of type trailer or factor expected. %s found instead"%toText(arg[0]))
    return nodelist

@py_cst
def atom(*args):
    "atom: '(' [testlist_gexp | yield_expr] ')' | '[' [listmaker] ']' | '{' [dictmaker] '}' | '`' testlist1 '`' | NAME | NUMBER | STRING+ "
    nodelist = [py_symbol.atom]
    if args[0] == '(':
        nodelist.append(Symbol(py_token.LPAR, "("))
        if len(args)>2:
            assert args[1][0] in (py_symbol.testlist_gexp, py_symbol.yield_expr), toText(args[1][0])
            nodelist.append(args[1])
        nodelist.append(Symbol(py_token.RPAR, ")"))
    elif args[0] == '[':
        nodelist.append(Symbol(py_token.LSQB, "["))
        if len(args)>2:
            assert args[1][0] == py_symbol.listmaker, toText(args[1][0])
            nodelist.append(args[1])
        nodelist.append(Symbol(py_token.RSQB, "]"))
    elif args[0] == '{':
        nodelist.append(Symbol(py_token.LBRACE, "{"))
        if len(args)>2:
            assert args[1][0] == py_symbol.dictmaker, toText(args[1][0])
            nodelist.append(args[1])
        nodelist.append(Symbol(py_token.RBRACE, "}"))
    elif args[0] == '`':
        nodelist.append(Symbol(py_token.BACKQUOTE, "`"))
        if len(args)>2:
            assert args[1][0] == py_symbol.testlist1, toText(args[1][0])
            nodelist.append(args[1])
        nodelist.append(Symbol(py_token.BACKQUOTE, "`"))
    elif args[0][0] in (py_token.NAME, py_token.NUMBER):
            nodelist.append(args[0])
    else:
        for arg in args:
            assert arg[0] == py_token.STRING
            nodelist.append(arg)
    return nodelist

@py_cst
def exprlist(*args):
    "exprlist: expr (',' expr)* [','] "
    nodelist = [py_symbol.exprlist]
    if len(args)==1:
        assert args[0][0] == py_symbol.expr, toText(args[0][0])
        return nodelist+[args[0]]
    for arg in args:
        if arg == ",":
            nodelist.append(Symbol(py_token.COMMA, ","))
            return nodelist
        assert arg[0] == py_symbol.expr, toText(arg[0])
        nodelist.append(arg)
        nodelist.append(Symbol(py_token.COMMA, ","))
    del nodelist[-1]
    return nodelist

@py_cst
def lambdef(*args):
    "lambdef: 'lambda' [varargslist] ':' test "
    parameters, test = args
    nodelist = [py_symbol.lambdef]
    nodelist.append(Symbol(py_token.NAME, "lambda"))
    if parameters !=():
        assert parameters[0] == py_symbol.varargslist or parameters == ()
        nodelist.append(parameters)
    nodelist.append(Symbol(py_token.COLON, ':'))
    assert test[0]==py_symbol.test, toText(test[0])
    nodelist.append(test)
    return nodelist

@py_cst
def testlist_gexp(*args):
    "test ( gen_for | (',' test)* [','] )"
    nodelist = [py_symbol.testlist_gexp]
    assert args[0][0] == py_symbol.test, toText(args[0][0])
    nodelist.append(args[0])
    if len(args) > 1:
        if args[1][0] == py_symbol.gen_for:
            nodelist.append(args[1])
            return nodelist
    for arg in args[1:]:
        if arg == ",":
            nodelist.append(Symbol(py_token.COMMA, ","))
            return nodelist
        nodelist.append(Symbol(py_token.COMMA, ","))
        assert arg[0] == py_symbol.test, toText(arg[0])
        nodelist.append(arg)
    return nodelist

@py_cst
def listmaker(*args):
    "listmaker: test ( list_for | (',' test)* [','] )"
    nodelist = [py_symbol.listmaker]
    assert args[0][0] == py_symbol.test, toText(args[0][0])
    nodelist.append(args[0])
    for arg in args[1:]:
        if arg == ",":
            nodelist.append(Symbol(py_token.COMMA, ","))
            return nodelist
        if (arg[0] == py_symbol.test):
            nodelist.append(Symbol(py_token.COMMA, ","))
            nodelist.append(arg)
        elif (arg[0] == py_symbol.list_for):
            nodelist.append(arg)
        else:
            raise ValueError,"expected list_for or test. %s found"%arg[0]
    return nodelist

@py_cst
def trailer(*args):
    "trailer : '(' [arglist] ')' | '[' subscriptlist ']' | '.' NAME "
    nodelist = [py_symbol.trailer]
    if args[0] == '(':
        nodelist.append(Symbol(py_token.LPAR, "("))
        if args[1]==')':
            nodelist.append(Symbol(py_token.RPAR, ")"))
        else:
            assert args[1][0] == py_symbol.arglist, toText(args[1][0])
            nodelist.append(args[1])
            nodelist.append(Symbol(py_token.RPAR, ")"))
    elif args[0] == '[':
        nodelist.append(Symbol(py_token.LSQB, "["))
        assert args[1][0] == py_symbol.subscriptlist, toText(args[1][0])
        nodelist.append(args[1])
        nodelist.append(Symbol(py_token.RSQB, "]"))
    else:
        assert args[0] == '.'
        nodelist.append(Symbol(py_token.DOT, "."))
        if isinstance(args[1],list):
            assert args[1][0] == py_token.NAME
            nodelist.append(args[1])
        else:
            nodelist.append(Symbol(py_token.NAME,args[1]))
    return nodelist



@py_cst
def dictmaker(*args):
    "dictmaker: test ':' test (',' test ':' test)* [','] "
    if args[-1] == ",":
        assert (len(args)-1)%2 == 0
    else:
        assert len(args)%2 == 0
    nodelist = [py_symbol.dictmaker]
    i = 0
    while i<len(args):
        if args[i] == ",":
            nodelist.append(Symbol(py_token.COMMA, ","))
            return nodelist
        assert args[i][0] == args[i+1][0] == py_symbol.test
        if i>=2:
            nodelist.append(Symbol(py_token.COMMA, ","))
        nodelist.append(args[i])
        nodelist.append(Symbol(py_token.COLON, ":"))
        nodelist.append(args[i+1])
        i+=2
    return nodelist

@py_cst
def subscriptlist(*args):
    "subscriptlist: subscript (',' subscript)* [','] "
    nodelist = [py_symbol.subscriptlist]
    assert args[0][0] == py_symbol.subscript, toText(args[0][0])
    nodelist.append(args[0])
    for arg in args[1:]:
        if arg == ",":
            nodelist.append(Symbol(py_token.COMMA, ","))
            return nodelist
        assert arg[0] == py_symbol.subscript, toText(arg[0])
        nodelist.append(Symbol(py_token.COMMA, ","))
        nodelist.append(arg)
    return nodelist

@py_cst
def subscript(*args):
    "subscript: '.' '.' '.' | [test] ':' [test] [sliceop] | test "
    nodelist = [py_symbol.subscript]
    if args[0] == "...":
        nodelist.append(Symbol(py_token.DOT, "."))
        nodelist.append(Symbol(py_token.DOT, "."))
        nodelist.append(Symbol(py_token.DOT, "."))
    elif len(args)==1:
        assert args[0][0] == py_symbol.test, toText(args[0][0])
        return nodelist+[args[0]]
    else:
        assert len(args)<=4
        i = 0
        if args[0][0] == py_symbol.test:
            nodelist.append(args[0])
            i = 1
        assert args[i] == ':'
        nodelist.append(Symbol(py_token.COLON, ":"))
        for arg in args[i+1:]:
            assert arg[0] in (py_symbol.test, py_symbol.sliceop)
            nodelist.append(arg)
    return nodelist

@py_cst
def sliceop(*args):
    "sliceop: ':' [test]"
    nodelist = [py_symbol.sliceop]
    nodelist.append(Symbol(py_token.COLON, ":"))
    if args:
        assert args[0][0] == py_symbol.test, toText(args[0][0])
        nodelist.append(args[0])
    return nodelist

@py_cst
def classdef(*args):
    "classdef: 'class' NAME ['(' testlist ')'] ':' suite "
    if len(args) == 3:
        name, tl, suite = args
    else:
        name, suite = args
    nodelist = [py_symbol.classdef]
    nodelist.append(Symbol(py_token.NAME,"class"))
    if isinstance(name,str):
        nodelist.append(Symbol(py_token.NAME,name))
    else:
        assert name[0] == py_token.NAME
        nodelist.append(name)
    if tl:
        assert tl[0] == py_symbol.testlist, toText(tl[0])
        nodelist.append(Symbol(py_token.LPAR,"("))
        nodelist.append(tl)
        nodelist.append(Symbol(py_token.RPAR,")"))
    assert suite[0] == py_symbol.suite, toText(suite[0])
    nodelist.append(Symbol(py_token.COLON,":"))
    nodelist.append(suite)
    return nodelist

@py_cst
def arglist(*args):
    "arglist: (argument ',')* (argument [',']| '*' test [',' '**' test] | '**' test) "
    nodelist = [py_symbol.arglist]
    for i in range(len(args)):
        if args[i] == '**':
            nodelist.append(Symbol(py_token.DOUBLESTAR, '**'))
            assert args[i+1][0] == py_symbol.test, toText(args[i+1][0])
            nodelist.append(args[i+1])
            return nodelist
        elif args[i] == '*':
            nodelist.append(Symbol(py_token.STAR,'*'))
            assert args[i+1][0] == py_symbol.test, toText(args[i+1][0])
            nodelist.append(args[i+1])
            if len(args)>i+2:
                assert args[i+2] == '**'
                nodelist.append(Symbol(py_token.COMMA, ','))
                nodelist.append(Symbol(py_token.DOUBLESTAR, '**'))
                assert args[i+3][0] == py_symbol.test, toText(args[i+3][0])
                nodelist.append(args[i+3])
            return nodelist
        else:
            if args[i] == ",":
                return nodelist
            nodelist.append(args[i])
            assert args[i][0] == py_symbol.argument, toText(args[i][0])
            nodelist.append(Symbol(py_token.COMMA, ','))
    del nodelist[-1]
    return nodelist

@py_cst
def argument(*args):
    "argument: test [gen_for] | test '=' test "
    nodelist = [py_symbol.argument]
    if len(args)>1:
        if args[1] == '=':
            assert args[0][0] == py_symbol.test, toText(args[0][0])
            nodelist.append(args[0])
            nodelist.append(Symbol(py_token.EQUAL, '='))
            args = args[2:]
        assert args[0][0] == py_symbol.test, toText(args[0][0])
        nodelist.append(args[0])
        if len(args)>1:
            assert args[1][0] == py_symbol.gen_for, py_symbol.sym_name[args[1][0]]
            nodelist.append(args[1])
    else:
        assert args[0][0] == py_symbol.test, toText(args[0][0])
        nodelist.append(args[0])
    return nodelist


@py_cst
def list_iter(*args):
    "list_iter: list_for | list_if "
    arg = args[0]
    nodelist = [py_symbol.list_iter]
    assert arg[0] in (py_symbol.list_for, py_symbol.list_if)
    nodelist.append(arg)
    return nodelist

@py_cst
def list_for(*args):
    "list_for: 'for' exprlist 'in' testlist_safe [list_iter] "
    nodelist = [py_symbol.list_for]
    assert args[0][0] == py_symbol.exprlist, toText(args[0][0])
    nodelist.append(Symbol(py_token.NAME,"for"))
    nodelist.append(args[0])
    nodelist.append(Symbol(py_token.NAME,"in"))
    assert args[1][0] == py_symbol.testlist_safe, toText(args[1][0])
    nodelist.append(args[1])
    if len(args)>=3:
        assert args[2][0] == py_symbol.list_iter, toText(args[2][0])
        nodelist.append(args[2])
    return nodelist

@py_cst
def list_if(*args):
    "list_if: 'if' old_test [list_iter] "
    nodelist = [py_symbol.list_if]
    assert args[0][0] == py_symbol.old_test, toText(args[0][0])
    nodelist.append(Symbol(py_token.NAME,"if"))
    nodelist.append(args[0])
    if len(args)>=2:
        assert args[1][0] == py_symbol.list_iter, toText(args[1][0])
        nodelist.append(args[1])
    return nodelist

@py_cst
def gen_iter(*args):
    "gen_iter: gen_for | gen_if "
    arg = args[0]
    nodelist = [py_symbol.gen_iter]
    assert arg[0] in (py_symbol.gen_for, py_symbol.gen_if)
    nodelist.append(arg)
    return nodelist

@py_cst
def gen_for(*args):
    "gen_for: 'for' exprlist 'in' or_test [gen_iter] "
    nodelist = [py_symbol.gen_for]
    assert args[0][0] == py_symbol.exprlist, toText(args[0][0])
    nodelist.append(Symbol(py_token.NAME,"for"))
    nodelist.append(args[0])
    nodelist.append(Symbol(py_token.NAME,"in"))
    assert args[1][0] == py_symbol.or_test, toText(args[1][0])
    nodelist.append(args[1])
    if len(args)>=3:
        assert args[2][0] == py_symbol.gen_iter, toText(args[2][0])
        nodelist.append(args[2])
    return nodelist

@py_cst
def gen_if(*args):
    "gen_if: 'if' old_test [gen_iter] "
    nodelist = [py_symbol.gen_if]
    assert args[0] == py_symbol.old_test, toText(args[0])
    nodelist.append(Symbol(py_token.NAME,"if"))
    nodelist.append(args[0])
    if len(args)>=2:
        assert args[1][0] == py_symbol.gen_iter, toText(args[1][0])
        nodelist.append(args[1])
    return nodelist

@py_cst
def testlist1(*args):
    "testlist1: test (',' test)* "
    nodelist = testlist(*args)
    nodelist[0] == [py_symbol.testlist1]
    return nodelist



class dict_of_dicts(dict):
    def __getitem__(self, key):
        d = dict.get(self, key, {})
        self[key] = d
        return d

    def __setitem__(self, key, val):
        assert isinstance(val, dict), "Value of type dict expected. %s found instead."%(type(val))
        dict.__setitem__(self, key, val)



