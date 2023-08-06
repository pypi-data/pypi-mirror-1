import EasyExtend
import EasyExtend.util
from EasyExtend.cst import py_symbol, py_token
#from pyutils.decorators import dump_data, load_obj
import string
import pprint
import warnings
import copy
import sys
from nfatracing import*

NFA_EXPANSION_OVERFLOW = 1500

class LeftRecursionWarning(Warning):
    def __init__(self,*args, **kwd):
        super(LeftRecursionWarning, self).__init__(*args, **kwd)
        self.rules = []

class NeedsMoreExpansionWarning(Warning): pass
class RightExpansionWarning(Warning): pass
class DriftingExpansionWarning(Warning): pass

warnings.simplefilter("always",LeftRecursionWarning)
warnings.simplefilter("always",NeedsMoreExpansionWarning)
warnings.simplefilter("always",RightExpansionWarning)

@EasyExtend.util.psyco_optimized
def combinations(l):
    if l == ():
        return ((),)
    else:
        return [(x,)+y for x in l[0] for y in combinations(l[1:]) if (y and x<y[0] or y==())]

def lower_triangle(lst):
    '''
    Converts list of integers ( or ordered values of another type ) into a list of pairs belonging
    to a lower triangle matrix.

    Example:

        >>> L = [1, 2, 3]
        >>> lower_triangle(L)
        [(1,2),(1,3),(2,3)]

    There is no sorting involved so when you keep a rotated list the result will differ:

        >>> L = [2, 1, 3]
        >>> lower_triangle(L)
        [(2,3),(1,2),(1,3)]

    Doubles will not be erased:

        >>> L = [3, 1, 3]
        >>> lower_triangle(L)
        [(1,3),(1,3)]

    '''
    _lst = list(lst)
    L = (_lst,_lst)
    return combinations(L)

def symbols(lst):
    res = set()
    for s in lst[1:]:
        if isinstance(s, list):
            res.update(symbols(s))
        else:
            res.add(s)
    return res


class NFAData:
    def __init__(self):
       self.nfas       = {}
       self.keywords   = []
       self.reachables = {}
       self.ancestors  = {}
       self.first_set  = {}
       self.traces     = {}
       self.used_symbols = set()
       self.terminals    = set()
       self.nonterminals = set()
       self.symbols_of   = {}
       self.expansion_target = {}


class NFADataGenerator(object):
    @classmethod
    def new(self, langlet, parser_type, transitions = None, rules = None):
        if parser_type == "Token":
            return NFADataGenerator_TrailLexer(langlet, transitions = transitions, rules = rules)
        else:
            return NFADataGenerator_TrailParser(langlet, transitions = transitions, rules = rules)

    def graph(self, nt):
        rtd = NFATracerDetailed(self.rules)
        return rtd.graph(nt)

    #@dump_data
    def create_all(self):
        self._collect_symbols()
        self._keywords()
        self._terminals()
        self._first_set(self.start_symbol)
        self._reachables()
        self._terminal_ancestors()
        return self.nfadata

    def _collect_symbols(self):
        self.used_symbols = set()
        for k,v in self.rules.items():
            S = symbols(v[0])
            self.nfadata.used_symbols.update(S)
            self.nfadata.symbols_of[k] = S

    def _keywords(self):
        if not self.nfadata.used_symbols:
            self._collect_symbols()
        self.nfadata.keywords = set(s for s in list(self.nfadata.used_symbols) if isinstance(s, str))

    def _terminals(self):
        for s in list(self.nfadata.used_symbols):
            if s in self.nfadata.keywords:
                self.nfadata.terminals.add(s)
            elif s%512<256:
                self.nfadata.terminals.add(s)
            else:
                self.nfadata.nonterminals.add(s)

    def reduced_nfa(self, start):
        '''
        Computes a nfa while skipping any skippable labels.
        '''
        reduced = {}
        tracer    = NFATracerDetailed(self.nfadata.nfas)
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

    def _last_set(self):
        '''
        The EndTrans(A) = { A_t1, ..., A_tk } is the set of "end transitions" of A i.e. those transitions
        that contain (None,'-',A). The LastSet(A) of A is defined recursively by EndTrans(A) together with
        the EndTrans of each element in EndTrans(A). Often LastSet(A) is just {None}. In those cases we
        do not care.

        This function computes the LastSets of all nodes in the NFA set.
        '''
        def end_trans(r):
            etrans = set()
            nfa = self.nfadata.nfas[r]
            start = nfa[2]
            for t in self.reduced_nfa(start).values():
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
        for r in self.nfadata.nfas:
            if last_sets.get(r) is None:
                compute_last_set(r)
        for r in last_sets:
            S = last_sets[r]
            for A in self.nfadata.reachables[r]:
                if not self.is_token(A):
                    S.update(last_sets[A])
        return last_sets


    def _first_set(self, state):
        rt = NFATracer(self.rules)
        try:
            selection = [s for s in rt.select(state) if s]
            self.nfadata.first_set[state] = selection
            for s in selection:
                if not self.nfadata.first_set.get(s) and self.rules.get(s):
                    self._first_set(s)
        except Exception:
            pass

    def expanded_transitions(self, r):
        class N:n = 0
        nfa = self.nfadata.nfas[r]
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


    def all_selections(self, r, full = True):
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

        rtd = NFATracerDetailed(self.rules)
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


    def span(self):
        def exhaust(nt):
            rtd = NFATracerDetailed(self.rules)
            visited = set()
            symbols = set()

            def get_selections(rt, state):
                tree = [state]
                selection = rt.select(state)
                for s in selection:
                    if s in visited or s[0] is None:
                        continue
                    visited.add(s)
                    symbols.add(s[0])
                    cloned = rt.clone()
                    tree.append(get_selections(cloned, s[0]))
                return tree

            tree = get_selections(rtd, nt)
            return tree, symbols

        spanned = {}
        for nt in list(self.nfadata.nonterminals):
            tree, symbols = exhaust(nt)
            flt = self.flatten(tree)
            if not isinstance(flt[0], list):
                flt = [flt]
            spanned[nt] = (symbols, flt)
        return spanned

    def cyclefree_traces(self):
        cfree_traces = {}
        spanned = self.span()
        # pprint.pprint(spanned)
        for r, (sym, lst) in spanned.items():
            cfree_traces[r] = lst
        return cfree_traces


    def flatten(self,lst):
        if not isinstance(lst, list) or len(lst)==1:
            return lst
        else:
            flst = []
            for item in lst:
                fl = self.flatten(item)
                if isinstance(fl, list) and isinstance(fl[0], list):
                    flst+=fl
                else:
                    flst.append(fl)
            res  = [[lst[0]]+item for item in flst[1:]]
            if len(res) == 1:
                return res[0]
            else:
                return res

    def _reachables(self):
        def get_reachables(state):
            reach = self.nfadata.reachables.get(state)
            if reach:
                return reach
            selection = [s for s in NFATracer(self.rules).select(state) if s!=None]
            self.nfadata.reachables[state] = set(selection)
            for s in selection:
                if self.is_token(s):
                    if isinstance(s, str):
                        self.nfadata.keywords.add(s)
                    continue
                self.nfadata.reachables[state].update(get_reachables(s))
            return self.nfadata.reachables[state]
        for r in self.rules:
            get_reachables(r)

    def _terminal_ancestors(self):
        _ancestors = {}
        for r, reach in self.nfadata.reachables.items():
            for s in reach:
                if is_token(s):
                    S = _ancestors.get(s, set())
                    S.add(r)
                    _ancestors[s] = S
        self.nfadata.ancestors = _ancestors


class NFADataGenerator_TrailParser(NFADataGenerator):
    def __init__(self, langlet, transitions = None, rules = None):
        assert transitions or rules
        self.start_symbol = langlet.symbol.file_input
        if rules:
            self.rules = rules
        else:
            self.rules = transitions.nfas
        self.sym_name  = langlet.parse_symbol.sym_name
        self.tok_name  = langlet.parse_token.tok_name
        self.nfadata = NFAData()
        self.nfadata.nfas = self.rules
        self.warn_cnt = 0

    def is_token(self, s):
        try:
            return s%512<256
        except TypeError:
            return True

    def node_name(self, item):
        return self.sym_name.get(item,"")+self.tok_name.get(item,"")

    def _get_follow_sets(self, start):
        '''
        returns all follow sets containing at least two elements
        '''
        follow = []
        for T in self.all_selections(start[0]):
            K = [label for label in T if label[0] is not None]
            if len(K)>1:
                follow.append(K)
        return follow

    def redux(self, label):
        if isinstance(label[1], int):
            return label
        else:
            return (label[0], label[1][1:], label[2])

    def check_embedded(self, label, rule, embedded):
        if (label, rule) in embedded:
            return False
        if (self.redux(label), rule) in embedded:
            nid_A = label[0]
            A = self.nfadata.nfas[nid_A]
            R_NAME = A[1].split(":")[0]
            Z = self.nfadata.nfas[rule]
            lineno = sys._getframe(0).f_lineno +1

            warnings.warn_explicit('no expansion of `%s` possible in rule\n\t\t `%s`!\n'%(R_NAME, Z[1]), ExpansionWarning, "nfadatagen.py", lineno)
            self.warn_cnt+=1
            return False
        return True

    #@EasyExtend.util.psyco_optimized
    #@dump_data
    def expand_all(self, fullexpansion = True):
        '''
        Expand each rule that requires expansion.
        '''
        self.size = sum(len(nfa[3]) for nfa in self.nfadata.nfas.values())
        visited = set()
        self.shifter = 100
        self.labels = set()
        for r in self.nfadata.nfas:
            if r not in visited:
                k = len(self.nfadata.nfas[r][3])
                self.expand(r, visited, fullexpansion)
                n = len(self.nfadata.nfas[r][3])
                if n-k>0:
                    print "Rule `%s` expanded. Rule size = %s labels."%(r,n)

        # TODO : this is an implementation wart. Avoid this completely. Check whether it is stable
        #        and how it behaves in the presence of left recursion
        not_fully_expanded = []
        for r in self.nfadata.nfas:
            if self.check_expanded(self.nfadata, r):
                not_fully_expanded.append(r)
                self.expand(r, set() , fullexpansion)
                self.check_expanded(self.nfadata, r, print_warning = True)

    def expand_transitions(self):
        for r in self.nfadata.nfas.keys():
            if r not in self.nfadata.expansion_target:
                nfa = self.nfadata.nfas[r]
                D_r = self.expanded_transitions(r)
                nfa[3] = D_r


    def expand(self, rule = 0, visited = set(), fullexpansion = True):
        '''
        Let K be the reduced NFA[r]. For each transition

            S -> {L1, ..., Ln}

        with at least two follow labels L1, L2 and Li!=None we determine
        the corresponding selection

            sel = {s1, ..., sk}

        From sel we build Ri = s1.reach \/ s2.reach \/ .... si.reach successively.

        If Ri intersects with s(i+1) find the first sj, j=1,...,i with

                sj.reach /\ s(i+1).reach

        Now embedd the smaller of both NFAs into K.

        Repeat this procedure for each transition T until Rn-1 /\ sn.reach = {}.
        '''

        # TODO: understanding Trail and expansion
        #
        # - convergence. The result seems to depend on the selection of the NFA that
        #                will be embedded. How does this dependency affect the behaviour of
        #                the NFA set.
        #
        # - failure. Under which constraints are the results finite? Avoidance of left
        #            recursion is one necessary criterion. What are the others?
        #            Goal: predict expansion conditions from unexpanded state.
        #
        # - power. Closely related to failure conditions is the domain of rules that can
        #          be reliably used with Trail. Construct this domain!
        #
        # - alternatives. Is explicit expansion really necessary or can we create a stack based
        #                 approach? What are the relationships to other approaches?
        #

        if not rule:
            rule = self.start_symbol

        def maybe_expand(r):
            if r and r not in visited and not self.is_token (r):
                k = len(self.nfadata.nfas[r][3])
                self.expand(r, visited)
                n = len(self.nfadata.nfas[r][3])
                if n-k>0:
                    print "Rule `%s` expanded. Rule size = %s labels."%(r,n)

        visited.add(rule)
        embedded = set()
        more = True
        must_select = False
        while more:
            more = False
            #nfa   = self.reduced_nfa(self.nfadata.nfas[rule][2])
            selections = self.all_selections(rule, fullexpansion)
            # print "len-selection", len(selections)
            if len(selections)>NFA_EXPANSION_OVERFLOW or len(selections)>5*self.size:
                raise OverflowError("NFA size > NFA_EXPANSION_OVERFLOW. Cannot expand rule `%s : %s`"%(rule, self.node_name(rule)))
            if self.warn_cnt>10:
                raise RuntimeError("More than ten expansion warnings issued. Expansion is terminated!")

            for follow in selections:
                selectable = sorted(list(set(s[0] for s in follow if s and s[0]!=None)))
                if len(selectable)<=1:
                    continue
                R = set()
                C = {}
                for i,s in enumerate(selectable):
                    tok_s = False
                    if self.is_token(s):
                        tok_s = True
                        S = set([s])
                    else:
                        S = self.nfadata.reachables[s]
                    if R&S:
                        for u in selectable[:i]:
                            tok_u,U = C[u]
                            if U&S:
                                if tok_s:
                                    k = u
                                elif tok_u:
                                    k = s
                                else:
                                    N_s = self.nfadata.nfas[s][3]
                                    N_u = self.nfadata.nfas[u][3]
                                    k = (s if len(N_s)<=len(N_u) else u)
                                break
                        for label in (label for label in follow if label[0] == k):
                            maybe_expand(label[0])
                            if not (label, rule) in embedded:
                                self.embedd_nfa(label, rule)
                                embedded.add((label, rule))
                                more = True
                        break
                    else:
                        R.update(S)
                        C[s] = (tok_s, S)
                else:
                    continue
                break
            else:
                break


    def embedd_nfa(self, label, target_rule):
        # print "embedd_nfa(self, label: %s, at: %s)"%(label, at)
        '''
        Embedd NFA rule defined by label ( or by label[0] ) within NFA rule defined by target_rule.

        The current implementation performs the embedding *explicitely*.
        '''
        nid_A = label[0]
        shifted = label[1]
        Z = self.nfadata.nfas[target_rule]
        A = self.nfadata.nfas[nid_A]
        if label[0] == target_rule:
            R_NAME = A[1].split(":")[0]
            lineno = sys._getframe(0).f_lineno +1

            warnings.warn_explicit('no expansion of `%s` possible in `%s`!'%(R_NAME, Z[1]), LeftRecursionWarning, "nfadatagen.py", lineno)
            self.warn_cnt+=1
            return

        # store reminder
        if not target_rule in self.nfadata.expansion_target:
            self.nfadata.expansion_target[target_rule] = copy.deepcopy(Z)

        start_A  = (A[2][0], self.shifter, A[2][0]) # shift
        nfa_A    = self.shift_state(A[3]) # shifted NFA will be embedded
        nfa_Z    = Z[3]
        follow_A = nfa_A[start_A]
        transit  = (label[0], SKIP )+label[1:]
        for key, follow in nfa_Z.items():
            if key == label:
                nfa_Z[transit] = follow
                del nfa_Z[label]
            try:
                k = follow.count(label)
                if k:
                    while k:
                        follow.remove(label)
                        k-=1
                    follow.extend(follow_A)
            except ValueError:
                pass
        for key, follow in nfa_A.items():
            for i,v in enumerate(follow):
                if v[0] == None:
                    new_follow = follow[:]
                    new_follow[i] = transit
                    nfa_Z[key] = new_follow
                    break
            else:
                if start_A == key:
                    continue
                nfa_Z[key] = follow


    def shift_state(self, nfa):
        '''
        Used to move indices on embedding.
        '''
        shift = self.shifter
        Z = {}
        for key, follow in nfa.items():
            new_follow = []
            for label in follow:
                if label[1] == SKIP:
                    new_follow.append((label[0],SKIP,label[2] + shift,label[3]))
                elif label[1] == '-':
                    new_follow.append(label)
                else:
                    new_follow.append((label[0], label[1] + shift, label[2]))
            if key[1] == SKIP:
                Z[(key[0],SKIP, key[2]+ shift,key[3])] = new_follow
            else:
                Z[(key[0], key[1] + shift , key[2])] = new_follow
        #print "LEN_NFA", len(nfa)
        self.shifter+=25
        return Z


    def check_expanded(self, nfamodule, rule = None, print_warning = False):

        def check(r, label, tracer, visited):
            must_trace = False
            labels    = tracer.select(label[0])
            selection = list(set(s[0] for s in labels if s and s[0]!=None))
            R = set()
            C = {}
            msg = ""
            for i,s in enumerate(selection):
                if self.is_token(s):
                    S = set([s])
                else:
                    S = nfamodule.reachables[s]
                if R&S:
                    for u in C:
                        if C[u]&S:
                            if self.is_token(s):
                                msg = "%s : %s -> FirstSet(%s) /\\ {%s} = %s\n"%(r, label, u, s, C[u]&S)
                            elif self.is_token(u):
                                msg = "%s : %s -> {%s} /\\ FirstSet(%s) = %s\n"%(r, label, u, s, C[u]&S)
                            else:
                                msg = "%s : %s -> FirstSet(%s) /\\ FirstSet(%s) = %s\n"%(r, label, u, s, C[u]&S)
                            lineno = sys._getframe(0).f_lineno +1
                            if print_warning:
                                warnings.warn_explicit(msg, NeedsMoreExpansionWarning, "nfadatagen.py", lineno)
                            must_trace = True
                    break
                else:
                    R.update(S)
                    C[s] = S

            for label in labels:
                if label[0] is not None and label not in visited:
                    visited.add(label)
                    subtracer = tracer.clone()
                    must_trace|=check(r, label, subtracer, visited)
            return must_trace
        must_trace = False
        if rule is None:
            rules = self.rules.keys()
        else:
            rules = [rule]

        for r in rules:
            nfa = self.rules[r]
            visited = set()
            tracer = NFATracerDetailed(nfamodule.nfas)
            start = nfa[2]
            must_trace|=check(r, start, tracer, visited)
        return must_trace


    def check_rightexpand(self):
        last_sets = self._last_set()
        warned = set()

        def format_stream(T, k):
            stream = []
            for t in [t for t in T[:k+2]]:
                if isinstance(t, int):
                    stream.append(self.node_name(t))
                else:
                    stream.append("'"+t+"'")
            return stream[0]+': '+' '.join(stream[1:])

        for r, traces in self.cyclefree_traces().items():
            for T in traces:
                for i in range(1,len(T)-1):
                    A = T[i]
                    B = T[i+1]
                    if (r,A,B) in warned or A == B:
                        continue
                    if self.is_token(B):
                        if B in last_sets.get(A, set()):
                            warn_text = "%s -> LastSet(%s) /\\ set(`%s`) != {}"%(r,self.node_name(A),B) #, format_stream(T,i))

                            warnings.warn_explicit(warn_text, RightExpansionWarning, "nfadatagen.py", sys._getframe(0).f_lineno-1)
                            warned.add((r,A,B))
                            break
                    else:
                        S = last_sets.get(A, set()) & self.nfadata.reachables.get(B, set())
                        if S:
                            warn_text = warn_text = "%s -> LastSet(%s) /\\ FirstSet(%s) != {}"%(r, self.node_name(A),self.node_name(B)) #,format_stream(T,i))

                            warnings.warn_explicit(warn_text, RightExpansionWarning, "nfadatagen.py", sys._getframe(0).f_lineno-1)
                            warned.add((r,A,B))
                            break


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#
#   NFADataGenerator_TrailLexer
#
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class PseudoTokenSet(dict):
    max_tid = 0
    def __init__(self, dct={}):
        dict.__init__(self, dct)

    def __setitem__(self, key, value):
        dict.__setitem__(self, key, value)
        PseudoTokenSet.max_tid = max(PseudoTokenSet.max_tid, key)

    def __repr__(self):
        d = {}
        for tid, pt in self.items():
            d[tid] = pt.litset
        return pprint.pformat(d)


class PseudoToken(object):
    def __init__(self, tid, litset, name = ""):
        if tid == -1:
            PseudoTokenSet.max_tid +=1
            self.tid = PseudoTokenSet.max_tid
        else:
            self.tid    = tid
        self.litset = litset
        self.name   = name

    def __repr__(self):
        return "<PT: %s , %-16s, %s>"%(self.tid, self.name, self.litset)


class NFADataGenerator_TrailLexer(NFADataGenerator_TrailParser):
    def __init__(self, langlet, transitions = None, rules = None):
        assert transitions or rules
        self.start_symbol = langlet.lex_symbol.token_input
        self.sym_name  = langlet.parse_symbol.sym_name
        self.tok_name  = langlet.parse_token.tok_name
        self.token_map = langlet.lex_token.token_map
        self.litset    = langlet.lex_token.litset
        if rules:
            self.rules = rules
        else:
            self.rules = transitions.nfas
        self.nfadata = NFAData()
        self.nfadata.nfas = self.rules
        self.pseudo_token = PseudoTokenSet()
        self.offset = langlet.LANGLET_OFFSET
        self.initial_pseudo_token()
        #pprint.pprint(self.pseudo_token, width = 360)

    def is_token(self, s):
        return ( s in self.nfadata.terminals or \
                 s in self.pseudo_token )

    def node_name(self, item):
        return self.sym_name.get(item,"")+self.tok_name.get(item,"")

    def initial_pseudo_token(self):
        for name, val in self.litset.__dict__.items():
            if not name.startswith("LS_"):
                continue
            tid = self.token_map[name[3:]]
            self.pseudo_token[tid] = PseudoToken(tid, val, name[3:])


    def expand_all(self, fullexpansion = True):
        super(NFADataGenerator_TrailLexer, self).expand_all(fullexpansion)
        self.nfadata.pseudo_token = self.pseudo_token


    def expand(self, rule = 0, visited = set(), fullexpansion = True):
        if not rule:
            rule = self.start_symbol
        start = self.nfadata.nfas[rule][2]
        nfa = self.nfadata.nfas[rule][3]
        self.expand_nt(rule, start, nfa, visited)
        self.expand_pseudo_token(rule, start, nfa)

    def expand_pseudo_token(self, rule, start, nfa):
        # print "EXPAND_PSEUDO", rule, start
        more = True
        while more:
            more = False
            kicked = []
            selections = self.all_selections(start[0])
            for trans in selections:
                follow = [f for f in trans if f[0]!=None and f not in kicked]
                if len(follow)<2:
                    continue
                pseudo_token = self.split(follow)
                for label, sets in pseudo_token.items():
                    # LS_label has been split into several sets, we check if the set is already a Litset of another
                    # PseudoToken. If this is not the case we create a new PseudoToken from this set.
                    nids = []
                    for S in sets:
                        if len(S) == 1:
                            nids.append(list(S)[0])
                            continue
                        for P in self.pseudo_token.values():
                            if P.litset == S:
                                nids.append(P.tid)
                                break
                        else:
                            pt = PseudoToken(-1, S)
                            self.pseudo_token[pt.tid] = pt
                            nids.append(pt.tid)
                            # print "NEW pt", pt

                    # Label substitution.
                    #
                    # Let L be a label with LS_L = LS_L1 \/ LS_L2 \/ ... \/ LS_Lk and {L,L1, ..., Lk}<follow.
                    # The set {L1,...,Lk} is computed using the split() method. We have now collected the nids of
                    # those labels. From the nids we create new labels L1', ..., Lk' and replace L be them:
                    #   1) if L occurs on the RHS of a transition replace it by {L1', ..., Lk'}
                    #   2) insert Li' as a key with the transitions of L.
                    #
                    label_follow = nfa[label]
                    del nfa[label]
                    kicked.append(label)
                    new_labels = []
                    for n in nids:
                        i = 0
                        new_label = (n, label[1]+i, label[-1])
                        while nfa.get(new_label):
                            i+=1
                            new_label = (n, label[1]+i, label[-1])
                        nfa[new_label] = label_follow
                        new_labels.append(new_label)
                    for trans in nfa.values():
                        if label in trans:
                            trans.remove(label)
                            trans+=new_labels
                    more = True

    def split(self, labels):
        # If for two pseudo-token A, B the corresponding Litsets intersect i.e.
        # K = LS_A /\ LS_B != {} we split those sets into LS_A-K, K, LS_B-K in an initial step.
        # An important special case is K = LS_A or K = LS_B.
        # Suppose K = LS_B, then we have pseudo_token[A] = [LS_A - LS_B, LS_B]. For LS_A - LS_B we
        # eventually need a new PseudoToken.
        pt_list, np_list = [],[]
        for label in labels:
            if label[0] in self.pseudo_token:
                pt_list.append(label)
            else:
                np_list.append(label)
        res = []
        pseudo_token = {}
        for i,A in enumerate(pt_list):
            LS_A = self.pseudo_token[A[0]].litset
            for B in pt_list[1+i:]:
                if A[0]!=B[0]:
                    LS_B = self.pseudo_token[B[0]].litset
                    K = LS_A & LS_B
                    if K:
                        if K!=LS_A:
                            pt = pseudo_token.get(A,[])
                            pt.append(K)
                            pseudo_token[A] = pt
                        if K!=LS_B:
                            pt = pseudo_token.get(B,[])
                            pt.append(K)
                            pseudo_token[B] = pt
                        #print "LABELS", labels
                        #print "SPLIT", "A = %s:%s, B = %s:%s, K = %s"%(A,LS_A,B,LS_B,K)
            for t in np_list:
                if t[0] in LS_A:
                    pt = pseudo_token.get(A,[])
                    pt.append(set(t[0]))
                    pseudo_token[A] = pt
        if pseudo_token:
            i = 1
            for A, sets in pseudo_token.items():
                R = [self.pseudo_token[A[0]].litset]
                for S in sets:
                    K = []
                    for T in R:
                        for r in T & S, T-S, S-T:
                            if r and r not in K:
                                K.append(r)
                    R = K
                pseudo_token[A] = R
        return pseudo_token


    def expand_nt(self, rule, start, nfa, visited):

        def maybe_expand(r):
            if r and r not in visited and not self.is_token (r):
                self.expand(r, visited)

        def intersect(R_A, R_B):
            for t in R_A:
                if t in self.pseudo_token:
                    LS_t = self.pseudo_token[t].litset
                    for u in R_B:
                        if u in self.pseudo_token:
                            if LS_t & self.pseudo_token[u].litset:
                                return True
                        else:
                            if u in LS_t:
                                return True
            return False

        def try_expansion(nids, follow, rule, embedded):
            for label in (label for label in follow if label[0] in nids):
                maybe_expand(label[0])
                if not (label, rule) in embedded:
                    self.embedd_nfa(label, rule)
                embedded.add((label, rule))
            return True

        visited.add(rule)
        expanded = set()
        embedded = set()
        bla = False
        while True:
            more = False
            #pprint.pprint(nfa)
            follow_sets = self._get_follow_sets(start)
            #if __DEBUG__:
            #    print "DEBUG - follow_sets", follow_sets
            for follow in follow_sets:
                follow = list(follow)
                selectable = [s[0] for s in follow if s]
                pairs = lower_triangle( selectable )
                for A,B in pairs:
                    rc = 0
                    if (A,B) in expanded:
                        continue
                    elif A in self.nfadata.terminals and not A in self.pseudo_token:
                        #elif self.is_token(A) and not A in self.pseudo_token:
                        if self.is_token(B):
                            pass
                        elif A in self.nfadata.reachables[B]:
                            rc = try_expansion([B], follow, rule, embedded)
                    elif self.is_token(B) and not B in self.pseudo_token:
                        if A in self.pseudo_token:
                            continue   # special case of two intersecting PT entities
                                       # is handled in expand_pseudo_token method
                        elif B in self.nfadata.reachables[A]:
                            rc =try_expansion([A], follow, rule, embedded)
                    elif A in self.pseudo_token:
                        if B in self.pseudo_token:
                            continue
                        R_B = self.nfadata.reachables[B]
                        if intersect([A],R_B):
                            rc = try_expansion([B], follow, rule, embedded)
                    elif B in self.pseudo_token:
                        R_A = self.nfadata.reachables[A]
                        if intersect([B],R_A):
                            rc = try_expansion([A], follow, rule, embedded)
                    elif self.nfadata.reachables[A] & self.nfadata.reachables[B]:
                        rc = try_expansion([A,B], follow, rule, embedded)
                    else:
                        R_A = self.nfadata.reachables[A]
                        R_B = self.nfadata.reachables[B]
                        if intersect(R_A, R_B) or intersect(R_B, R_A):
                            rc = try_expansion([A,B], follow, rule, embedded)
                    if rc:
                        expanded.add((A,B))
                        more = True
            if not more:
                #pprint.pprint(nfa)
                break



def check_grammar(langlet, typ):
    if typ == "Token":
        nfadata = NFADataGenerator.new(langlet, "Token", langlet.lex_nfa)
    else:
        nfadata = NFADataGenerator.new(langlet, "Parser", langlet.parse_nfa)
    nfadata.create_all()
    nfadata.expand_all()
    nfadata.check_rightexpand()

def nfa2dot(nfa, langlet):
    '''
    Create dot diagram
    '''
    start = nfa[2]
    transitions = nfa[3]
    nodes = []
    nodes.append('    nodeNone[label = "{None|-|%s}"];'%start[0])

    def Node(label):
        if len(label) == 3:
            return '    node%d[label = "{%s|{%s|%s|%s}}"];'%(label[1], node_name(label[0],langlet),label[0],label[1],label[2])
        else:
            return '    node%d[label = "{%s|{%s|.|%s|%s}}", color = green];'%(label[2], node_name(label[0],langlet),label[0],label[2],label[3])

    def Arrows(label):
        form   = "    node%s -> node%s;"
        idx = (label[2] if label[1] == SKIP else label[1])
        arrows = []
        for f in transitions[label]:
            if f[0] is None:
                arrows.append(form%(idx,"None"))
            else:
                idx2 = (f[2] if f[1] == SKIP else f[1])
                arrows.append(form%(idx,idx2))
        return "\n".join(arrows)

    arrows = []
    for label in transitions:
        nodes.append(Node(label))
        arrows.append(Arrows(label))
    graph = "digraph G {\n    node [shape = record,height=.1];\n"
    graph+="\n".join(nodes)+"\n"
    graph+="\n".join(arrows)
    graph+="\n}\n"
    return graph



def check_last_set_zero():
    import EasyExtend.langlets.zero.langlet as langlet
    nfadata = NFADataGenerator.new(langlet, "Parser", langlet.parse_nfa)
    nfadata.create_all()
    nfadata.expand_all()
    nfadata.check_rightexpand()

def check_grammar(langlet, typ):
    if typ == "Token":
        nfadata = NFADataGenerator.new(langlet, "Token", langlet.lex_nfa)
    else:
        nfadata = NFADataGenerator.new(langlet, "Parser", langlet.parse_nfa)
    nfadata.create_all()
    nfadata.expand_all()
    nfadata.check_rightexpand()


def create_new_nfa(langlet, typ):
    '''
    Used for testpurposes...
    '''
    from pyutils.decorators import dump_data, load_obj
    try:
        nfadatagen = load_obj()
    except:
        parser_type = "Grammar" if typ == "parse_nfa" else "Token"
        import nfagen
        nfagenerator = nfagen.NFAGenerator(langlet, parser_type)
        nfas = nfagenerator.create_all()
        nfadatagen = NFADataGenerator.new(langlet, parser_type, rules = nfas)
        nfadatagen.create_all()
        dump_data(nfadatagen)
    import time
    a = time.time()
    print "Start NFA expansions..."
    nfadatagen.expand_all()
    k = len(nfadatagen.nfadata.expansion_target)
    if k == 1:
        print "1 NFA expanded."
    else:
        print "%d NFAs expanded."%k
    print "EXPANSION TIME", time.time() - a
    return nfadatagen

def create_new_nfa_x(langlet, typ):
    '''
    Used for testpurposes...
    '''
    parser_type = "Grammar" if typ == "parse_nfa" else "Token"
    import time
    a = time.time()
    print "Start NFA expansions..."
    nfadatagen = load_obj()
    #nfadatagen.expand_all()
    k = len(nfadatagen.nfadata.expansion_target)
    if k == 1:
        print "1 NFA expanded."
    else:
        print "%d NFAs expanded."%k
    print "EXPANSION TIME", time.time() - a
    return nfadatagen




def check_no_indent():
    import EasyExtend.langlets.no_indent.langlet as langlet
    create_new_nfa(langlet, "parse_nfa")

def create_gallery_langlet():
    import EasyExtend.langlets.gallery.langlet as langlet
    nfadatagen = create_new_nfa(langlet, "lex_nfa")

def create_p4d_langlet():
    import EasyExtend.langlets.p4d.langlet as langlet
    nfadatagen = create_new_nfa(langlet, "parse_nfa")

if __name__ == '__main__':
    create_gallery_langlet()


