#!/usr/bin/env python
# -*- coding: Latin-1 -*-

"""It's an example how to reach turbulent heat fluxes
"""

import numarray
import fluid.atmosphere.atmospheric_functions

import fluid.DataSet

Atm = fluid.DataSet.Atmosphere()

print dir(Atm)

HF = fluid.DataSet.HeatFlux()

print dir(HF)

HF.Ta   = numarray.array([27.70,28.40,27.60,28.00])
HF.q   = numarray.array([17.60,18.00,17.30,18.80])*1e-3
HF.p = 100800
HF.DOY = numarray.array([350.,351.,352.,353.])
HF.Lat=numarray.array([10.])
HF.z_u = 4.
HF.z_T = 3.
HF.z_q = 3.
HF.Qswi = numarray.array([100,200,220,300])
HF.SST  = numarray.array([29.00,29.20,29.00,29.30])
HF.U = numarray.array([4.70,2.50,5.90,2.80])  # Need to be an array
HF.RH = fluid.atmosphere.atmospheric_functions.vapor_pressure(fluid.atmosphere.atmospheric_functions.q2w(HF.q),100800) / fluid.atmosphere.atmospheric_functions.saturation_vapor_pressure(HF.Ta)

HF.recalculate()


print 'Ta',HF.Ta
print HF.Ka
print HF.Atm.Ta
print HF.RH
print HF.Atm.RH
print HF.p
print HF.Atm.p
print HF.ea
print 'SST',HF.SST
print 'NSA',HF.NSA
print 'Qcs',HF.Qcs
print 'FracQ',HF.FracQ
print 'C',HF.C
print 'Qlw',HF.Qlw
print 'nu_air',HF.nu_air
print 'U',HF.U
print 'u_star',HF.u_star
print 'Tv',HF.Tv
print 'q_sea',HF.q_sea
print 'HF.Atm.q',HF.Atm.q
#HF.set_transfer_coefficients()
print 'u_star',HF.u_star
print 'T_star',HF.T_star
print 'q_star',HF.q_star
print 'Le',HF.Le
print 'HF.Atm.rho_air',HF.Atm.rho_air
HF.set_tubulent_heat_fluxes()
print 'HF.Hs',HF.Hs
print 'HF.Hl',HF.Hl
