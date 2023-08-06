# URL:     http://www.fiber-space.de
# Author:  Kay Schluehr <easyextend@fiber-space.de>
# Date:    10 May 2006
import EasyExtend
from   EasyExtend.trail.nfaparser import TokenStream, NFAParser
from   EasyExtend.util.PyParser import PyParser
from   EasyExtend.eegrammar import EEGrammar
import EasyExtend.exotools
import marshal
import imp
import struct
import os
import eecommon
import eeoptions
import csttools
import cst
import sys

COMPILER_FLAGS = PyCF_DONT_IMPLY_DEDENT = 0x200   # ??? some undocumented compiler flag with unkown functionality but effect.

class EECompiler(eeoptions.EEShow):
    def __init__(self, langlet):
        self.options    = langlet.options
        self.langlet    = langlet
        self.nfaparser  = NFAParser(langlet)


    def expr(self, source, no_transform = False):
        cst = self.parse_expr(source)
        if no_transform:
            return cst
        self.transform(cst)
        return cst

    def suite(self, source, no_transform = False):
        cst = self.parse_suite(source)
        if no_transform:
            return cst
        self.transform(cst)
        return cst

    def transform(self, cst, **kwd):
        transformer  = self.langlet.LangletTransformer(self.langlet, **kwd)
        try:
            transformer.run(cst)
        finally:
            transformer.terminate()


    ###################   eetokenize   ####################################

    def tokenize(self, source):
        '''
        @param source: text to be tokenized.
        @return: token stream.
        '''
        tokenizer   = eecommon.load_tokenizer(self.langlet)
        return tokenizer.tokenize_string(source)

    def tokenize_string(self, source):
        tokenizer   = eecommon.load_tokenizer(self.langlet)
        return tokenizer.tokenize_string(source)

    def old_tokenize_file(self, filename):
        tokenizer   = eecommon.load_tokenizer(self.langlet)
        tokenizer.tokenize_file(filename)
        return tokenizer.tokenized()

    def tokenize_file(self, filename):
        tokenizer   = eecommon.load_tokenizer(self.langlet)
        return tokenizer.tokenize_file(filename)

    ###################   eeparse   ####################################

    def parse(self, stream, start_symbol = None):
        tokenstream = TokenStream(stream)
        tokenstream.position = 0
        cst = self.nfaparser.parse(tokenstream, start_symbol)
        return cst

    def parse_file(self, filename):
        '''
        @param filename: file to be parsed.
        '''
        stream = self.tokenize_file(filename)
        self.maybe_show_token("", filename = filename)
        parseTree = self.parse(stream, start_symbol = self.langlet.symbol.file_input)
        return parseTree

    def new_parse_file(self, filename):
        '''
        @param filename: file to be parsed.
        '''
        stream = self.tokenize_file(filename)
        self.maybe_show_token("", filename = filename)
        parseTree = self.parse(stream, start_symbol = self.langlet.symbol.file_input)
        return parseTree

    def parse_source(self, source, start_symbol):
        stream = self.tokenize(source)
        self.maybe_show_token(source)
        parseTree = self.parse(stream, start_symbol = start_symbol)
        return parseTree

    def parse_expr(self, source):
        return self.parse_source(source, self.langlet.symbol.eval_input)

    def parse_suite(self, source):
        return self.parse_source(source, self.langlet.symbol.file_input)


    ###################   eecompile   ####################################


    def try_compile(self, cst, **kwd):
        try:
            ast =  PyParser.tuple2ast(cst)
            return ast.compile(kwd.get("filename","<single>"))
        except PyParser.ParserError:
            raise
            #TBD: self.check_cst(cst, sys.exc_info()) <>
            src = self.langlet.unparse(cst)
            return compile(src,kwd.get("filename","<single>"),"exec", COMPILER_FLAGS)

    def compile_cst(self, node, **kwd):
        nid = node[0]%512
        if nid != self.langlet.symbol.file_input%512:
            node = cst.file_input(node)
        try:
            return PyParser.tuple2ast(node).compile()
        except PyParser.ParserError:
            csttools.projection(node)
            return self.try_compile(node, **kwd)

    def compile_suite(self, source, **kwd):
        '''
        @param source: source in string form
        '''
        cst = self.parse_suite(source)
        self.transform(cst, **kwd)
        csttools.projection(cst)
        return self.compile_cst(cst)

    def compile_expr(self, source, **kwd):
        '''
        @param source: source in string form
        '''
        cst = self.parse_expr(source)
        self.transform(cst, **kwd)
        csttools.projection(cst)
        return self.try_compile(cst, **kwd)


    def compile_file(self, filename, **kwd):
        '''
        Compile file according to a specific extension language into a Python module.

        @param filename: path to the destination file that will be compiled
        '''
        #print "PARSE", filename
        parseTree = self.parse_file(filename)
        mod = EEModule(parseTree, filename, self.langlet)
        kwd["options"]  = self.options
        kwd["filename"] = kwd["module"] = filename
        try:
            cst = mod.preprocess(**kwd)
            mod.code = self.try_compile(cst, **kwd)
        except SyntaxError:
            raise
        else:
            return mod.write_to_file()


class EEModule(eeoptions.EEShow):
    '''
    Class used to represent a module object of the langlet.
    '''
    def __init__(self, tree, filename, langlet):
        '''
        @param tree: parse tree of the extension language
        @param filename: filename of the compiled module
        @param langlet: Python module object containing relevant ext-language definitions.
        '''
        self.tree = tree
        self.filename = filename
        self.code = None
        self.langlet = langlet

    mode = "exec"

    def write_to_file(self):
        try:
            ext = self.langlet.compiled_ext
        except AttributeError:
            ext = ".pyc"
        idx = self.filename.rfind(".")
        f = open(self.filename[:idx] + ext, "wb")
        self.dump(f)
        f.close()
        return f

    def preprocess(self, **kwd):
        self.langlet.exospace = EasyExtend.exotools.Exospace(id(self.tree))
        self.options = kwd["options"]
        transformer = self.langlet.LangletTransformer(self.langlet, **kwd)
        self.maybe_show_cst_before(self.tree)
        transformer.run(self.tree)
        transformer.general_transform(self.tree)
        self.maybe_show_cst_after(self.tree)
        transformer.terminate()
        csttools.projection(self.tree)
        self.maybe_show_python(self.tree)
        self.maybe_grammar_check(self.tree)
        #print self.langlet.unparse(self.tree)
        if self.options.get("parse_only"):
            print "File parsed -> exit"
            sys.exit(0)
        return self.tree

    def compile(self, **kwd):
        '''
        Create Python code object from transformed extension language parse tree.
        '''
        tree = self.preprocess(**kwd)
        try:
            ast = PyParser.tuple2ast(tree)      # usual compilation process
            self.code = ast.compile(self.filename)
        except PyParser.ParserError:
            source = self.langlet.unparse(tree)   #  parser module is buggy...
            self.code = compile(source, self.filename, "exec")

    def dump(self, f):
        '''
        Dump Python code-object into a binary file
        '''
        f.write(self.getPycHeader())
        marshal.dump(self.code, f)

    MAGIC = imp.get_magic()

    def getPycHeader(self):
        # compile.c uses marshal to write a long directly, with
        # calling the interface that would also generate a 1-byte code
        # to indicate the type of the value.  simplest way to get the
        # same effect is to call marshal and then skip the code.
        mtime = os.path.getmtime(self.filename)
        mtime = struct.pack('<i', mtime)
        return self.MAGIC + mtime


def dump_code(filename, code):
    # experimental...
    f = open(filename, "wb")
    mtime = os.path.getmtime(filename)
    mtime = struct.pack('<i', mtime)
    MAGIC = imp.get_magic()
    f.write(MAGIC + mtime)
    marshal.dump(code, f)
    f.close()

