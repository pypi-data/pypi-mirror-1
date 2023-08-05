# vim: tabstop=4 shiftwidth=4 expandtab

# epsilon is the ration of the molecular weight of water vapor to dry air. 
#   Define the value with more precision.
_Rv = 461.          # [J/(K kg)]
_Rd = 287.04        # [J/(K kg)]
_epsilon = 0.62197    # molecular weight ratio (water/air)
_gas_const_R = 287.04 # gas constant for dry air [J/kg/K]
_cp = 1004.7

import numpy as N
 
#from future import division

def air_density(p,Kv,gas_const_R=_gas_const_R):
    """Air density

    Estimated from ?? relation, considering an ideal gas

    Input:
        p =>    Atmospheric pressure [Pascal]
        Kv =>   Virtual temperature [Kelvin]
        _gas_const_R => Gas constant for dry air (287.04) [?]
    Output:
        air_rho => Density of the air [kg/m**3]

    >>> air_density(100800,300)
    12.109329950409411
    >>> air_density(101300,303)
    11.028515189520624
    >>> air_density(101000,298.4)
    23.457822370865848
    """

    air_rho=p/(gas_const_R*Kv)

    return air_rho

def air_viscosity(T_a):
    """Kinematic viscosity of dry air
        Andreas (1989), CRREL Report 89-11
	
    Input:
        T_a => Air temperature [C]
    Output:
        viscair => Air viscosity [m^2/s]

    >>> air_viscosity(N.array([0.1, 5., 15.]))
    array([  1.32686758e-05,   1.36964784e-05,   1.45857532e-05])
    >>> air_viscosity(N.array([22.8, 28.9, 31.4]))
    array([  1.52942886e-05,   1.58573695e-05,   1.60903922e-05])
    """

    viscair = 1.326e-5*(1 + 6.542e-3*T_a + 8.301e-6*T_a**2 - 4.84e-9*T_a**3)

    return viscair
	  
def equivalent_potential_temperature(theta,L,w_s,c_p,T):
    """Equivalent Potential Temperature

    Input:
        theta => Potential temperature [?]
        L => [?]
        w_s => [?]
        c_p => [?]
        T => [?]
    Output:
        theta_e => Equivalent Potential Temperature [?]
    """

    theta_e = theta*N.exp(L*w_s/(c_p*T))

    return theta_e

#def w2e
def vapor_pressure(w,p,epsilon=_epsilon):
    """Vapor Pressure

    Input:
        w => Mixing Ratio [?]
        p => Pressure [?]
        epsilon =>
    Output:
        e => Vapor Pressure [?]

    >>> vapor_pressure(5.5e-3,1026.8*100)   # From Wallace, p.71
    900.02709292874567
    """

    e = w*p/(w+epsilon)

    return e

def saturation_vapor_pressure(T_a,p=None):
    """Saturation Vapor Pressure
    
    e_s [hPa] = e_s(T_a[C])
    
    Estimate the saturation vapor pressure for a given temperature
    
    Atention!!! There are different formulas. Maybe include them in future!
    Look at "polynomial developed by Herman Wobus"

    Input:
        T_a => Air temperature [C]
    Output:
        e_s => Saturation vapor pressure [Pa]

    Need to validate!

    >>> saturation_vapor_pressure(10.)
    1227.1695993898763
    >>> saturation_vapor_pressure(15.5)
    1759.6941250149196
    
    
    """

    if ( N.sometrue((T_a < -30) | (T_a > 50)) ): return
    
    e_s = 6.112*N.exp(17.67*T_a/(T_a+243.5))
    #e_s = 6.1121*(1.0007+3.46e-6*Pa)*N.exp((17.502*T_a)./(240.97+T_a)) From Air Sea!
    
    #g=N.zeros(8,N.Float)
    #g[0] = -2.9912729e3
    #g[1] = -6.0170128e3
    #g[2] = 1.887643854e1
    #g[3] = -2.8354721e-2
    #g[4] = 1.7838301e-5
    #g[5] = -8.4150417e-10
    #g[6] = 4.4412543e-13
    #g[7] = 2.858487e0
    #es=N.zeros(N.size(K_a),N.Float)
    #for i in range(7):
    #    es = es + g[i]*K_a**(i-2)
    #es = N.exp(es + g[7]*N.log(K_a))
    

    e_s = e_s*100 # mb -> Pa
	    
    return e_s

#def e2w
def mixing_ratio(e,p,epsilon=_epsilon):
    """Mixing Ratio

    w[kg/kg] = MixingRatio( e[Pa], p[Pa] )

    Estimate the mixing ratio based on mixture pressure and vapor pressure

    Input:
        e => Vapor pressure [?Pa?]
        p => Atmospheric pressure [?Pa?]
    Output:
        w => Mixing ratio [?kg of water /kg of air?]
    """

    w = epsilon * e /(p-e)

    return w

def saturation_mixing_ratio(Ta,p,epsilon=_epsilon):
    """Saturation Mixing Ratio (Alias function)

    Input:
        Ta => Air Temperature [?]
        p => Pressure [?]
        epsilon => [?]
    Output:
        ws => Saturation mixing ratio [?]

    Obs.: Could be estimated from mixing_ratio function too, 
        but using e_s instead of e.
        w_s = w(e_s)
    """

    # First determine the Saturation Vapor Pressure.
    es = saturation_vapor_pressure(Ta)
    # Estimate mixing ratio using es instead of e.
    ws = mixing_ratio(es,p,epsilon)

    return ws

def RH2w(RH,ws):
    """Relative Humidity to Mixing Ratio

    Input:
        RH => Relative humidity []
        ws => Saturation Mixing Ratio [?]
    Output:
        w => Mixing Ratio
    """

    w = RH*ws

    return w
    
def RH2e(RH,ws,p,epsilon=_epsilon):
    """
    
    Input:
        => []
    Output:
        => []
    """

    w = RH2w(RH,ws)
    e = vapor_pressure(w,p,epsilon)

    return e

def q2w(q):
    """Specific humidity to Mixing ratio

    Input:
        => []
    Output:
        => []
    """

    w = q/(1-q)

    return w
    
#def w2q
def specific_humidity(w):
    """Specific humidity

    Input:
        w => Mixing ratio []
    Output:
        q => Specific humidity []
    """

    q = w/(1+w)

    return q

#Redundant
#def saturation_specific_humidity(ws):
#    """
#    """
#
#    q = ws/(1+ws)

def virtual_temperature(T,e,p,epsilon=_epsilon):
    """Virtual Temperature

    Tv[] = VirtualTemperature( T[], e[], p[], epsilon)

    Input:
        T =>    [?]
        e =>    Vapor pressure [?]
        p =>    Atmospheric pressure [?]
        epsilon => [?]
    Output:
        Tv =>   Virtual temperature [?]
    """

    Tv = T/( 1-(e/p)*(1-epsilon) )

    return Tv

def potential_temperature(T,p,R,p0=1e5,cp=_cp):
    """Potential temperature

    Input:
        T =>    [?]
        p =>    [?]
        R =>    [J/deg/Kg]
        p0 =>   (10^5) [?]
        c_p =>  [J/deg/Kg]
    Output:
        theta =>    Potential temperature []
    """

    theta = T*(p0/p)**(R/c_p)

    return theta
#def Gama

#def Gama_s

def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test() 
                
