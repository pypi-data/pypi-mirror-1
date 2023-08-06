'''
The class BaseLexerToken encapsulates settings that can be used and overwritten
by custom Lexers. In a sense it is about those token used while tokenization using token Grammars.
'''

import string
import copy

class any_object(object):
    pass

BaseLexerToken          = any_object()
BaseLexerToken.litset   = any_object()
BaseLexerToken.abstract = any_object()
BaseLexerToken.use      = any_object()

# abstract token ( for use in Token and Token.ext )
BaseLexerToken.abstract.T_ENDMARKER   = 1
BaseLexerToken.abstract.T_INDENT      = 2
BaseLexerToken.abstract.T_DEDENT      = 3
BaseLexerToken.abstract.T_OP          = 4
BaseLexerToken.abstract.T_ERRORTOKEN  = 5
BaseLexerToken.abstract.T_NT          = 6
BaseLexerToken.abstract.T_N_TOKENS    = 7
BaseLexerToken.abstract.T_NEWLINE     = 8
BaseLexerToken.abstract.T_NT_OFFSET   = 9
BaseLexerToken.abstract.A_LINE_END    = 10
BaseLexerToken.abstract.A_CHAR        = 11
BaseLexerToken.abstract.A_WHITE       = 12
BaseLexerToken.abstract.A_HEX_DIGIT   = 13
BaseLexerToken.abstract.A_OCT_DIGIT   = 14
BaseLexerToken.abstract.A_DIGIT       = 15
BaseLexerToken.abstract.A_BACKSLASH   = 16
BaseLexerToken.abstract.ANY           = 17
BaseLexerToken.abstract.A_NON_NULL_DIGIT = 18

# litsets
BaseLexerToken.litset.LS_A_LINE_END       = set(map(chr,[10, 13]))  # '\n\r'
BaseLexerToken.litset.LS_A_CHAR           = set(string.ascii_letters+"_")
BaseLexerToken.litset.LS_A_WHITE          = set(map(chr,[9, 10, 11, 12, 13, 32]))  # '\t\n\x0b\x0c\r '
BaseLexerToken.litset.LS_A_HEX_DIGIT      = set(string.hexdigits)
BaseLexerToken.litset.LS_A_OCT_DIGIT      = set(string.octdigits)
BaseLexerToken.litset.LS_A_NON_NULL_DIGIT = set('123456789')
BaseLexerToken.litset.LS_A_DIGIT          = set(string.digits)
BaseLexerToken.litset.LS_A_BACKSLASH      = set(['\\'])
BaseLexerToken.litset.LS_ANY              = set()

# options
BaseLexerToken.use.B_SigWhite = True

def NewLexerToken(offset):
    LxToken = copy.copy(BaseLexerToken)
    LxToken.abstract = copy.copy(BaseLexerToken.abstract)
    LxToken.litset = copy.copy(BaseLexerToken.litset)
    LxToken.use = copy.copy(BaseLexerToken.use)
    LxToken.tok_name = {}
    for name, value in LxToken.abstract.__dict__.items():
        setattr(LxToken.abstract, name, value+offset)
        if type(value) is type(0):
            LxToken.tok_name[value+offset] = name

    LxToken.token_map = LxToken.abstract.__dict__  # for compliency with parse_token files
    return LxToken

if __name__ == '__main__':
    assert BaseLexerToken.abstract.A_CHAR == 11
    LexerToken = NewLexerToken(100)
    assert LexerToken.abstract.A_CHAR == 111
    # o.k. nothing changed
    assert BaseLexerToken.abstract.A_CHAR == 11



