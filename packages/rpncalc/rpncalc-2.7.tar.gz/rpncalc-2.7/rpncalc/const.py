#-----------------------------------------------------------------------------
# Copyright (c) 2005  Raymond L. Buvel
#
# Physical constants and conversion factors in the SI (MKS) system.  Values are
# from the 2002 CODATA recommended values as published on the NIST site
# (http://physics.nist.gov/cuu/index.html).  This module is part of rpncalc.
#
# The rpncalc module is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option) any
# later version.
#
# The rpncalc nodule is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# rpncalc; if not, write to the Free Software Foundation, Inc., 59 Temple
# Place, Suite 330, Boston, MA  02111-1307  USA
#-----------------------------------------------------------------------------
import math
import rpncalc
import clnum

# Note: all constants are converted to mpf form when they are installed in the
# calculator.  This is done only to make it easy to mix these values with
# rationals in a calculation.

c=299792458
mu0=4e-7*math.pi

constDict = dict(
c=float(c),             # Speed of light in vacuum (m/sec)
mu0=mu0,                # Permeability of vacuum (N/A^2)
eps0=1.0/(mu0*c*c),     # Permittivity of vacuum (F/m)
G=6.6742e-11,           # Newtonian gravitational constant (m^3/(kg*sec^2))
h=6.6260693e-34,        # Plank constant (J*sec)
h_=1.05457168e-34,      # h/(2*pi) (J*sec)
e=1.60217653e-19,       # Elementary charge (C)
alpha=7.297352568e-3,   # Fine-structure constant (unitless)
a0=0.5291772108e-10,    # Bohr radius (m)
me=9.1093826e-31,       # Electron mass (kg)
mp=1.67262171e-27,      # Proton mass (kg)
mn=1.67492728e-27,      # Neutron mass (kg)
Na=6.0221415e23,        # Avagadro constant (mol^-1)
k=1.3806505e-23,        # Boltzmann constant (J/K)
g=9.80665,              # Standard acceleration of gravity (m*s^-2)

plank_length=1.61624e-35,  # (m)
plank_time=5.39121e-44,    # (s)
plank_mass=2.17645e-8,     # (kg)

# The following were obtained from various sources on the internet.  No claim
# of precision here!
MT=1.0/4.2e15,          # Megatons per joule
)

constDict['Mev'] = 1.0/(constDict['e']*1e6) # Million electron volts per Joule

SIconstVoc = rpncalc.Vocabulary('SI constants')

for key,value in constDict.iteritems():
    SIconstVoc[key] = rpncalc.parms_v_1(clnum.mpf(value))

_mev_fac = clnum.mpf(c*c * constDict['Mev'])

# Convert mass in kg to Mev
def _toMev(m):
    return m*_mev_fac

# Convert mass in Mev to kg
def _mevFrom(m):
    return m/_mev_fac

SIconstVoc['>mev'] = rpncalc.parms_1_1(_toMev)
SIconstVoc['mev>'] = rpncalc.parms_1_1(_mevFrom)

# Toggle the installation of the constants.
def _si_const():
    if rpncalc.installVocabulary(SIconstVoc):
        return
    rpncalc.removeVocabulary(SIconstVoc)

rpncalc.systemVoc['si_const'] = _si_const
rpncalc.installHelp('si_const', '( -- )',
    'Switch the SI constants vocabulary in and out of the search order.')

# The constants are not selected because some of the names conflict with
# entries in the system vocabulary.

def installHelp(name, stack, description, format=True):
    rpncalc.installHelp(name, stack, description, format, SIconstVoc)

installHelp('c', '( -- c)', 'Speed of light in vacuum (m/sec)')
installHelp('mu0', '( -- mu0)', 'Permeability of vacuum (N/A^2)')
installHelp('eps0', '( -- eps0)', 'Permittivity of vacuum (F/m)')
installHelp('G', '( -- G)', 'Newtonian gravitational constant (m^3/(kg*sec^2))')
installHelp('h', '( -- h)', 'Plank constant (J*sec)')
installHelp('h_', '( -- h_)', 'h/(2*pi) (J*sec)')
installHelp('e', '( -- e)', 'Elementary charge (C)')
installHelp('alpha', '( -- alpha)', 'Fine-structure constant (unitless)')
installHelp('a0', '( -- a0)', 'Bohr radius (m)')
installHelp('me', '( -- me)', 'Electron mass (kg)')
installHelp('mp', '( -- mp)', 'Proton mass (kg)')
installHelp('mn', '( -- mn)', 'Neutron mass (kg)')
installHelp('Na', '( -- Na)', 'Avagadro constant (mol^-1)')
installHelp('k', '( -- k)', 'Boltzmann constant (J/K)')
installHelp('g', '( -- g)', 'Standard acceleration of gravity (m*s^-2)')
installHelp('plank_length', '( -- plank_length)', 'Plank unit of length (m)')
installHelp('plank_time', '( -- plank_time)', 'Plank unit of time (s)')
installHelp('plank_mass', '( -- plank_mass)', 'Plank unit of mass (kg)')
installHelp('MT', '( -- MT)', 'Megatons per joule')
installHelp('Mev', '( -- Mev)', 'Million electron volts per Joule')
installHelp('>mev', '(kg -- mev)', 'Convert mass in kilograms to Mev')
installHelp('mev>', '(mev -- kg)', 'Convert mass in Mev to kilograms')
