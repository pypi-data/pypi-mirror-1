from nfatracing import NFATracer, NFATracerDetailed

def is_token(s):
    if type(s) == str:
        return True
    return s%512<256

def symbols(lst):
    res = set()
    for s in lst[1:]:
        if isinstance(s, list):
            res.update(symbols(s))
        else:
            res.add(s)
    return res

def collect_symbols(nfas):
    used_symbols = set()
    symbols_of   = {}
    for k,v in nfas.items():
        S = symbols(v[0])
        used_symbols.update(S)
        symbols_of[k] = S
    return used_symbols, symbols_of

def keywords(used_symbols):
    return set(s for s in used_symbols if type(s) == str)

def terminals(used_symbols, keywords):
    terminals = set()
    nonterminals = set()
    for s in used_symbols:
        if s in keywords:
            terminals.add(s)
        elif s%512<256:
            terminals.add(s)
        else:
            nonterminals.add(s)
    return terminals, nonterminals

def reduced_nfa(nfas, start):
    '''
    Computes a nfa while skipping any skippable labels.
    '''
    reduced = {}
    tracer    = NFATracerDetailed(nfas)
    visited   = set()

    def trace(tracer, label, visited):
        selection = tracer.select(label[0])
        reduced[label] = selection
        visited.add(label)
        for s in selection:
            if s[0] is not None and s not in visited:
                trace(tracer.clone(), s, visited)

    trace(tracer, start, visited)
    return reduced

def last_set(nfas, reachables):
    '''
    The EndTrans(A) = { A_t1, ..., A_tk } is the set of "end transitions" of A i.e. those transitions
    that contain (None,'-',A). The LastSet(A) of A is defined recursively by EndTrans(A) together with
    the EndTrans of each element in EndTrans(A). Often LastSet(A) is just {None}. In those cases we
    do not care.

    This function computes the LastSets of all nodes in the NFA set.
    '''
    def end_trans(r):
        etrans = set()
        nfa = nfas[r]
        start = nfa[2]
        for t in reduced_nfa(nfas, start).values():
            if (None, '-', r) in t:
                for label in t:
                    if label[0] is not None:
                        etrans.add(label[0])
        return etrans

    last_sets = {}
    visited = set()
    def compute_last_set(r):
        visited.add(r)
        S = last_sets.get(r)
        if S:
            return S
        else:
            etrans = end_trans(r)
            for t in tuple(etrans):
                if not self.is_token(t):
                    if t not in visited:
                        etrans.update(compute_last_set(t))
                    else:
                        etrans.update(last_sets.get(t,set()))
            last_sets[r] = etrans
        return etrans

    last_sets = {}
    for r in nfas:
        if last_sets.get(r) is None:
            compute_last_set(r)
    for r in last_sets:
        S = last_sets[r]
        for A in reachables[r]:
            if not is_token(A):
                S.update(last_sets[A])
    return last_sets


def first_set(nfas, r):
    _first_set = {}
    try:
        selection = [s for s in NFATracer(nfas).select(r) if s]
        _first_set[state] = selection
        for s in selection:
            if not _first_set.get(s) and nfas.get(s):
                _first_set.update(first_set(nfas, s))
    except Exception:
        pass
    return _first_set

def expanded_transitions(nfas, r):
    class N:n = 0
    nfa = nfas[r]
    transitions = nfa[3]
    exp_trans = {}
    visited = {}

    for L0, T in transitions.items():
        D_T = {}
        for L in T:
            S = D_T.get(L[0], set())
            S.add(L)
            D_T[L[0]] = S
        exp_trans[L0] = D_T

    def get_index(k,S):
        return (k,tuple(sorted([(L[1] if L[1]!='.' else L[2]) for L in S])))

    def new_label(n, k):
        return (k, n, '*')

    def produce(D_T):
        for k, S in D_T.items():
            if len(S) == 1:
                continue
            else:
                I = get_index(k,S)
                if I in visited:
                    continue
                else:
                    D_S = {}
                    N.n+=1
                    for L in S:
                        T_L = exp_trans[L]
                        for m, R in T_L.items():
                            M = D_S.get(m, set())
                            M.update(R)
                            D_S[m] = M
                    NL = new_label(N.n, k)
                    visited[I] = NL
                    exp_trans[NL] = D_S
                    produce(D_S)

    for D_T in exp_trans.values():
        produce(D_T)
    for D_T in exp_trans.values():
        for k, S in D_T.items():
            I = get_index(k,S)
            if I in visited:
                D_T[k] = visited[I]
            else:
                D_T[k] = S.pop()
    return exp_trans


def all_selections(nfas, r, full = True):
    # requires some less primitive memoization techniques...
    #
    # If label L has been used it shall not be reused. But there might be a label L'
    # that exists in a selection together with L and the combination of L + L'gives rise to a
    # new selection. So we actually have to store all combinations of labels for meomoization.
    #
    # We do this using two types of dicts:
    #
    #    global_v -- {label: collection of set-of-labels}
    #    local_v -- {nid: (bool, set-of-labels) }
    #
    # The algo works as follows:
    # 1. If L is not in global_v then do some selection - unless there has been a selection already with the same nid
    #    triggered by the current selection containing L. This can be looked up in local_v.
    # 2. In either case add L to local_v.
    # 3. If L has been noticed in global_v keep the set-of-labels in local_v with the correct nid and add L to it.
    #    If the length is > 1 iterate through the collection of sets-of-labels in global_v and check whether one
    #    could be found that does not contain the local set of labels.

    # print "all-selections", r
    def update_global_v(global_v, S):
        for L in S:
            collection = global_v.get(L,[])
            for K in collection:
                if K.issubset(S):
                    K.update(S)
                    break
            else:
                collection.append(S)
            global_v[L] = collection

    def use_label(label, local_v, global_v):
        use = False
        s = label[0]
        done, S = local_v.get(s, (False, set()))
        if label not in global_v:
            if not S:
                use = True
            else:
                if not done:
                    use = True
            S.add(label)
        else:
            S.add(label)
            collection = global_v[label]
            for R in collection:
                if S.issubset(R):   # nothing to do
                    break
                elif R.issubset(S) and len(R)<len(S):
                    if not done:
                        use = True
                    break
            else:
                collection.append(S)
                if not done:
                    use = True
        local_v[s] = (use, S)
        update_global_v(global_v, S)
        return use

    rtd = NFATracerDetailed(nfas)
    global_v = {}
    selections = []
    visited = set()

    def compute_selections(rt, state):
        selection = rt.select(state)
        selections.append(selection)
        local_v = {}
        for L in selection:
            s = L[0]
            used = s in local_v
            if s is None:
                continue
            if full:
                if not use_label(L, local_v, global_v):
                    continue
            elif L in visited:
                continue
            visited.add(L)
            cloned = rt.clone()
            compute_selections(cloned, s)
    compute_selections(rtd, r)
    return selections


def cyclefree_traces(nfas, nonterminals):
    cfree_traces = {}
    spanned = span_traces(nfas, nonterminals)
    # pprint.pprint(spanned)
    for r, (sym, lst) in spanned.items():
        cfree_traces[r] = lst
    return cfree_traces


def span_traces(nfas, nonterminals):
    class Node:
        def __init__(self, label, parent):
            self.label  = label
            self.parent = parent
            self.children = []
            self.circle = False

        def in_trace(self, label):
            parent = self.parent
            while parent:
                if parent.label == label:
                    return True
                parent = parent.parent
            return False

        def trace(self):
            _trace = [self.label]
            parent = self.parent
            while parent:
                _trace.append(parent.label)
                parent = parent.parent
            return _trace

    def exhaust(start):
        leafs = []
        circles = []
        def build_node(tracer, state, parent = None):
            node = Node(state, parent)
            nid = state[0]
            selection = tracer.select(nid)
            for S in selection:
                if S[0] == None:
                    leafs.append(Node(S, node))
                elif node.in_trace(S):
                    N = Node(S, node)
                    _trace = N.trace()
                    i = _trace[1:].index(S)
                    circles.append(_trace[:i+1])
                    leafs.append(N)
                else:
                    build_node(tracer.clone(), S, node)

        build_node(NFATracerDetailed(nfas), start)
        return leafs, circles

    spanned = {}
    for nt, nfa in nfas.items():
        start = nfa[2]
        leafs, circles = exhaust(start)
        spanned[nt] = (leafs, circles)
    return spanned


def flatten_list(lst):
    if not type(lst) == list or len(lst)==1:
        return lst
    else:
        flst = []
        for item in lst:
            fl = flatten_list(item)
            if type(fl) == list and type(fl[0]) == list:
                flst+=fl
            else:
                flst.append(fl)
        res  = [[lst[0]]+item for item in flst[1:]]
        if len(res) == 1:
            return res[0]
        else:
            return res

def reachables(nfas):
    def get_reachables(r, _reachables):
        reach = _reachables.get(r)
        if reach:
            return reach
        selection = [s for s in NFATracer(nfas).select(r) if s!=None]
        _reachables[state] = set(selection)
        for s in selection:
            if is_token(s):
                continue
            _reachables[state].update(get_reachables(s))
        return _reachables[state]

    _reachables = {}
    for r in nfas:
        get_reachables(r)
    return _reachables

def terminal_ancestors(reachables):
    _ancestors = {}
    for r, reach in reachables.items():
        for s in reach:
            if is_token(s):
                S = _ancestors.get(s, set())
                S.add(r)
                _ancestors[s] = S
    return _ancestors

#from reverb import*

def lexnfa2regex(nfa, pseudo_token):
    '''
    Constructs a set of regular expressions from an nfa ::

        If NFA = {L1:T1, ..., Ln:Tn} is given we try to construct a regex for each label L
        that matches the same string as an NFALexer would match following the standard parsing
        routine.
    '''
    # Idea: we can construct
    regexps = {}
    start       = nfa[2]
    transitions = nfa[3]
    ptoken = {}
    for nid, cset in pseudo_token.items():
        if len(cset) == 0:
            ptoken[nid] = '.'
        else:
            ptoken[nid] = '['+''.join(list(cset))+']'
    label = start
    visted = set()
    return ptoken

if __name__ == '__main__':
    import pprint
    import EasyExtend.langlets.zero.lexdef.lex_nfa as lex_nfa
    #pprint.pprint( lex_nfa.nfas[322] )
    pprint.pprint(lexnfa2regex( lex_nfa.nfas[322], lex_nfa.pseudo_token))
    used_symbols, symbols_of = collect_symbols(lex_nfa.nfas)
    terms, nonterms = terminals(used_symbols, keywords(used_symbols))
    #pprint.pprint(span_traces(lex_nfa.nfas, nonterms))

    T = {(11, 1, 257): [(15, 3, 257), (11, 2, 257), (None, '-', 257)],
         (11, 2, 257): [(15, 3, 257), (11, 2, 257), (None, '-', 257)],
         (15, 3, 257): [(15, 3, 257), (11, 2, 257), (None, '-', 257)],
         (257, 0, 257): [(11, 1, 257)]}

    S = "dzduzdddzzd6373673636"



    S11 = 'ACBEDGFIHKJMLONQPSRUTWVYXZ_acbedgfihkjmlonqpsrutwvyxz'
    S15 = '1032547698'





