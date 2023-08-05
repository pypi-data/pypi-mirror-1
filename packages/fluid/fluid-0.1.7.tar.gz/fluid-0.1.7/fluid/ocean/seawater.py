"""Seawater routines."""

import numpy as N

# There are 9 parts, following the UNESCO document.
# 1. Conductivity to Salinity Conversion

# R = C(S,t,p)/C(35,15,0)
# R = R_p * R_t * r_t

#	R_p(S,t,p) = C(S,t,p)/C(S,t,0)
#	R_t(S,t)   = C(S,t,0)/C(35,t,0)
#	r_t(t)     = C(35,t,0)/C(35,15,0)


def set_Sal(R,t,p):

    # For 0.2 < S < 42
    a = N.array([0.0080,-0.1692,25.3851,14.0941,-7.0261, 2.7081])

    r_t = set_r_t(t)
    R_p = set_R_p(R,p,t)
    R_t = set_R_t(R,R_p,r_t)
    
    S = _sal(R_t,t)

    return S

def _sal(R_t,t):

    DeltaS = set_DeltaS(t,R_t)
    
    S = a[0] + a[1]*R_t**(1/2) + a[2]*R_t + a[3]*R_t**(3/2) + \
        a[4]*R_t**2 + a[5]*R_t**(5/2) + DeltaS
    
    return S

########################
def _RT35(XT):
    c = N.array([0.6766097, 2.00564e-2, 1.104259e-4, \
        -6.9698e-7, 1.0031e-9])
    RT35 = (((1.0031e-9*XT+c[3])*XT+c[2])*XT + c[1])*XT + c[0]
    return RT35

def _c(XP):
    e = N.array([0 , 2.070e-5, -6.370e-10, 3.989e-15])
    c = ((e[3]*XP +e[2])*XP + e[1])*XP
    return c

def _b(XT):
    d = N.array([0 , 3.426e-2, 4.464e-4, 4.215e-1, -3.107e-3])
    b = (d[2]*XT+d[1])*XT + 1.0
    return b

def _a(XT):
    d = N.array([0 , 3.426e-2, 4.464e-4, 4.215e-1, -3.107e-3])
    a = d[4]*XT + d[3]
    return a


########################

def Sal2R(S,t,p):

    # For 0.2 < S < 42
    a = N.array([0.0080,-0.1692,25.3851,14.0941,-7.0261, 2.7081])
	
    Dt = t-15
    # Initial gess
    R_t = (S/35)**0.5

    S = _sal(R_t,t)


    for i in range(20):
        SI
        DDeltaS = set_DDeltaS(t,R_t)
        SI_new = a[1]*R_t**(1/2) + 2*a[2]*R_t + 3*a[3]*R_t**(3/2) + \
            4*a[4]*R_t**2 + 5*a[5]*R_t**(5/2) + DDeltaS
		
        R_t = R_t + (S-SI)/SI_new

        SI = _sal(R_t,t)
    
    RTT = set_r_t(t)*R_t
    AT = _a(t)
    CP = RTT*(_c(p) + _b(t))
    BT = _b(t) - RTT*AT

    R = (abs(BT*BT + 4*AT*CP))**0.5 -BT

    SAL78 = 0.5*R/AT
    
    return SAL78
	

def set_DeltaS(t,R_t):

    b = N.array([0.0005,-0.0056,-0.0066,-0.0375, 0.0636,-0.0144])
    k = 0.0162
    
    DeltaS = (t-15)/(1+k*(t-15)) \
        * ( b[0] + b[1]*R_t**(1/2) + b[2]*R_t + b[3]*R_t**(3/2) \
        + b[4]*R_t**2 + b[5]*R_t**(5/2) )
    
    return DeltaS
    
def set_DDeltaS(t,R_t):

    b = N.array([0.0005,-0.0056,-0.0066,-0.0375, 0.0636,-0.0144])
    k = 0.0162
    
    DeltaS = (t-15)/(1+k*(t-15)) \
        * (b[1] + 2*b[2]*R_t + 3*b[3]*R_t**(3/2) \
        + 4*b[4]*R_t**2 + 5*b[5]*R_t**(5/2) )
    
    return DeltaS

def set_r_t(t):
    """
    >>> set_r_t(15.)
    1.0000000
    >>> set_r_t(20.)
    1.1164927
    >>> set_r_t(5.)
    0.77956585
    """

    # Valid for -2 <= t <= 35 C

    c = N.array([0.6766097, 2.00564e-2, 1.104259e-4, \
        -6.9698e-7, 1.0031e-9])
    r_t = c[0] + c[1]*t +c[2]*t**2 + c[3]*t**3 + c[4]*t**4

    return r_t

def set_R_p(R,t,p):
    """
    >>> set_R_p(1., 15., 0.)
    1.0000
    >>> set_R_p(1.2, 20., 2000.)
    1.0169429
    >>> set_R_p(.65, 5., 1500.)
    1.0204864
    
    """

    e = N.array([0 , 2.070e-5, -6.370e-10, 3.989e-15])
    d = N.array([0 , 3.426e-2, 4.464e-4, 4.215e-1, -3.107e-3])
    R_p = 1 + ( p*(e[1] + e[2]*p + e[3]*p**2) \
        / (1 + d[1]*t + d[2]*t**2 + (d[3] + d[4]*t) *R) )

    return R_p

def set_R_t(R,R_p,r_t):
    """
    >>> set_R_t(1.,set_R_p(1., 15., 0.),set_r_t(15.))
    1.0000000
    >>> set_R_t(1.2,set_R_p(1.2, 20., 2000.),set_r_t(20.))
    1.0568875
    >>> set_R_t(0.65,set_R_p(0.65, 5., 1500.),set_r_t(5.))
    0.81705885
    """

    R_t = R/(R_p*r_t)

    return R_t

# 2. Salinity to Conductivity Conversion
# 3. Specific Volumne Anomaly and Density Anomaly of Seawater
# 4. Pressure to Depth Conversion
# 5. Freezing Point Temperature of Seawater
# 6. Specific Heat of Seawater
# 7. Potential Temperature
# 9. Sound Speed in Seawater

#def alpha(s, theta, p):
#    """Thermal expansion coefficient
#
#    This function calculates the thermal expansion
#    coefficient of sea water
#    """
#
#    alpha = _aonb(S,T,P,keyword)*_beta(S,T,P,keyword)
#
#    return alpha

def dens(s, t, p):
    """Density of sea water.
    
    This function calculates the density of sea water
    using the UNESCO 1983 (EOS 1980) polynomial.
    """
    rho0 = _dens0(s, t)
    k = _seck(s, t, p)
    p = p / 10.0

    rho = rho0 / (1 - p / k)

    return rho

def O2_saturation(s, K):
    """Saturation of O2 in sea water

    !!!! Strange values!!! Check it!
    """
    a = [-173.4292, 249.6339, 143.3483, -21.8492]
    b = [-0.033096, 0.014259, -0.0017000]

    lnC = a[0] + a[1]*(100/K) + a[2]*N.log(K/100) + a[3]*(K/100) \
        + s*( b[0] + b[1]*(K/100) + b[2]*((K/100)**2) )
    c = N.exp(lnC)

    return c
	  

def potential_temperature(s,t,p,p_final):
    """Potential Temperature
    """

    # Theta1
    del_p = p_final - p
    del_theta = del_p*_atg(s,t,p)
    theta = t + 0.5*del_theta
    q = del_theta

    # theta2
    del_theta = del_p*_atg(s,theta,p+0.5*del_p)
    theta = theta + (1 - 1/(2)**0.5)*(del_theta - q)
    q = (2-(2)**0.5)*del_theta + (-2+3/(2)**0.5)*q
   
    # theta3
    del_theta = del_p*_atg(s,theta,p+0.5*del_p) 
    theta = theta + (1 + 1/(2)**0.5)*(del_theta - q)
    q = (2 + (2)**0.5)*del_theta + (-2-3/(2)**0.5)*q

    # theta4
    del_theta = del_p*_atg(s,theta,p+del_p)
    potential_temperature = theta + (del_theta - 2*q)/6
   
    #return theta
    return potential_temperature

def _atg(s, t, p):
    """Adiabatic temperature gradient

    This function calculates the adiabatic temperature 
    gradient for seawater using the UNESCO 1983 (EOS 1980).
    """
    a = [3.5803E-5, 8.5258E-6, -6.836E-8, 6.6228E-10]
    b = [1.8932E-6, -4.2393E-8]
    c = [1.8741E-8, -6.7795E-10, 8.733E-12, -5.4481E-14]
    d = [-1.1351E-10, 2.7759E-12]
    e = [-4.6206E-13, 1.8676E-14, -2.1687E-16]

    atg = a[0] + (a[1] + (a[2] + a[3]*t)*t)*t \
        + (b[0] + b[1]*t)*(s-35) \
	+ ( (c[0] + (c[1] + (c[2] + c[3]*t)*t)*t) \
	+ (d[0] + d[1]*t)*(s-35) )*p \
	+ (  e[0] + (e[1] + e[2]*t)*t )*p**2

    return atg
			       
    
#def _aonb(s, theta, p):
def _dens0(s, t):
    """Density of sea water at atmospheric pressure.
    
    This function calculates the density of sea water at
    atmospheric pressure using the UNESCO 1983 (EOS 1980)
    polynomial.
    """
    b = [8.24493e-1, -4.0899e-3, 7.6438e-5, -8.2467e-7, 5.3875e-9]
    c = [-5.72466e-3, 1.0227e-4, -1.6546e-6]
    d = [4.8314e-4]

    rho0 = _smow(t) \
             + (b[0] + b[1]*t + b[2]*t**2 + b[3]*t**3 + b[4]*t**4)*s \
             + (c[0] + c[1]*t + c[2]*t**2)*s**(3./2) \
	     + d[0]*s**2

    return rho0

def _seck(s, t, p):
    """Secant bulk bodulus of sea water.
    
    This function calculates the Secant bulk bodulus of
    sea water using the equation of state 1980 UNESCO
    polynomial implementation.
    """
    p = p / 10.0
    
    h = [3.239908, 1.43713e-3, 1.16092e-4, -5.77905e-7]
    aw = h[0] + (h[1] + (h[2] + h[3]*t)*t)*t;

    k = [8.50935e-5, -6.12293e-6, 5.2787e-8]
    bw = k[0] + (k[1] + k[2]*t)*t

    e = [19652.21, 148.4206, -2.327105, 1.360477e-2, -5.155288e-5]
    kw = e[0] + (e[1] + (e[2] + (e[3] + e[4]*t)*t)*t)*t

    i = [2.2838e-3, -1.0981e-5, -1.6078e-6]
    j = [1.91075e-4]
    a  = aw + (i[0] + (i[1] + i[2]*t)*t + j[0]*N.sqrt(s))*s;

    m = [-9.9348e-7, 2.0816e-8, 9.1697e-10]
    b = bw + (m[0] + (m[1] + m[2]*t)*t)*s

    f = [54.6746, -0.603459, 1.09987e-2, -6.1670e-5]
    g = [7.944e-2, 1.6483e-2, -5.3009e-4]

    k0 = kw + (f[0] + (f[1] + (f[2] + f[3]*t)*t)*t \
            + (g[0] + (g[1] + g[2]*t)*t)*N.sqrt(s))*s

    k = k0 + (a + b*p)*p

    return k

def _smow(t):
    """Density of standard mean ocean water.
    
    This function calculate the density of standard
    mean ocean water (pure water) using EOS 1980.
    """
    # a[0] = -28.263737 is the value given by Milero
    a = [999.842594, 6.793952e-2, -9.095290e-3, 1.001685e-4, -1.120083e-6, 6.536332e-9]
    rho0 = a[0] + a[1]*t + a[2]*t**2 + a[3]*t**3 + a[4]*t**4 + a[5]*t**5

    return rho0

#def specific_volume_anomaly(s,t,p,zdim=1):
def specific_volume_anomaly(s,t,p):
    """

       INPUT:
         p => Pressure [db]
         zdim => Dimension of z(p) in the data array
       !!!ATENTION, zdim is not used yet. z need to be the first dimension
              of s and t
       !!!OBS, Maybe I shouldn't use zdim, but force everybody to have the
          same dimesions. The function be simple d safer
    """

    #delta = numpy.zeros(s.shape,dtype=s.dtype.type)
    #l=s.shape
    #for i in range(l[0]):
    #    print i
    #    delta[i,:] = 1./dens(s,t,p[i])-1./dens(35.,0.,p[i])

    delta = 1./dens(s,t,p)-1./dens(35.,0.,p)

    return delta

def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()

#if __name__ == '__main__':
#    s = N.array([35, 34, 33])
#    t = N.array([20, 21, 22])
#    p = N.array([0, 10, 20])
#    print dens(s, t, p)
