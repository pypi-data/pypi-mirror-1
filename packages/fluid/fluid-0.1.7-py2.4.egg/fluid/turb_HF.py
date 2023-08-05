#!/usr/bin/env python
# -*- coding: Latin-1 -*-

"""It's an example how to reach turbulent heat fluxes
"""

import numarray
import fluid.common.common
import fluid.common.gfd
import fluid.atmosphere.atmospheric_functions
import fluid.interaction.heat_flux
import fluid.interaction.others

from fluid import DataSet

Air = DataSet.Atmosphere()


Lat = numarray.array([15.,-5.,8.,4.,0.,15.,4.,0.,0.])

Ts = numarray.array([27.24,25.60,28.39,27.13,28.15,26.97,28.10,29.33,28.81])
Ks = Ts+273.15
Ta = numarray.array([27.07,25.21,27.94,26.50,27.27,26.90,28.14,28.39,27.99])
Ka = Ta+273.15

Air.Ta = Ta
Air.p = 100800.
Air.RH = numarray.array([0.841,0.813,0.792,0.847,0.848,0.899,0.802,0.839,0.810])

u = numarray.array([3.90,7.00,5.60,8.60,5.70,4.80,5.10,3.20,3.40])
z_u = numarray.array([4.])
z_T = numarray.array([3.])
z_q = numarray.array([3.])

p = 100800.

#e_sat=fluid.atmosphere.atmospheric_functions.saturation_vapor_pressure(Ta)
#w_sat = fluid.atmosphere.atmospheric_functions.mixing_ratio(e_sat,p)
#q_sat = fluid.atmosphere.atmospheric_functions.specific_humidity(w_sat)
#ea = fluid.atmosphere.atmospheric_functions.RH2e(RH,w_sat,p)
#w = fluid.atmosphere.atmospheric_functions.mixing_ratio(ea,p)
#q = fluid.atmosphere.atmospheric_functions.specific_humidity(w)
#air_nu = fluid.atmosphere.atmospheric_functions.air_viscosity((Ta))
g = fluid.common.gfd.gravity(Lat)

w_sat_sea = fluid.atmosphere.atmospheric_functions.saturation_mixing_ratio(Ts,p)
q_sat_sea = fluid.atmosphere.atmospheric_functions.specific_humidity(w_sat_sea)
q_sea = q_sat_sea*.98

Dq = Air.q-q_sea
DT = Air.Ta - Ts

Kv=fluid.atmosphere.atmospheric_functions.virtual_temperature(Ka,Air.ea,p=p)
Tv = fluid.common.common.K2C(Kv)


#% compute initial neutral scaling coefficients
#S=sqrt(ur.^2 + min_gustiness.^2);
#cdnhf=sqrt(cdntc(S,zr,Air.Ta)); % Smith's neutral cd as first guess


# Maybe first u_star gest should be inside find_transfer_coefficients
u_star = fluid.interaction.others.find_u_star(u, Air.nu_air, z_u, g=g)
#print "u_star",u_star
#u_star = 0.036*u
z0=fluid.interaction.others.set_z0(u_star, Air.nu_air)
#CD=fluid.interaction.others.drag_coefficient(z_u,z0)

u_star, T_star, q_star = fluid.interaction.others.find_transfer_coefficients(Air.Ta,Tv,Ts,Air.q,q_sea,u,z_u,z_T,z_q,Air.nu_air,u_star)


# compute latent heat
Le = fluid.interaction.others.latent_heat(Ts)

# compute fluxes into ocean
air_rho = fluid.atmosphere.atmospheric_functions.air_density(p,Kv)

Hs, Hl = fluid.interaction.others.turbulent_heat_fluxes(air_rho,u_star,T_star,q_star,Le)

#% compute transfer coefficients at measurement heights
CD=(u_star/u)**2
CT=u_star*T_star/(u*(DT)) # Stanton number
CQ=u_star*q_star/(u*(Dq))  # Dalton number

stress = fluid.interaction.others.wind_stress(air_rho,CD,u)
#
RI = fluid.interaction.others.richardson_number(Air.Ta,DT,Tv,Dq,u,z_u,g)
#
#% compute Webb correction to latent heat flux into ocean
#W = 1.61.*U_star.*Q_star + (1 + 1.61.*Q).*U_star.*T_star./T; % eqn. 21
#Hl_webb = rho.*Le.*W.*Q; % eqn. 22, Fairall et al. (1996), JGR, 101, p3751.
