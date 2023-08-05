"""Distances along Earth's surface"""

try:
    import numpy as N
except:
    try:
        import numarray as N
    except:
        import Numeric as N
                            

#-----------------
# DEFINE CONSTANTS
#-----------------
DEG2RAD = (2*N.pi/360)
RAD2DEG = 1/DEG2RAD
DEG2MIN = 60
DEG2NM  = 60
NM2KM   = 1.8520    # Defined in Pond & Pickard p303.

def distance(lat,lon,lat_c=None,lon_c=None,method="simplest"):
    """Calculate distances along Earth's surface

    !!!! Uncomplete, improve it !!! !!!!!

    -> Simplest method based on Seawater routines for MatLab

    Input:
        - lat =>
        - lon =>
        - lat_c =>
        - lon_c =>
        - method =>
    Output:
        - L =>
    """

    # Why ((lon_c!=None)&(lat_c!=None)) is false ?
    if(lat_c!=None):

        #!!! values must be float or failure
        # Dinstance in degrees
        L = ((lat-lat_c)**2+(lon-lon_c)**2)**.5
        L = L*DEG2NM
        L = L*NM2KM*10**3


        return L

    return
