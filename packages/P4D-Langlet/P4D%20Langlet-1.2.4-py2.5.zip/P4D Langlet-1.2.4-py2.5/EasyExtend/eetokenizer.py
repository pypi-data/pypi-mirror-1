from EasyExtend.trail.nfalexer import NFALexer, TokenStream
from EasyExtend.eetransformer import transform
from EasyExtend.eeoptions import EEShow
import EasyExtend.util
import pprint
import sys

class StopTokenizing(Exception): pass

def post(f):
    f.post_lex_handler = True
    return f

class BaseTokenizer(EEShow):
    '''
    Abstract base class of Tokenizer classes.
    '''
    def __init__ (self, langlet):
        self.lexer = NFALexer(langlet)
        self.langlet = langlet
        self.options = langlet.options
        self.filename = "<input>"
        self._handler = {}

    def post_lex(self, scan):
        stream = []
        for tok in scan:
            tok[0] = tok[0][0]-256
            tok[2] = tok[2][0]
            stream.append(tok)
        return stream

    def add_token(self, tok, stream):
        tok[0]=tok[0]-256
        stream.append(tok)

    def set_handler(self):
        for name in dir(self):
            obj = getattr(self, name)
            if hasattr(obj, "post_lex_handler"):
                try:
                    nid = getattr(self.langlet.lex_symbol, name)
                    self._handler[nid] = obj
                except AttributeError:
                    obj.im_func.post_lex_handler = False

    @EasyExtend.util.psyco_optimized
    def tokenize_file(self, filename):
        self.filename = filename
        source = open(filename).read()
        source = source.rstrip()+"\n"
        scan = self.lexer.scan(TokenStream(source, fileinfo = filename))
        return self.post_lex(scan)

    @EasyExtend.util.psyco_optimized
    def tokenize_fileobj(self, fileobj):
        self.filename = fileobj.name
        source = fileobj.read()
        source = source.rstrip()+"\n"
        scan = self.lexer.scan(TokenStream(source, fileinfo = self.filename))
        return self.post_lex(scan)

    @EasyExtend.util.psyco_optimized
    def tokenize_string(self, source):
        self.filename = "<string>"
        tokstream = TokenStream(source)
        scan = self.lexer.scan(tokstream)
        return self.post_lex(scan)

class Tokenizer(BaseTokenizer):
    def __init__(self, langlet):
        BaseTokenizer.__init__(self, langlet)
        self.parenlev  = 0
        self.scan = None
        self.indents = []

    def post_lex(self, scan):
        self.scan = scan
        self.maybe_show_scan(scan)
        self.set_handler()
        self.symbols = self.langlet.lex_symbol
        sym_left  = self.langlet.lex_nfa.reachables[self.symbols.LEFT]
        sym_right = self.langlet.lex_nfa.reachables[self.symbols.RIGHT]
        stream = []
        for pos, tok in enumerate(scan):
            tok[0] = tok[0][0]
            tid = tok[0]
            if tid in sym_left:
                self.LEFT(pos, tok, stream)
            elif tid in sym_right:
                self.RIGHT(pos, tok, stream)
            else:
                handler = self._handler.get(tid)
                if handler:
                    handler(pos, tok, stream)
                else:
                    self.default(pos, tok, stream)
        self.dedent_to(0, stream)
        self.terminate_stream(stream)
        self.indents = []
        self.parenlevl = 0
        return stream

    def default(self, pos, tok, stream):
        tok[2] = tok[2][0]
        self.add_token(tok, stream)

    def terminate_stream(self, stream):
        if stream:
            T = stream[-1]
            if T[0] == self.symbols.DEDENT:
                self.add_token([self.symbols.ENDMARKER, '', T[2], (0,0) ], stream)
            else:
                self.add_token([self.symbols.ENDMARKER, '', T[2]+1, (0,0) ], stream)
        else:
            self.add_token([self.symbols.ENDMARKER, '', 1, (0,0) ], stream)

    @post
    def dot_start(self, pos, tok, stream):
        "dot_start: '.' | '.' A_DIGIT+ [Exponent] ['j'|'J']"
        # dot_start is an optimization hack in the Token definition. It helps preventing a bloated
        # `unit` NFA.
        if tok[1] == '.':
            self.add_token([self.symbols.DOT, '.', tok[2][0], tok[3]], stream)
        else:
            self.add_token([self.symbols.NUMBER, tok[1], tok[2][0], tok[3]], stream)

    @post
    def INTRON(self, pos, tok, stream):
        if self.parenlev:   # no action inside expression
            return
        introns = tok[1]
        if len(introns) == 1:   # case 1
            self.single_intron(introns[0], tok, stream)
        else:
            self.multiple_introns(introns, tok, stream)

    def multiple_introns(self, introns, tok, stream):
        content = []
        for item in introns:
            nid = item[0][0]
            if nid == self.symbols.COMMENT:
                content.append('\n')
            elif nid == self.symbols.LINECONT:
                pass
            elif nid == self.symbols.WHITE:
                content.append(item[1])
        return self.single_intron([(self.symbols.WHITE, "WHITE"), ''.join(content)], tok, stream)


    def single_intron(self, intron, tok, stream):
        line_begin, line_end = tok[2]
        col_begin, col_end = tok[3]
        nid  = intron[0][0]
        text = intron[1]
        if nid == self.symbols.LINECONT:    # [****]'\'
            return
        if nid == self.symbols.COMMENT:
            if col_begin:                  # [****]['#'....'\n']
                self.add_token([self.symbols.NEWLINE,
                                '\n', line_begin, (col_end-1,col_end)], stream)
            else:
                return                     # ['#'....'\n']
        elif nid == self.symbols.WHITE:
            if line_begin == line_end:     # [****][    ][****]
                return
            else:                          # [****][  '\n'  ][****]
                self.add_token([self.symbols.NEWLINE,'\n', line_begin, (col_begin,col_begin+text.find('\n'))], stream)
                if self.indents:
                    if col_end>self.indents[-1]:
                        self.add_token([self.symbols.INDENT, ' '*col_end, tok[2][1], (0, tok[3][1])], stream)
                        self.indents.append(col_end)
                    elif col_end<self.indents[-1]:
                        if col_end not in self.indents+[0]:
                            raise IndentationError("(Line %d, column %d): Unindent does not match any outer indentation level."%(line_end, col_end))
                        self.dedent_to(col_end, stream)
                elif col_end:
                    self.add_token([self.symbols.INDENT, ' '*col_end, tok[2][1], (0, tok[3][1])], stream)
                    self.indents.append(col_end)

    def dedent_to(self, k, stream):
        if not stream:
            return
        line = stream[-1][2]+1
        while self.indents:
            n = self.indents[-1]
            if n>k:
                self.indents.pop()
                self.add_token([self.symbols.DEDENT, '', line, (0,0)], stream)
            elif n == k:
                break

    @post
    def LEFT(self, pos, tok, stream):
        self.parenlev+=1
        tok[2] = tok[2][0]
        self.add_token(tok, stream)

    @post
    def RIGHT(self, pos, tok, stream):
        self.parenlev-=1
        tok[2] = tok[2][0]
        self.add_token(tok, stream)


if __name__ == '__main__':

    source='''

# -*- coding: iso-8859-1 -*-
import sys as foo_sys  # comment at the end
   # comment in between
from inspect import*

# comment at begin

class Foo(object):
    def __init__(self, x):
        self.x = x

    def f(self):
        multiline_expr = {0:1,
            1:2,
            2:3} # expression end
                 # m

class Bar(object):
    if True:
        if False:
            pass
            # bla
    if True:
    #bla
    # x
        pass
z = a+\
 b + \ # bla
    c
x = -1
class A:
 class B:
  class C:
   pass
'''

    import EasyExtend.langlets.zero.langlet as zero
    import EasyExtend.eeoptions as eeoptions
    from EasyExtend.eecompiler import EECompiler
    eec = EECompiler(zero)
    tokenizer = Tokenizer(zero)
    tokstream = tokenizer.tokenize_string(source)
    eeoptions.EEShow.show_tokenstream(zero, tokstream)
    eec.parse(tokstream)

