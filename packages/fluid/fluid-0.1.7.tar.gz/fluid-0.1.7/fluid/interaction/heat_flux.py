# vim: tabstop=4 shiftwidth=4 expandtab

#!!! Atention, include the albedo estimative method by Payne72!!!

import numpy as N

_emiss_lw = 0.985
_sigma = 5.6697e-8  #[J/(s m**2 K**4)] Stefan-Boltzman constant


# ==================================================================
#Maybe this class isn't the best place for it.

def noon_solar_altitude(DOY,Lat):
    """Noon solar altitude
    Liou, 1980 + Liou, 1992
    Copied from Air-Sea package

    Input: 
        - DOY => Day of year [1-366],
        - Lat => Latitude [Degree],
    Output:
        - NSA => Noon Solar Altitude [Rad]

    >>> noon_solar_altitude(100,15)
    1.4426105288157709
    >>> noon_solar_altitude(250,25)                
    1.2456580990881319
    >>> noon_solar_altitude(300,2)                
    1.3173402650598927
    """

    k = N.pi/180.
    t = 2*N.pi*DOY/365.
    d = .397+3.630*N.sin(t) - 22.98*N.cos(t) \
        + .040*N.sin(2*t) - .388*N.cos(2*t) \
        + .075*N.sin(3*t) - .160*N.cos(3*t)
    dl = k*d
    ll = k*Lat
    z = N.sin(ll)*N.sin(dl)+N.cos(ll)*N.cos(dl)

    NSA  = N.arcsin(z)

    return NSA

# ==================================================================

def short_wave_radiation(Qswi,albedo=0.055):
    """Estimate short wave hear flux

    """

    Qsw=(1-albedo)*Qswi

    return Qsw

def short_wave_clear_sky(Lat,DOY):
    """Short wave for clear sky
    Reed 1977, J. Phys. Oce.
    Q_cs defined by Seckel and Beaudry 1973, Trans. Am. Geophys. Union

    Estimative of daily mean incident short wave for clear sky.
    It's knowed as Smithsonian formulae
    Input: 
        - DOY => Day of year [1-366],
        - Lat => Latitude [Degree],
    Output:
        - Qcs => Incident short wave for a clear sky [W.m**(-2)]

    Need to check what to do with 40 deg of lat!!!!
    Validated against Air Sea clskswr() function.

    >>> short_wave_clear_sky(N.array([5.,0.,50.,15.,40.]),N.array([1.,300.,180.,200.,78.]))
    array([ 285.71838284,  321.01531555,  356.71914368,  332.60339837,
            231.36758401])
    >>> short_wave_clear_sky(N.array([15.,-5.,8.,4.]),N.array([257.,360.,155.,89.]))
    array([ 318.97973028,  323.73555101,  315.20311188,  328.55555574])
    """

    # !!!Must include a check if Lat and DOY have some dimensions

    # Convert Latitude to an angle in radians
    LatTheta = Lat/180.*N.pi

    # Convert Day of year to angle in degree
    # !! Improve it, alternate between 365 and 366!
    phi = (DOY-21)*360./365.
    # Convert Phi to radians
    phi = phi/180.*N.pi

    #Qcs = N.zeros(N.shape(Lat))
    Qcs = Lat*0

    #for L,LT,P,n in zip(Lat,LatTheta,phi,range(len(Qcs))):
    for L,LT,P,n in zip(Lat,LatTheta,phi,range(len(Lat))):

        if (L > -20 and L <= 40):
            A0=-15.82+326.87*N.cos(LT)
            A1=9.63+192.44*N.cos(LT+N.pi/2)
            B1=-3.27+108.70*N.sin(LT)
            A2=-0.64+7.80*N.sin(2*(LT-N.pi/4))
            B2=-0.50+14.42*N.cos(2*(LT-N.pi/36))
             
            Qcs[n] = A0 + A1*N.cos(P) + B1*N.sin(P) \
                + A2*N.cos(2*P) + B2*N.sin(2*P)
        elif (L > 40 and L < 60):
            A0=342.61-1.97*L-0.018*L**2
            A1=52.08-5.86*L+0.043*L**2
            B1=-4.80+2.46*L-0.017*L**2
            A2=1.08-0.47*L+0.011*L**2
            B2=-38.79+2.43*L-0.034*L**2
              
            Qcs[n] = A0 + A1*N.cos(P) + B1*N.sin(P) \
                + A2*N.cos(2*P) + B2*N.sin(2*P)
        else:
            print "Function short_wave_clear_sky incomplete!!! Lat out of range."
            return
    return Qcs

def cloud_cover(Lat,FracQ,NSA):
    """Cloud cover
    Reed, 1977

    Input: 
        - Lat => Latitude [Degree],
        - FracQ => Qswi/Qcs [W m**(-2)], ratio between Incident short wave 
            heat flux and Clear sky short wave
        - NSA => Noon Solar Altitude [Rad]
    Output:
        - C => Cloud Cover [0 - 1] !! Should be 0.3 - 1.0
    """

    # NSA here is used in degree
    NSA = NSA/N.pi*180

    # Qswi shouldn't be greater than Qcs. Therefore, if measured 
    #  Qswi is greater than Qcs, force Qswi to be equal to Qcs
    FracQ = FracQ*N.less_equal(FracQ,1)+N.greater(FracQ,1)

    C = 1.61*(1-FracQ+0.0019*NSA)

    # According to Reed77, the basic relation is limited for values of
    #   C between 0.3 and 1.0. So:
    #       - Is here the best place to limit this range?
    #       - Is this the best treatment when out of range?
    # Cloudness factor lesser than 0.3 is considered equal to 0 and
    # Cloudness factor greater than 1.0 is considered equal to 1.0
    C = C*N.greater_equal(C,0.3)*N.less_equal(C,1) \
        + N.greater(C,1)

    return C

def long_wave_radiation(Ts,Ta,ea,C,Lat,method="Clark"):
    """Long wave heat flux
    
    Different results of Air Sea routines!!! But close, difference lesser than 5%

    
    Estimative of Long wave heat flux emited from ocean surface

    Parameters:
        - emiss_lw =>     % long-wave emissivity of ocean from Dickey et al^M
                              % (1994), J. Atmos. Oceanic Tech., 11, 1057-1076.^M
                              
        - sigma => Stefan-Boltzmann constant [W/m^2/K^4]^
    Input:
        - Ts => Surface temperature [Kelvin]
            Check if is 1m temperature or surface temperatue
        - Ta => Air temperature [Kelvin]
            Check if have some elevation dependence
        - ea => [Pa]
        - C => Cloudness Cover factor [no unit]
            Check true name and reference
        - method (Clark) => Parametrization method # Or Clarke?!?!?!

    Validated against Air Sea. Only for CLark method.
    >>> long_wave_radiation(300.4, 300.23, 3042.63, 0.33681998,15., method="Clark")
    array(-49.429443088351128)
    >>> long_wave_radiation(298.76, 298.37, 2635.41, 0.52657767, -5., method="Clark")
    array(-52.922747390415843)
    >>> long_wave_radiation(301.55, 301.1, 3021.67, 0.80383036, 8., method="Clark")
    array(-36.690214825537389)
    >>> long_wave_radiation(300.29, 299.66, 2961.96, 0.78402179, 4., method="Clark")
    array(-39.90190354401949)
    
    """

    # Pa to mb
    ea = ea/100
        
    if(method=="Bunker"):
        # Bunker solution for Atlantic
        a=N.zeros(N.shape(Lat),N.Float)

        # (N.greater_equal(a,65) & N.less(a,75))
        a = a + (N.greater_equal(abs(Lat),75) & N.less(abs(Lat),85))*.84
        a = a + (N.greater_equal(abs(Lat),65) & N.less(abs(Lat),75))*.80
        a = a + (N.greater_equal(abs(Lat),55) & N.less(abs(Lat),65))*.76
        a = a + (N.greater_equal(abs(Lat),45) & N.less(abs(Lat),55))*.72
        a = a + (N.greater_equal(abs(Lat),35) & N.less(abs(Lat),45))*.68
        a = a + (N.greater_equal(abs(Lat),25) & N.less(abs(Lat),35))*.63
        a = a + (N.greater_equal(abs(Lat),15) & N.less(abs(Lat),25))*.59
        a = a + (N.greater_equal(abs(Lat),7.5) & N.less(abs(Lat),15))*.52
        a = a + (N.less(abs(Lat),7.5))*.5
        
#        for i in range(len(Lat)):
#            if (abs(Lat[i]) > 75):     a[i]=0.84
#            elif (abs(Lat[i]) > 65):   a[i]=0.80
#            elif (abs(Lat[i]) > 55):   a[i]=0.76
#            elif (abs(Lat[i]) > 45):   a[i]=0.72
#            elif (abs(Lat[i]) > 35):   a[i]=0.68
#            elif (abs(Lat[i]) > 25):   a[i]=0.63
#            elif (abs(Lat[i]) > 15):   a[i]=0.59
#            elif (abs(Lat[i]) > 7):    a[i]=0.52
#            else:                   a[i]=0.50

        CF = 1-a*C
        Qlw=0.022*(_emiss_lw*_sigma*Ta**4*(11.7-0.23*ea)*CF) + \
          4*_emiss_lw*_sigma*Ta**3*(Ts-Ta)
    ## !!!!! CHECK this formulae
    elif(method=="Clark"):

        a=N.zeros(N.shape(Lat),N.Float)

        # (N.greater_equal(a,65) & N.less(a,75))
        a = a + (N.greater_equal(abs(Lat),45) & N.less(abs(Lat),55))*.73
        a = a + (N.greater_equal(abs(Lat),35) & N.less(abs(Lat),45))*.69
        a = a + (N.greater_equal(abs(Lat),25) & N.less(abs(Lat),35))*.64
        a = a + (N.greater_equal(abs(Lat),15) & N.less(abs(Lat),25))*.60
        a = a + (N.greater_equal(abs(Lat),7.5) & N.less(abs(Lat),15))*.56
        a = a + (N.greater_equal(abs(Lat),2.5) & N.less(abs(Lat),7.5))*.53
        a = a + (N.less(abs(Lat),2.5))*.51

#        for i in range(len(Lat)):
    
        CF = 1-a*C**2
        # Check this "-"signal!!
        Qlw = - _emiss_lw*_sigma*Ts**4*(0.39-0.05*ea**0.5)*CF \
          - 4*_emiss_lw*_sigma*Ts**3*(Ts-Ta)
    else: return

    return Qlw

def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()        
