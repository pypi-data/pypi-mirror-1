def more_recent(file_A, file_B):
    import os
    return os.stat(file_A)[-2]>=os.stat(file_B)[-2]


def psyco_optimized(f):
    '''
    Decorator for Psyco optimized functions.
    '''
    try:
        import psyco
        return psyco.proxy(f)
    except ImportError:
        return f



