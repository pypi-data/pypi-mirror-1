# vim: tabstop=4 shiftwidth=4 expandtab

try:
    import numpy as N
except:
    try:
        import numarray as N
    except:
        import Numeric as N


#Apenas um exemplo de como iniciar um código.
def soma(a, b):
    """Retorna a soma de dois n<FA>meros a e b.

    >>> soma(1,1)
    2
    >>> soma(1.0,2.0)
    3.0
    """
    pass
def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()

