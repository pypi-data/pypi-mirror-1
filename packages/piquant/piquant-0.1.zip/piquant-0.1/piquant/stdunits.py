######### PHYSICAL UNIT NAMES #####################
#------------------------------------ Dan Goodman -
# These are optional shorthand unit names which in
# most circumstances shouldn't clash with local names

"""Optional short unit names

This module defines the following short unit names:

mV, mA, uA (micro_amp), nA, pA, mF, uF, nF, mS, uS, ms,
Hz, kHz, MHz, cm, cm2, cm3, mm, mm2, mm3, um, um2, um3
"""

import units as _units

mV = _units.mvolt

mA = _units.mamp
uA = _units.uamp
nA = _units.namp
pA = _units.pamp

pF = _units.pfarad
uF = _units.ufarad
nF = _units.nfarad

nS = _units.nsiemens
uS = _units.usiemens

ms = _units.msecond

Hz = _units.hertz
kHz = _units.khertz
MHz = _units.Mhertz

cm = _units.cmetre
cm2 = _units.cmetre2
cm3 = _units.cmetre3
mm = _units.mmetre
mm2 = _units.mmetre2
mm3 = _units.mmetre3
um = _units.umetre
um2 = _units.umetre2
um3 = _units.umetre3

_units.all_units.extend([mV,mA,uA,nA,pA,pF,uF,nF,nS,uS,ms,Hz,kHz,MHz,cm,cm2,cm3,mm,mm2,mm3,um,um2,um3])