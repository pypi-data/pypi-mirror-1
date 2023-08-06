from conf import*                  # langlet specific modules ( symbol, token ) and objects ( prompt, pprint, unparse ...)
from EasyExtend.csttools import*   # tools used to manipulate CSTs

class LangletImporter(eeimporter.Importer):
    '''
    Defines langlet specific import behaviour.
    '''

class LangletTokenizer(eetokenizer.Tokenizer):
    '''
    Defines langlet specific token stream processor.
    '''

class LangletTransformer(Transformer):
    '''
    Defines langlet specific CST transformations.
    '''

__publish__ = []


