'''
libcst is a general purpose CST library.
'''
import random
from EasyExtend.trail.nfatracing import NFATracer
import EasyExtend.langlets.zero.langlet as zero_langlet

class RandomExpr(object):
    def __init__(self, langlet = zero_langlet):
        self.langlet = zero_langlet
        self.symbol    = self.langlet.parse_symbol
        self.token     = self.langlet.parse_token

    def randcst(self, start, tracer, normlen):
        nid = start
        _trace = []
        while True:
            selection  = tracer.select(nid)
            if None in selection and len(_trace)>=normlen:
                return [start, _trace]
            k = len(selection)
            nid = selection[random.randint(0,k-1)]
            if nid is None:
                return [start, _trace]
            _trace.append(nid)



    def randexpr(self, normbranches=3):
        tracer = NFATracer(self.langlet.parse_nfa.nfas)
        expr = self.symbol.expr
        nodelist = self.randcst(expr, tracer, random.randint(1,normbranches))
        sublist = nodelist[1]

    def randtest(self, maxbranches=10):
        pass

    def randstmt(self, maxbranches=10):
        pass

randexp = RandomExpr()
print randexp.randexpr()

