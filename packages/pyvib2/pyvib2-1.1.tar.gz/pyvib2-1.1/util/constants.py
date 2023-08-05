#  Copyright (C) 2007 Maxim Fedorovsky, University of Fribourg (Switzerland).
#       email : Maxim.Fedorovsky@unifr.ch, mutable@yandex.ru
#
#  This file is part of PyVib2.
#
#  PyVib2 is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  PyVib2 is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with PyVib2; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

"""Physical constants and conversion factors."""

__author__ = 'Maxim Fedorovsky'

from math import pi, log


## Bohr radius, m
A_BOHR = 0.5291772083E-10

## Electron mass, kg
ME = 9.10938188E-31

## Planck constant devided by 2*pi, J*s
HBAR = 1.05457266E-34

## Electron charge, C
ECHARGE = 1.602176462E-19

## Kelvin temperature, K
T_KELVIN = 273.15

## h = 2pi * HBAR, J*s
H = HBAR * (2.*pi)

## Boltzmann constant, J/K
KB = 1.3806503E-23

## Speed of light, m/s
C = 2.99792458E+08

## Speed of light, a.u
C_AU = 137.03599963

## Atomic mass unit = 1/12*m(C12), kg
M_AU = 1.6605402E-27

## Permeability of free space, H/m = N/A^2
MU_VACUUM = 4 * pi * 1E-07

## Permittivity of free space, F/m
EPS_VACUUM = 1./(MU_VACUUM * C * C)

## Avogadro's number, 1/mol
NA = 6.02214199E+23

## Universal gas constant, J/(mol*K)
R = 8.314472

## a.m.u. -> a.u
AMU2AU = 1822.88848

## bohr -> angstrom
BOHR2ANGSTROM = A_BOHR*1E+10

## HARTREE2INVCM: hartree -> reciprocal cm
HARTREE2INVCM = 219474.631371

## hartree -> J
HARTREE2J = 4.35974381E-18

## hartree -> kJ/mol, ~ 2625.562 kJ/mol
HARTREE2KJMOL = HARTREE2J * NA * 0.001

## cm**(-1) -> a.u. of time**(-1)
INVCM2AU = 1./HARTREE2INVCM

## Inch to cm
INCH2CM = 2.54

## Reduced Raman/ROA invariant sum{Lx_a V_ab Lx_b} * f_Qp_i**2 -> SI
RAMAN_ROA_INV2SI = pow(A_BOHR, 6) * pow(ECHARGE, 4) * ME / pow(HBAR, 4)

## Dipole strength -> epsilon (SI)
DIPSTRENGTH2EPSILON  = 2. * pi**2 * NA / (3. * EPS_VACUUM * H * C * log(10.))

## Rotational strength -> delta epsilon (SI)
ROTSTRENGTH2DEPSILON = 4. / C * DIPSTRENGTH2EPSILON

## Dipole strength a.u. -> SI : (A_BOHR*e)^2, C^2 * m^2
## see http://folk.uio.no/michalj/node69.html
DIPSTRENGTH2SI = pow(A_BOHR * ECHARGE, 2.)

## Rotational strength a.u. -> SI : hbar^3 / (e^2 * me^2 * C), C * m * J / T
## see http://folk.uio.no/michalj/node69.html
ROTSTRENGTH2SI = 1.572E-52
