# URL:     http://www.fiber-space.de
# Author:  Kay Schluehr <easyextend@fiber-space.de>
# Date:    10 May 2006
#--------------------------------------------------------------------------------------


from cst import*
import sys
from cstdef25 import*
import random
import fstools
import warnings
import string
import EasyExtend.util

class GrammarConformanceWarning(Warning): pass
warnings.simplefilter("always",GrammarConformanceWarning)

##################################################################################################
#
# classes used to extend nodes
#
##################################################################################################

class cstnode(list):
    def __init__(self, lst=[]):
        list.__init__(self, lst)
        self.msg = ""
        self.transformable = False
        self.handler  = None
        self.prepared = False

    def __message__(self):
        return self.msg


class add_info(object):
    def __init__(self, lineno, column, comment):
        self.lineno   = lineno
        self.column   = column
        self.comment  = comment

    def __repr__(self):
        if self.comment:
            comment = self.comment[0][1]
            return str(self.lineno)+"  "+str(self.column)+"  "+comment
        else:
            return str(self.lineno)+"  "+str(self.column)

##################################################################################################
#
# node property checker and node id functions
#
##################################################################################################

def smallest_node(node):
    if is_node(node, py_symbol.atom):
        return node
    if len(node) == 2:
        return smallest_node(node[1])
    else:
        return node

def is_node(node, nid):
    return node[0] == nid or node[0]%512 == nid%512

def is_token(nid):
    try:
        return nid%512<256
    except TypeError:
        return True

def remove_from( A, Z ):
    id_A = id(A)
    for i, item in enumerate(Z):
        if id(item) == id_A:
            del Z[i]
            return Z
    return Z



def is_simple(node):
    '''
    check for the structure [a,[b,[c,[...[k,[symbol.atom,...]]...]
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

def is_supersimple(node):
    '''
    checks for the structure [a,[b,[c,[...[k,[tid, ...]]...] where tid is a token nid. The node is
    basically a wrapper of a single token.
    '''
    py_atom = py_symbol.atom
    n = node
    while n:
        if n[0]%512 == py_atom:
            if len(n) == 2:
                return True
            else:
                return False
        elif n[0]%512<256:
            return True
        elif len(n) > 2:
            return False
        n = n[1]

def is_atomic(node):
    try:
        if node[0]%512 in ( py_symbol.atom, 1, 2, 3 ):
            return True
        else:
            if len(node) >= 3:
                return False
            else:
                return is_atomic(node[1])
    except TypeError:
        raise

@EasyExtend.util.psyco_optimized
def projection(node):
    '''
    The projection function takes a parse tree of an arbitrary langlet and maps it onto a
    a Python parse tree. This is done by shifting the node ids of each node to the left.
    Since each node id can be described by ::

        nid = n + k*512,  with n<512

    the node id of the Python node is just the rest of division by 512: n = nid%512
    '''
    try:
        if node[0]>MAX_PY_SYMBOL:
            node[0] = node[0]%512
        for item in node[1:]:
            if isinstance(item, (list, tuple)):
                projection(item)
    except IndexError:
        raise
    return node

def lift(node, LANGLET_OFFSET):
    '''
    Adds LANGLET_OFFSET to each node id N where n<LANGLET_OFFSET.
    @param node: node to be lifted.
    @param LANGLET_OFFSET: amount to be lifted.
    '''
    if node[0]<LANGLET_OFFSET:
        node[0] = node[0]+LANGLET_OFFSET
    for item in node[1:]:
        if isinstance(item, (list, tuple)):
            lift(item, LANGLET_OFFSET)
    return node

def get_node_name(langlet, nid, type = "parse"):
    if type == "parse":
        try:
            return langlet.symbol.sym_name[nid]
        except KeyError:
            pass
        try:
            return langlet.token.tok_name[nid]
        except KeyError:
            pass
    elif type == "lex":
        try:
            return langlet.lex_symbol.sym_name[nid]
        except KeyError:
            pass
        try:
            return langlet.lex_token.tok_name[nid]
        except KeyError:
            pass
    return "UNKNOWN"


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

def func_name(node):
    return node[2][1]

def proj_nid(node):
    return node[0]%512

def has_type(node, nid):
    return node[0]%512 == nid%512

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
    is_py = node_id<512
    tree_id = proj_nid(tree)
    node_id = node_id%LANGLET_OFFSET_SCALE
    if tree_id == node_id:
        return 0
    elif tree_id<256:
        return -1
    if is_py:
        try:
            s0 = hierarchy[tree_id]
            s1 = hierarchy[node_id]
            if s0>s1:
                return -1
        except KeyError:
            return 1
    else:
        return 1

##################################################################################################
#
# node checking
#
##################################################################################################

def check_node(node, target_langlet, strict = True):
    '''
    Recursive validity check of a CST node against a grammar.
    @param node: node to check.
    @param target_langlet: langlet to check against.
    @param strict: the modifier strict is used as follows
                   True  -> node id's must match those of the grammar precisely
                   False -> it suffices that projected node id's match those of the Python grammar
    '''
    import EasyExtend.trail.nfagen as nfagen
    from   EasyExtend.trail.nfatracing import NFATracerUnexpanded
    mod       = target_langlet.parse_nfa
    nfa_table = mod.nfas
    nid       = node[0]
    tracer    = NFATracerUnexpanded(mod)
    if strict:
        factor   = 10**7
        TERMINAL = target_langlet.LANGLET_OFFSET+255
        NAME = target_langlet.token.NAME
    else:
        factor   = 512
        TERMINAL = 255
        NAME     = 1

    error_msg = "<====  No grammar conformance!\n\n  ---->  Expected node(s): %s"
    error_msg_terminal = "<====  No grammar conformance! More nodes required. Expected node(s): %s"

    def annotate(node, sub, msg, selection):
        select_txt = "{ "
        for s in selection:
            if isinstance(s, int):
                name = get_node_name(target_langlet, s)
                if s%512<256:
                    select_txt+=name+" -- T'%d, "%s
                else:
                    select_txt+=name+" -- S'%d, "%s
            else:
                select_txt+="%s, "%s
        msg = msg%select_txt[:-2]+" }\n"
        if isinstance(sub, cstnode):
            sub.msg = msg
        elif isinstance(sub, list):
            n = cstnode(sub)
            n.msg = msg
            sid = id(sub)
            for i,item in enumerate(node):
                if id(item) == sid:
                    node[i] = n
                    break
        else:
            if isinstance(node[-1], cstnode):
                node[-1] = cstnode(node[-1])
                node[-1].msg = msg

    def filter_selection(selection, strictness):
        if strictness:
            return selection
        projected = []
        for s in selection:
            try:
                projected.append(s%512)
            except TypeError:
                projected.append(s)
        return projected


    def _check_node(node, nid, tracer, strictness):
        selection = filter_selection(tracer.select(nid), strictness)
        for sub in node[1:]:
            sub_nid = sub[0]%factor
            if isinstance(sub, list):
                if sub_nid == NAME:
                    if sub_nid in selection:
                        selector = sub_nid
                    elif sub[1] in selection:
                        selector = sub[1]
                    else:
                        annotate(node, sub, error_msg, selection)
                        return False
                    selection = filter_selection(tracer.select(selector), strictness)
                elif sub_nid in selection:
                    if sub_nid > TERMINAL:
                        new_tracer = NFATracerUnexpanded(mod)
                        rc = _check_node(sub, sub_nid, new_tracer, strictness)
                        if rc is False:
                            return False
                    selection = filter_selection(tracer.select(sub_nid), strictness)
                else:
                    annotate(node, sub, error_msg, selection)
                    return False
        if None not in selection:
            annotate(node, None, error_msg_terminal, selection)
            return False
        return True

    rc = _check_node(node, nid, tracer, strict)
    if not rc:
        target_langlet.pprint(node)

        warnings.warn_explicit("CST doesn't match target langlet grammar.", GrammarConformanceWarning, "csttools.py", lineno = sys._getframe(0).f_lineno)
    else:
        print "CST o.k"
    return rc

##################################################################################################
#
# node representation
#
##################################################################################################


def to_text(node_id):
    '''
    Returns textual representation of a node id regardless of the langlet.
    '''
    name = fstools.FSConfig.get_sym_name(node_id)
    if not name:
        name = fstools.FSConfig.get_tok_name(node_id)
    if not name:
        return "(node_id = %s) -> ???"%node_id
    return name


def prepare_source(source):
    '''
    Formats an indented source string by stripping away "leading" whitespaces.
    A whitespace block is considered as "leading" if has the size of the whitespace
    preceding the first non-whitespace token. So it actually dedents the source.

    @param source: source string
    '''
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
    return "\n".join(res).strip()+"\n"


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
        div, rest = divmod(node_id, LANGLET_OFFSET_SCALE)
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

        nid = node[0]%512
        if node[0] in mark or to_text(node[0]) in mark or ("> MAX_PY_SYMBOL" in mark and (nid > MAX_PY_SYMBOL or 256 > nid > MAX_PY_TOKEN )):
            s = " "*indent+toText(node[0])+"       <-------  \n"
            if stop == True:
                s+=" "*(indent+INDENT)+".... \n\n"
                return s
        else:
            if hasattr(node, "__message__"):
                msg = node.__message__()
            else:
                msg = ""
            ln = node[-1]
            if isinstance(ln, int):
                s = " "*indent+toText(node[0])+"     L`%s     %s"%((node[-1]),msg)+"\n"
            else:
                s = " "*indent+toText(node[0])+"   %s\n"%msg
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
                if item in string.whitespace:
                    k = ("' '"   if item == ' '  else
                         "'\\n'" if item == '\n' else
                         "'\\t'" if item == '\t' else
                         "'\\r'" if item == '\r' else
                         "'\\'"  if item == '\\' else
                         "''")
                else:
                    k = item
                s+=" "*(indent+INDENT)+k+"\n"
        if indent == 0:
            return "\n"+s+"\n"
        else:
            return s

    return node2text(node, indent = indent)

def pprint(node, mark = [], stop = True, indent = 0, short_form = False):
    print present_node(node, mark = mark, stop = stop, indent = indent, short_form = short_form)

def rule_error(langlet, cst, expected_nids, keywords = set(), parts = 10, type = "parse"):
    def get_symbols():
        try:
            return token.sym_name.items()
        except AttributeError:
            return token.token_map.items()

    if type == "parse":
        token = langlet.parse_token
    else:
        token = langlet.lex_token
    rule  ="Expected symbol(s) from applied grammar rule:  "+ get_node_name(langlet, cst[0], type)+": "
    words = []
    for i, item in enumerate(cst[1:]):
        if isinstance(item, (tuple,list)):
            nid = item[0]
            node_name = get_node_name(langlet, nid, type)
            if is_token(nid):
                if nid%512 not in range(7) or item[1] in keywords:
                    try:
                        words.append("'"+item[1]+"'")
                    except TypeError:
                        words.append(node_name)
                else:
                    words.append(node_name)
            else:
                words.append(node_name)
    nid_names = []
    for expnid in expected_nids:
        if expnid in keywords:
            nid_names.append(expnid)
        elif is_token(expnid):
            for value, nid in ((y,x) for (x,y) in get_symbols()):
                if expnid == nid:
                    if nid%512 not in range(7):
                        nid_names.append("'"+value+"'")
                    else:
                        nid_names.append(value)
                    break
            else:
                nid_names.append(get_node_name(langlet, expnid, type))
        else:
            nid_names.append(get_node_name(langlet, expnid, type))
    if len(nid_names) == 1:
        expected = nid_names[0]
    else:
        expected = "( "+" | ".join(nid_names)+" )"
    if len(words)>parts:
        rule+=" ".join(words[:3])+" { ... } "
        rule+=" ".join(words[-(parts+3):])
    else:
        rule+=" ".join(words)
    k = len(rule)
    rule+=" "+expected+"\n"+" "*(k+1)+len(expected)*"~"
    return rule

##################################################################################################
#
# simple node wrapper and manipulators
#
##################################################################################################


def node_replace(old, new):
    '''
    inplace replacement of old node by new new node.
    @param old: node to be replaced
    @param new: node replacement
    '''
    del old[:]
    old.extend(new)
    return old

def clone_node(node, with_marker = True):
    '''
    Creates an identical copy of node.
    '''
    if not isinstance(node, list):
        return node
    elif isinstance(node, cstnode):
        res = cstnode()
        res.msg = node.msg
        res.transformable = with_marker and node.transformable
        res.handler  = node.handler
        res.prepared = node.prepared
    else:
        res = cstnode([])
    for item in node:
        cloned = clone_node(item, with_marker)
        res.append(cloned)
    return res

def left_shift(node):
    '''
    inplace replacement of [k,[l,...]] by [l,...]
    '''
    rest = node[1]
    return node_replace(node, rest)

def replace_in(context, nid, in_nid, node):
    '''
    Replace all nodes N within i{context} where nid(N) = i{in_nid} by i{node}
    when a node M with nid(M) = i{nid} can be found in N.

    @param context: contextual cst node
    @param nid: node id that constraints the node to be replaced.
    @param in_nid: node id of the target node of replacement.
    @param node: substitution.
    '''
    assert proj_nid(node) == in_nid%512
    for _in in find_all(context, in_nid):
        if _in:
            if find_node(_in, nid):
                node_replace(_in, node)
                break

def make_node(item):
    if isinstance(item, (list, tuple)):
        try:
            return atomize(item)
        except (ValueError,TypeError):
            if item:
                if not isinstance(item[0], int):
                    if isinstance(item[0], list):
                        return item[0]
                    else:
                        raise
                return item

    elif isinstance(item, (int, long, float)):
        return atomize(Number(item))
    elif isinstance(item, (str, unicode)):
        return atomize(String(item))
    else:
        raise SyntaxError, "Cannot turn item %s into node"%item

def unparen(node):
    '''
    Unparenthesizes all subnodes of i{node} that are already atomic.

    Examples::
         (8)   -> 8
         ((a)) -> a
         (a+b) -> (a+b)  -!-  a+b is not atomic
    '''
    nid = proj_nid(node)
    if nid == py_symbol.atom:
        tlg = find_node(node, py_symbol.testlist_gexp, level = 1)
        if tlg and is_atomic(tlg):
            atomized_tlg = find_node(tlg, py_symbol.atom)
            node_replace(node, atomized_tlg)
    for item in node[1:]:
        if isinstance(item, (list, tuple)):
            unparen(item)
    return node

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
    '''
    Creates a new identifier from a string by appending a random number.
    '''
    return Name(name+"_"+str(random.randrange(100000)))


##################################################################################################
#
# specialized cst synthesis and manipulation functions
#
##################################################################################################

def left_distribute(a_atom, a_test, func = None):
    '''
    Suppose a_test is a predicate of the form `A == X or B > Y`. Then we map a_atom against the boolean
    expressions s.t. we yield `a_atom.A == X or a_atom.B > Y`.

    If func is available we distribute as `func(a_atom, A) == X or func(a_atom, B) > Y`.
    '''
    # Implementation:
    # 1) We seek for all not_test nodes in test down to level 3. For each not_test node we seek the comparison
    #    node without limitations of depth.
    # 2) The comparison node has the structure `expr (comp_op expr)*` If func is available we transform like
    #        any_expr(CST_CallFunc([[func]], [a_atom, expr])) (comp_op expr)*.
    # Otherwise we apply
    #        any_expr(CST_CallFunc("getattr", [a_atom, expr])) (comp_op expr)*.
    import cstgen
    _not_tests = find_all(a_test, py_symbol.not_test, level = 3)
    for nt in _not_tests:
        _comparison = find_node(nt, py_symbol.comparison)
        _expr = _comparison[1]
        _cloned = clone_node(_expr)
        if func:
            if func == ".":
                 _power    = find_node(_expr, py_symbol.power)
                 _trailer  = find_all(_power, py_symbol.trailer, level = 1)
                 _name     = find_node(_power, py_token.NAME)
                 _power[1] = atomize(a_atom)
                 _power.insert(2, trailer(".", _name))
            else:
                node_replace(_expr, any_expr(cstgen.CST_CallFunc(func, [a_atom, _cloned])))
        else:
            _cloned = clone_node(_expr)
            node_replace(_expr, any_expr(cstgen.CST_CallFunc("getattr", [a_atom, _cloned])))


def varargs2arglist(varargs):
    """
    This function is used to turn the arguments of a function defintion into that of a function
    call.

    Rationale: ::
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
    """
    Creates a dictionary from a varargs node.
    @param varargs: node of type varargslist.
    @return: dict of following structure: {'args': dict, 'defaults': dict, 'star_args': dict, 'dstar_args': dict}
    """
    assert proj_nid(varargs) == py_symbol.varargslist, py_symbol.sym_name[proj_nid(varargs)]
    signature = {'args':{}, 'defaults':{}, 'star_args': {}, 'dstar_args':{}, 'arglist': [] }
    n = len(varargs)-2
    i = 0
    current_name = ""
    while i<=n:
        item = varargs[1:][i]
        if proj_nid(item) == py_symbol.fpdef:
            if find_node(item, py_symbol.fplist):
                raise SyntaxError("Does not support tuple-structured arguments")
            else:
                current_name = item[1][1]
                signature['arglist'].append(current_name)
                signature['args'][current_name] = ()
        elif proj_nid(item) == py_symbol.test:
            signature['defaults'][current_name] = item
        elif proj_nid(item) == py_token.STAR:
            i+=1
            signature['star_args'][find_node(varargs[1:][i], py_token.NAME)[1]] = ()
        elif proj_nid(item) == py_token.DOUBLESTAR:
            i+=1
            signature['dstar_args'][find_node(varargs[1:][i], py_token.NAME)[1]] = {}
        i+=1
    return signature



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


def parens(node):
    return atomize(node, enforce = True)

def atomize(node, enforce = False):
    '''
    A lot of substitutions involve either a test or an expr node as a target. But it might happen that
    the node that shall be substituted is a child of an atom and replacing the parental expr node of this
    atom substitutes too much i.e. all trailer nodes following the atom.

    In this case we apply a trick which we called 'atomization'.
    Let n be a node ( e.g. expr, power, test etc.) with n.node_id > atom.node_id than we apply ::

         atom("(",testlist_gexp(any_test(n)),")")

    Syntactically atomization puts nothing but parentheses around the expression. Semantically the expression and
    its atomization are identical.

    @param enforce: wrapped even if node is already atomic. This causes an atom x being transformed int (x).
    '''
    nid = proj_nid(node)
    if not enforce:
        if is_atomic(node):
            if nid in (1,2,3):
                return [py_symbol.atom, node]
            else:
                return find_node(node, py_symbol.atom)
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
    n = find_node(_suite, py_symbol.simple_stmt, level = 1)
    if n:
        _args = [any_stmt(n)]
        if pos==0:
            _args.insert(0,_stmt)
        else:
            _args.append(_stmt)
        return node_replace(_suite, suite(*_args))
    else:
        nodes = find_all(_suite, py_symbol.stmt, level=1)
        if pos == -1:
            nodes.append(_stmt)
        else:
            nodes.insert(pos, _stmt)
        return node_replace(_suite, suite(*nodes))

def normalize(node):
    '''
    Sometimes a function f is defined using a simple_stmt node wrapping its SUITE. ::

       def f(x):pass

    Trying to insert a stmt node into f's SUITE will cause a wrong statement ::

       def f(x):stmt
       pass

    To prevent this we turn the simple_stmt node based SUITE of the original f into a
    stmt node based one which yields the correct result ::

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

def wrap_arg(arg):
    if isinstance(arg,int):
        return any_test(Number(arg))
    elif isinstance(arg,str):
        if arg[0] in ("'",'"'):
            return any_test(String(arg[1:-1]))
        elif arg[0] in string.digits:
            return any_test(Number(arg))
        else:
            return any_test(Name(arg))
    elif isinstance(arg,list):
        return any_test(arg)

def pushstmt(stmt1, stmt2):
    '''
    If stmt1 has following structure ::

        EXPR1:
            STMT11
            ...
            STMT1k
            EXPR2:
                STMT21
                ...
                STMT2m

    then we insert the second argument stmt2 at the end ::

        EXPR1:
            STMT11
            ...
            STMT1k
            EXPR2:
                STMT21
                ...
                STMT2m
      -->       stmt2
    '''
    SUITE = find_node(stmt1, py_symbol.suite)
    while True:
        _stmts = find_all(SUITE, py_symbol.stmt, level = 1)
        _stmt  = _stmts[-1]
        _suite = find_node(_stmt, py_symbol.suite)
        if not _suite:
            _stmts.append(stmt2)
            return stmt1
        else:
            SUITE = _suite


################################################################################
#
# Search and node retrieval functions
#
################################################################################

def find_node(tree, node_id, level = 10000, exclude = []):
    '''
    finds one node with a certain node_id.
    '''
    if level<0:
        return
    res = node_cmp(tree, node_id)
    if res == 0:
        return tree
    elif res == -1:
        return
    for sub in tree[1:-1]:
        if sub[0] not in exclude:
            res = find_node(sub, node_id, level=level-1, exclude = exclude)
            if res:
                return res
    if isinstance(tree[-1], (list, tuple)) and tree[-1][0] not in exclude:
        return find_node(tree[-1], node_id, level=level-1, exclude = exclude)

def remove_node(tree, node, level = 10000, exclude = []):
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
        if level<0:
            raise StopIteration
        res = node_cmp(tree, node_id)
        if res == 0:
            yield tree
        elif res == -1:
            raise StopIteration
        for sub in tree[1:]:
            if isinstance(sub, (list, tuple)) and sub[0] not in exclude:
                for item in find_all(sub, node_id, level=level-1, exclude = exclude):
                    if item:
                        yield item
    except Exception, e:
        raise e

def find_all_of(tree, node_ids = [], level=10000, exclude = []):
    '''
    generator that finds all nodes with a certain node_id.
    '''
    return list(find_all_of_gen(tree, node_ids, level, exclude))

def find_all_of_gen(tree, node_ids = [], level=10000, exclude = []):
    '''
    generator that finds all nodes with a certain node_id.
    '''
    try:
        for node_id in node_ids:
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

class Chain(object):
    def __init__(self, chain):
        self._chain = chain

    def step(self):
        n = len(self._chain)
        if n == 1:
            return self._chain[-1], None
        elif n>1:
            return self._chain[-1], Chain(self._chain[:-1])
        else:
            return None, None

    def unfold(self):
        nd, chain = self.step()
        lst = [nd]
        if chain:
            return lst+chain.unfold()
        else:
            return lst

def find_node_chain(tree, nid, level = 10000, exclude = [], chain = []):
    '''
    Find node and returns as node chain.
    '''
    res = node_cmp(tree, nid)
    if res == 0:
        return Chain(chain+[tree])
    elif res == -1:
        return
    if level<0:
        return
    for sub in tree[1:-1]:
        if sub[0] not in exclude:
            res = find_node_chain(sub, nid, level=level-1, exclude = exclude, chain = chain+[tree])
            if res:
                return res

    if isinstance(tree[-1], (list, tuple)) and tree[-1][0] not in exclude:
        return find_node_chain(tree[-1], nid, level=level-1, exclude = exclude, chain = chain+[tree])

def find_all_chains_gen(tree, node_id, level=10000, exclude = [], chain = []):
    '''
    generator that finds all nodes with a certain node_id.
    '''
    try:
        res = node_cmp(tree, node_id)
        if res == 0:
            yield Chain(chain+[tree])
        elif res == -1 or level<0:
            raise StopIteration
        for sub in tree[1:]:
            if isinstance(sub, (list, tuple)) and sub[0] not in exclude:
                for item in find_all_chains(sub, node_id, level=level-1, exclude = exclude, chain = chain+[tree]):
                    if item:
                        yield item
    except Exception, e:
        raise e

def find_all_chains(tree, node_id, level=10000, exclude = [], chain = []):
    '''
    generator that finds all nodes with a certain node_id.
    '''
    return list(find_all_chains_gen(tree, node_id, level = level, exclude = exclude, chain = chain))

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

def get_node(node, nid):
    return find_node(node, nid, level = 1)

def get_one_of(node, node_ids):
    return find_one_of(node, node_ids, level = 1)

def get_all(node, nid):
    return find_all(node, nid, level = 1)

def get_all_of(node, node_ids):
    return find_all_of(node, node_ids, level = 1)

# import cstgen to provide a single interface to all kinds of csttools
from cstgen import*

if __name__ == '__main__':
    pass
