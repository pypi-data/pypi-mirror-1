# vim: tabstop=4 shiftwidth=4 expandtab

try:
    import numpy as N
except:
    try:
        import numarray as N
    except:
        import Numeric as N


#from fluid.atmosphere.atmospheric_constants import *
import fluid.atmosphere.atmospheric_constants

_cp = fluid.atmosphere.atmospheric_constants.cp
_epsilon = fluid.atmosphere.atmospheric_constants.epsilon
#_kappa = 0.41
_kappa = 0.4
_alpha_c = 0.011
_R_roughness = 0.11
_min_gustiness = 0.5

_k_Boltzmann = 1.38e-23   # [J/K] Boltzman Constant
_h_Planck = 6.63e-34  # [Js]

_c = 299792458    # [m/s] Speed of light


def wind_height(u_str, z, z0):
    """Estimate wind at different height based on log profile
    
    Input:
        =>
    Output:
        =>
    """

    sqrtC_D = _kappa / ( N.log(z/z0) )
    u_z = u_str/sqrtC_D

    return u_z

def find_u_star(u, air_nu, z=None, g=9.8, alpha_c=_alpha_c, R_roughness=0.11,tol=_R_roughness):
    """Estimate u_star by iteration method

    Now only work for a neutral stability layer
    
    Input:
        =>
    Output:
        =>

    Differences on the third precision.
    >>> find_u_star(N.array([10.0]), N.array([1.5773800e-05]), N.array([4.0]))
    array([ 0.41099549])
    """

    u_stro = N.zeros(N.shape(u))
    u_str = .036*u

    go=1
    while(go):
        #print u_str
        u_stro=u_str
        #z0 = roughness_length(u_str=u_str, g=g, air_nu=air_nu, alpha_c=alpha_c, R_roughness=R_roughness)
        z0 = set_z0(u_stro, air_nu, g=g, alpha_c=alpha_c, R_roughness=R_roughness)
        C_D = drag_coefficient(z0=z0,z=z)
        u_str = u*C_D**.5
        Delta = N.abs(u_str-u_stro)

        go = (Delta[N.argmax(Delta)]>tol)

    return u_str

def find_transfer_coefficients(T_air,Tv,T_sea,q,q_sea,u,z_u,z_T,z_q,air_nu,u_star,tol=0.001):
    """Find by iteration method the transfer coeficients

    Estimate Drag, thermal and humidity transfer coeficients best
      fitted to the measured data
    
    Input:
        =>
    Output:
        =>
    """
    Ka = T_air+273.15
    Kv = Tv+273.15

    #DT = T_air - T_sea
    DT = T_air + 0.0098*z_T - T_sea
    Dq = q - q_sea

    S = (u**2 + _min_gustiness**2)**0.5

    z0t=7.5E-5
    z0q=z0t

    C_T = transfer_coefficient(z_T,z0t)
    C_q = transfer_coefficient(z_q,z0q)

    print "Epa!!!"
    print "Coefficients", C_T, C_q

    T_star = C_T*DT
    q_star = C_q*Dq


    Rr_u=0.
    Rr_T=0.
    Rr_q=0.

    go = N.greater( 1,0)

    while N.sometrue(go):
        Rr_u_old = Rr_u
        Rr_T_old = Rr_T
        Rr_q_old = Rr_q
        #print "T_star,q_star",T_star,q_star
        #print u_star
        
        #L = monin_obukhov_length(u_star,T_air,T_star,Tv,q,q_star)
        Tv_star=set_Tv_str(T_star,q,Ka,q_star)
        L = monin_obukhov_length(u_star,Tv_star,Kv)

        print "L: ",L

        zeta_u, zeta_T, zeta_q = stability_parameter(z_u,z_T,z_q,L)
        print  "zeta_u",zeta_u, zeta_T, zeta_q
        
        z0 = set_z0(u_star, air_nu)
        print "z0",z0
        
        #Psi_u = set_psi(zeta_u,who="u")
        Psi_u = set_psi_u(zeta_u)

        CD = drag_coefficient(z_u,z0,Psi_u)

        u_star = S*CD**0.5

        Rr_u = roughness_Reynolds(z0, u_star, air_nu)
        #print "Rr_u",Rr_u
        
        Rr_T, Rr_q = lkb(Rr_u)
        #print "Rr_T, Rr_q", Rr_T, Rr_q
        
        z0T = roughness_length(Rr_T, u_star, air_nu)
        z0q = roughness_length(Rr_q, u_star, air_nu)
        #print "z0T, z0q", z0T, z0q
        
        zeta_u, zeta_T, zeta_q = stability_parameter(z_u,z_T,z_q,L)
        #print "zeta_u, zeta_T, zeta_q", zeta_u, zeta_T, zeta_q
        
        #Psi_T = set_psi(zeta_T,who="T")
        Psi_T = set_psi_tq(zeta_T)
        #Psi_q = set_psi(zeta_u,who="q")
        Psi_q = set_psi_tq(zeta_q)
        #print "Psi_u,Psi_T,Psi_q", Psi_u, Psi_T, Psi_q
        
        C_T = transfer_coefficient(z_T,z0T,Psi_T)
        C_q = transfer_coefficient(z_q,z0q,Psi_q)
        #print "C_T, C_q",C_T, C_q
        print "z_T:",z_T,", z_q:",z_q
        print "z0T:",z0T,", z0q:",z0q
        print "Coefficients", C_T, C_q

        T_star = C_T*DT
        q_star = C_q*Dq
        #print "T_star,q_star",T_star,q_star
        
        wg = wind_gustiness(u_star,L,zeta_u)
        S = (u**2 + wg**2)**0.5

        #z0 = roughness_length_tq(u_star, air_nu)
        #print "z0",z0

        #go = N.greater( N.abs(Rr_u-Rr_u_old), tol)
        #print go
        go = N.greater( N.abs((Rr_u-Rr_u_old)/Rr_u), tol)
        #print ( N.abs((Rr_u-Rr_u_old)/Rr_u), tol)
        #print "Rr_u,Rr_T,Rr_q",Rr_u-Rr_u_old,Rr_T-Rr_T_old,Rr_q-Rr_q_old

    return u_star, T_star, q_star 

def richardson_number(Ta,DT,Tv,Dq,u,z_u,g=9.81,epsilon=_epsilon):
    """Richardson number

    Comments from Air-Sea
    #% compute bulk Richardson number (as a diagnostic) - the "T"
    #% is probably not quite right - assumes T \ approx. Ts (good enough though)
    
    
    Input:
        =>
    Output:
        =>
    """

    o61=1/epsilon-1

    RI=g*z_u*((DT) + o61*Ta*(Dq))/(Tv*u**2)

    return RI

def wind_stress(air_rho,CD,u):
    """Wind stress

    From Air-Sea package
    #% to compute mean stress, we don't want to include the effects
    #% of gustiness which average out (in a vector sense).
    #  ur     = wind speed [m/s] measured at height z_u [m]
    
    Input:
        =>
    Output:
        =>
    """

    #ur=u
    #stress=rho.*CD.*S.*ur;
    #stress = air_rho*CD*u*ur
    stress = air_rho*CD*u**2

    return stress

def wind_gustiness(u_star,L,zeta_u,kappa=_kappa,CVB_depth=600.,beta_conv=1.25,min_gustiness = _min_gustiness):
    """

    From Air Sea
        % the following are useful in hfbulktc.m
        %     (and are the default values used in Fairall et al, 1996)
        CVB_depth     = 600; % depth of convective boundary layer in atmosphere [m]
        min_gustiness = 0.5; % min. "gustiness" (i.e., unresolved fluctuations) [m/s]
        % should keep this strictly >0, otherwise bad stuff
        % might happen (divide by zero errors)
        beta_conv     = 1.25;% scaling constant for gustiness


        % estimate new gustiness^M
            bs=g*(T_star.*(1 + o61*Q) + o61*T.*Q_star)./Tv; ^M
            L=(U_star.^2)./(kappa*bs);^M
            
            Ws=U_star.*(-CVB_depth./(kappa*L)).^onethird;^M
            wg=min_gustiness*ones(M,1);^M
            j=find(zetu<0);                 % convection in unstable conditions only^M
            wg(j)=max(min_gustiness,beta_conv.*Ws(j)); % set minimum gustiness^M
            S=sqrt(ur.^2 + wg.^2);^M


            Bf=-grav/ta*usr*(tsr+0.61*ta*qsr)
            if (Bf.gt.0) then
              Wg=Beta*(Bf*zi)**.333
            else
              Wg=0.2
            endif

    IMPROVE IT!!!!!!!!!!
                                       
    """

    Ws = u_star *(-CVB_depth/(kappa*L))**(1./3)
    # Where zeta_u is lesser than zero, do the check below.
    # Converction in unstable condition only
    # zeta_u = zr/L
    # So, zeta_u will be negative only if L is negative.
    # I'll do here a check for negative L, but should be 
    #     for a negative zr.
    wg = N.maximum(min_gustiness,beta_conv*Ws)
    wg[N.greater(L,0)]=min_gustiness

    return wg
    

def latent_heat(T_sea):
    """Latent heat of vaporization

    Copied from Air-Sea routines. Find the right reference for it

    Maybe it should be on ocean functions group.

    If consider the Cool Skin, must has one variable more.
    
    Input:
        =>
    Output:
        =>

    Validated with Air Sea.
    >>> latent_heat(N.array([-5.,0.,5.,20.,30.]))
    array([ 2512850.,  2501000.,  2489150.,  2453600.,  2429900.])
    """

    Le=(2.501-0.00237*(T_sea))*10**6;

    return Le

def turbulent_heat_fluxes(air_rho,u_star,T_star,q_star,Le,cp=_cp):
    """Latent and Sensible heat fluxes

    
    Input:
        =>
    Output:
        =>
    """
    Hs=air_rho*cp*u_star*T_star
    print "Hs",Hs
    Hl=air_rho*Le*u_star*q_star
    print "Hl",Hl

    return Hs, Hl
    

#def drag_coefficient(u,z0,z=None,kappa=_kappa,method="Smith_N",Psi_u=None):
#    """Drag Coefficient (C_D)
#    
#    Input:
#        =>
#    Output:
#        =>
#    """
#
#    if(method=="LargePond"):
#    #Unfinished!!!!
#        print "Uncomplete Large & Pond method!!!!!"
#        return
#
#        for i in range(len(u)):
#            if (u[i] < 10):
#                C_D[i] = 1.15e-3
#            elif (u[i] >= 10):
#                C_D[i] = 4.9e-4 + 6.5e-5*u[i]
#    #Check if this method could be rightlly be called as Smith!
#    elif(method=="Smith_N"):
#        C_D = (kappa/(N.log(z/z0)))**2
#    elif(method=="Smith"):
#        C_D = (kappa/(N.log(z/z0)-Psi_u))**2
#    else:
#        return
#
#    return C_D

def drag_coefficient(z,z0,Psi_u=0,kappa=_kappa):
    """
    incomplete!!!! Large and Pond will be in another function or every buddy together with differen method?
    
    Input:
        =>
    Output:
        =>
    """
    C_D = (kappa/(N.log(z/z0)-Psi_u))**2

    return C_D

def cdnlp(sp,z):
    """Large and Pond method for estimate the drag coefficient.

    Only translated from the Air-Sea routines.

    ATENTION!!!! Think on a better way to manager between the different methods for CD
    """

    a=N.log(z/10)/_kappa
    tol=.001
    u10o=N.zeros([N.size(sp)])
    cd=1.15e-3*N.ones(N.size(sp))
    u10=sp/(1+a*(cd)**0.5)

    delta=N.absolute(u10-u10o)

    while ((delta>tol).any()):
        u10o=u10
        cd=(4.9e-4+6.5e-5*u10o)
        index=u10o<10.15385
        cd[index]=1.15e-3
        u10=sp/(1+a*(cd)**0.5)
        delta=N.absolute(u10-u10o)

    return cd,u10

def transfer_coefficient(z,z0,Psi=0,kappa=_kappa):
    """
    
    Input:
        =>
    Output:
        =>
    """

    C = kappa/(N.log(z/z0)-Psi)

    return C

def set_z0(u_str, nu, g=9.8, alpha_c=_alpha_c, R_roughness=_R_roughness):
    """Aerodynamic Roughness length (z0)

    Estimate roughness length according to Smith(1988), in future include other methods.
    Input: 
        - u_star => [],
        -alpha_c => Alpha de Charnock [?],
        - R_roughness => Reynolds roughness [?]
    Output:
        - z0 => roughness length [?]

    >>> set_z0(N.array([0.1369]), N.array([1.5496e-05]))
    array([  3.34876332e-05])
    >>> set_z0(N.array([0.1366]), N.array([1.4586e-05]))
    array([  3.26900849e-05])
    >>> set_z0(N.array([0.2817]), N.array([1.5221e-05]))
    array([  9.50154078e-05])
    >>> set_z0(N.array([0.4106]), N.array([1.5774e-05]))
    array([ 0.00019346])
    """

    z_c = alpha_c * u_str**2 / g
        
    z_s = R_roughness * nu / u_str

    z0 = z_c + z_s

    return z0

def roughness_Reynolds(z0, U_star, nu):
    """Roughness Reynolds Number

        Same relation of the roughness_length function.
        The relation is the same for friction, temperature and moisture,
    only changes the z0 (or z0t or z0q) value.
    
    Input:
        =>
    Output:
        =>
    """

    Rr = z0*U_star/nu

    return Rr
    
def roughness_length(R, U_star, nu):
    """Aerodynamic Roughness length (z0)
        
        Could be used for U, T or q

        Same relation of the roughness_Reynolds.
    
    Input:
        =>
    Output:
        =>
    """
         
    z0 = nu*R/U_star

    return z0    

def stability_parameter(zr,zt,zq,L):
    """
    
    Input:
        =>
    Output:
        =>
    """

    """
    % set upper limit on zr/L = 3.0 to force convergence under
    % very stable conditions. Assume that zr, zt and zq comparable.
    index_limit   = (L<zr/3 & L>0);
    L(index_limit)=zr(index_limit)/3;
    
    zetu=zr./L;  % nondimensionalized heights
    zett=zt./L;
    zetq=zq./L;
    """

    index_limit = (N.less(L,zr/3) & N.greater(L,0))

    #Improve it!
    #L[index_limit] = zr[index_limit]/3
    L[index_limit] = zr/3

    zeta_u=zr/L
    zeta_T=zt/L
    zeta_q=zq/L

    return zeta_u, zeta_T, zeta_q
                                

def friction_velocity(u,z,z0,psi_u=0,kappa=.4):
    """Friction Velocity (u_star)

    
    Input:
        =>
    Output:
        =>
    """
    u_star = u * kappa/(N.log(z/z0)-psi_u)
    return u_star


def set_psi(zeta,who=None):
    """
    
    Input:
        =>
    Output:
        =>

    >>> set_psi(N.array([-0.410665646, -0.583060182,-0.623164355]),'u')
    array([ 0.68949806,  0.838676  ,  0.86933721])
    >>> set_psi(N.array([-0.410665646, -0.583060182, -0.623164355]),'q') 
    array([ 1.2324603 ,  1.46971557,  1.51682981])
    """

    psi = N.zeros(N.shape(zeta),N.Float)

    index_low=N.less(zeta,0)
    index_high=N.greater_equal(zeta,0)

    if(who=="u"):
        #if(zeta < 0):
        x=(1-15.*zeta[index_low])**.25                        #Kansas unstable
        psik=2.*N.log((1.+x)/2.)+N.log((1.+x**2)/2.)-2.*N.arctan(x)+2.*N.arctan(1.)
        y=(1.-10.15*zeta[index_low])**.3333                   #Convective
        psic=1.5*N.log((1.+y+y*y)/3.)-N.sqrt(3.)*N.arctan((1.+2.*y)/N.sqrt(3.))+ 4.*N.arctan(1.)/N.sqrt(3.)
        f=zeta[index_low]*zeta[index_low]/(1.+zeta[index_low]*zeta[index_low])
        psi[index_low]=(1.-f)*psik+f*psic
        #else:
        c=N.minimum(50.,0.35*zeta[index_high])                       #Stable
        psi[index_high]=-((1.+1.*zeta[index_high])**1.+.6667*(zeta[index_high]-14.28)/N.exp(c)+8.525)

    elif( (who=="q") | (who=="T") ):
        #if(zeta < 0):
        x=(1-15.*zeta[index_low])**.5                          #Kansas unstable
        psik=2.*N.log((1.+x)/2.)
        y=(1.-34.15*zeta[index_low])**.3333                    #Convective
        psic=1.5*N.log((1.+y+y*y)/3.)-N.sqrt(3.)*N.arctan((1.+2.*y)/N.sqrt(3.)) +4.*N.arctan(1.)/N.sqrt(3.)
        f=zeta[index_low]*zeta[index_low]/(1.+zeta[index_low]*zeta[index_low])
        psi[index_low]=(1.-f)*psik+f*psic
        #else:
        c=N.minimum(50.,0.35*zeta[index_high])                        #Stable
        psi[index_high]=-((1.+2.*zeta[index_high]/3.)**1.5+.6667*(zeta[index_high]-14.28)/N.exp(c)+8.525)

    else: return
        
    return psi

def set_psi_u(zeta):
    """

    Based on Fairall algoritm, version 2.6 in MatLab


    >>> set_psi_u(N.array([-0.2,-0.12]))
    array([ 0.44199247,  0.30937727])
    >>> set_psi_u(N.array([0.1,0.23]))
    array([-0.49224604, -1.10847797])
    """
    alpha = 15.
    beta = 0.25 # 1/3.
    psi = N.zeros(N.shape(zeta),N.Float)

    index_low=N.less(zeta,0)
    #index_high=N.greater_equal(zeta,0)
    index_high=N.greater(zeta,0)

    #phi = (1-alpha*(zeta))**(-beta)
    phi = (1-alpha*(zeta[index_low]))**(0.25)
    psik=2.*N.log((1.+phi)/2.)+N.log((1.+phi**2)/2.)-2.*N.arctan(phi)+N.pi/2
    phi = (1-10.15*zeta[index_low])**(1./3)
    psic=1.5*N.log((1.+phi+phi**2)/3.) -3.**0.5 *N.arctan((1.+2.*phi)/(3.**0.5))+ N.pi/(3.**0.5)

    f = zeta[index_low]**2 / (1+zeta[index_low]**2)
    psi[index_low] = (1-f)*psik +f*psic

    c = N.minimum(50,.35*zeta[index_high])
    psi[index_high] = -((1+1.0*zeta[index_high])**1.0+.667*(zeta[index_high]-14.28)/N.exp(c)+8.525)

    return psi

def set_psi_tq(zeta):
    """
    Based on Fairall algoritm, version 2.6 in MatLab


    >>> set_psi_tq(N.array([-0.2,-0.12]))
    array([ 0.8154819 ,  0.58197985])
    >>> set_psi_tq(N.array([0.1,0.23]))
    array([-0.49800232, -1.12097035])
    """
    psi = N.zeros(N.shape(zeta),N.Float)
    
    index_low=N.less(zeta,0)
    index_high=N.greater(zeta,0)

    phi=(1-15*zeta[index_low])**.5
    psik=2*N.log((1+phi)/2.)
    phi=(1-34.15*zeta[index_low])**.3333
    psic=1.5*N.log((1+phi+phi**2)/3.)-3.**0.5*N.arctan((1+2*phi)/3.**0.5)+N.pi/3.**0.5

    f=zeta[index_low]**2/(1+zeta[index_low]**2)
    psi[index_low]=(1-f)*psik+f*psic

    c = N.minimum(50,.35*zeta[index_high])
    psi[index_high]=-((1+2./3*zeta[index_high])**1.5+.6667*(zeta[index_high]-14.28)/N.exp(c)+8.525)

    return psi

def set_Tv_str(T_str,q,Ka,q_str,epsilon=_epsilon):
    """
    >>> Tv_str(-0.0293802729,0.0181,301.549,-0.00027412031)
    -0.080127690762804793
    """

    # Maybe o61 should be lodade on constants!!!!
    o61 = 1/epsilon-1
    Tv_str = (T_str*(1 + o61*q) + o61*Ka*q_str)

    return Tv_str

def monin_obukhov_length(u_str,Tv_str,Kv,g=9.8,epsilon=_epsilon,kappa=_kappa):
    """Monin-Obukhov Length (L)

    From Godfrey91, Taylor01(sec. 7.4)

    
    Input:
        =>
    Output:
        =>

    >>> monin_obukhov_length(0.158229911,-0.0801295319,28.4+273.15)
    -23.449520267874956
    >>> monin_obukhov_length(0.133294969,-0.0839926282,28.1 +273.15)
    -15.860010417307238
    >>> monin_obukhov_length(0.171331148,-0.0810823153,28. +273.15)
    -27.134351301071682
    """
    o61 = 1/epsilon-1
    b_str=g*Tv_str/Kv
    L=(u_str**2)/(kappa*b_str)
    
    return L


def lkb(R_r):
    """Roughness Reynolds number for temperature and humidity

    LKB method to define R_T and R_q based on R_r

    From Liu, Katsaros and Businger, J. of the Atmos. Sci.,
        Volume 36 Number 9 Sepmtember 1979

    
    Input:
        =>
    Output:
        =>
    Validated with Air Sea.
    What should be the answer for R_r=0.0??
    >>> lkb(N.array([0.1]))
    (array([ 0.177]), array([ 0.292]))
    >>> lkb(N.array([0.5]))
    (array([ 0.72270585]), array([ 1.01987665]))
    >>> lkb(N.array([5.0]))
    (array([ 0.31571986]), array([ 0.48224191]))
    >>> lkb(N.array([20.0]))
    (array([ 0.05616424]), array([ 0.10256818]))

    """

    # Maybe use tuples?!?! Whats better?
    # ZtCoef={'InfLim':0.0,'SupLim':0.5,'a':.177,'b':0}

    Coefs = N.array([ \
      [0.000,0.110,0.177,0.000,0.292,0.000], \
      [0.110,0.825,1.376,0.929,1.808,0.826], \
      [0.925,3.000,1.026,-0.599,1.393,-0.528], \
      [3.000,10.00,1.625,-1.018,1.956,-0.870], \
      [10.00,30.00,4.661,-1.475,4.994,-1.297], \
      [30.00,100.0,34.904,-2.067,30.790,-1.845] \
      ])

    # Where indices are
    #   0 -> Inferior limit value for R_r
    #   1 -> Superior limit value for R_r
    #   2 -> a1
    #   3 -> b1
    #   4 -> a2
    #   5 -> b2

    # Z_T U_ast / nu = a1*R_r^b1
    # Z_Q U_ast / nu = a2*R_r^b2

    R_T = N.zeros(N.shape(R_r),N.Float)
    R_q = N.zeros(N.shape(R_r),N.Float)

    for bin in Coefs:
        indice = N.greater(R_r,bin[0]) & N.less_equal(R_r,bin[1])
        R_T[indice]=bin[2]*R_r[indice]**bin[3]
        R_q[indice]=bin[4]*R_r[indice]**bin[5]

    return R_T, R_q

def spectral_brightness(K,_lambda,k_Boltzmann=_k_Boltzmann,h_Planck=_h_Planck,c=_c):
    """
    """

    B_lambda = 2*h_Planck*c**2/_lambda**5 * 1/(N.exp(h_Planck*c/k_Boltzmann/K/_lambda)-1)
    # m^-1 to Micrometro^-1
    B_lambda = B_lambda*1e-6

    return B_lambda
    
# Dieletric constant
# epsilon_s = 87.134 - 1.949e-1*T -1.276e-2*T**2 +2.491e-4*T**3
# gamma = 1 +1.613*-5*S*T -3.656e-3*S +3.210e-5*S**2 -4.232e-7*S**3

def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()
