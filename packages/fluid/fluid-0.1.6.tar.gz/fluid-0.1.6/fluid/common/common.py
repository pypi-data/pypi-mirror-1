"""  stuffs"""

try:
    import numpy as N
except:
    try:
        import numarray as N
    except:
        import Numeric as N


def C2K(T):
    """Convert Celsius to Kelvin

    Input:
    	T =>	Temperature [C]
    Output:
    	K =>	Temperature [K]
    """
    K = T+273.15

    return K
def K2C(T):
    """Convert Kelvin to Celsius
    
    Input:
    	K =>	Temperature [K]
    Output:
    	T =>	Temperature [C]
    """

    C = T-273.15

    return C
