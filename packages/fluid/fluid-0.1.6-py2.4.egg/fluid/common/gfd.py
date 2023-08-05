"""Geophysical Fluid Dynamics related stuffs"""

try:
    import numpy as N
except:
    try:
        import numarray as N
    except:
        import Numeric as N


#How is the best way to define it? A function defining global variables?
# Not Earth's day, but sideral day!!
_Omega=2*N.pi/((1+1/365)*24*60*60)
_EarthRadius=6378137

def f_parameter(lat,Omega=_Omega):
    """f Coriolis parameter
    
    Input:
    	lat	=> Latitude [Degrees]
	Omega	=> Angular velocity () [Radians/s]
    Output:
    	f	=> Coriolis parameter []

    >>>f_parameter(0)
    0
    >>>f_parameter(30)
    1
    >>>f_parameter(45,1)
    1
    """
    theta = lat/180.*N.pi

    f = 2*Omega*N.sin(theta)

    return f

def beta(lat,Omega=_Omega,R=_EarthRadius):
    """Beta parameter

    """
    theta = lat/180.*N.pi

    B = 2 * Omega*N.cos(theta)/R

    return B


def gravity(lat):
    """Gravity in function of latitude using the 1980 IUGG formula
    Transcripted from COARE-3.0 routines (Fairall et. al.)

    Bulletin Geodesique, Vol 62, No 3, 1988 (Geodesist's Handbook)
        p 356, 1980 Gravity Formula (IUGG, H. Moritz)
        units are in m/sec^2 and have a relative precision of 1 part
        in 10^10 (0.1 microGal)
        code by M. Zumberge.

	Check SEAWATER routines use:
	Unesco 1983. Algorithms for computation of fundamental properties of 
	    seawater, 1983. _Unesco Tech. Pap. in Mar. Sci._, No. 44, 53 pp.
	
	A.E. Gill 1982. p.597
	    "Atmosphere-Ocean Dynamics"
	    Academic Press: New York.  ISBN: 0-12-283522-0
	

        check values are:
    
        g = 9.780326772 at latitude  0.0
        g = 9.806199203 at latitude 45.0
        g = 9.832186368 at latitude 90.0
    """

    gamma = 9.7803267715
    c1 = 0.0052790414
    c2 = 0.0000232718
    c3 = 0.0000001262
    c4 = 0.0000000007
    phi = lat * N.pi / 180.0
    g = gamma * (1.0 + c1 * ((N.sin(phi))**2) + c2 * ((N.sin(phi))**4) + c3 * ((N.sin(phi))**6) + c4 * ((N.sin(phi))**8))

    return g

def find_detadx(U,f,g,balance,R=None):
    """Estimate del eta/ del x  for different force balance equilibrae

    Input:
        - U => Velocity magnitude
        - balance:
            - geostrophic =>
            - gradient =>
    """

    if(balance=='geostrophic'):
        detadx = (f*U)/g
    elif(balance=='gradient'):
        detadx = (U**2/R+f*U)/g
    elif(balance=='max_gradient'):
        detadx = (R*f**2)/(4*g)
    else:
        return

    return detadx

#def dynamic_height(delta,p,p1=None,p2=0):
# Think about if the pressure should be previously selected or
#   keep the option to choose between which levels.
def dynamic_height(delta,p):
    """Dynamic Height in the ocean

       INPUT: delta => Specific Volume Anomaly
       !!! ATENTION !!!! The first dimension must be z
       !!! ATENTION !!!! It is uncomplete
    """
    if p1 is None:
        p1=max(p)

    Pressure should be in Pascal
    p = p*1e4 

    dp = numpy.ones(p.shape,dtype=p.dtype.type)
    dp[1:-1,:] = p[2:,:]-p[0:-2,:]
    dp[0,:] = p[1]-p[0]
    dp[-1] = p[-1]-p[-2]
    dp = dp*0.5

    Theta = numpy.ones(p.shape,dtype=p.dtype.type)
    Theta = delta*dp

    #from fluid.common.gfd import gravity
    #g=gravity(numpy.mean(lat[lat_index[0]:lat_index[-1]]))

    DH = numpy.cumsum(Theta)/g

    return DH

def _test():
    import doctest
    doctest.testmod()
