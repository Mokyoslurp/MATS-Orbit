import orekit
from orekit.pyhelpers import setup_orekit_curdir

vm = orekit.initVM()
setup_orekit_curdir()

from org.orekit.data import DataProvidersManager, ZipJarCrawler
from org.orekit.utils import IERSConventions, Constants, PVCoordinates, PVCoordinatesProvider, AbsolutePVCoordinates
from org.orekit.propagation.analytical.tle import TLE, TLEPropagator
from org.orekit.frames import StaticTransform, FramesFactory
from org.orekit.bodies import CelestialBodyFactory
from org.orekit.time import AbsoluteDate, TimeScalesFactory
from org.orekit.orbits import KeplerianOrbit, PositionAngleType
from org.orekit.propagation.analytical import KeplerianPropagator

import math
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from functions import INERTIAL_FRAME, SUN

#TLE of the ISS
tle = TLE(
        "1 25544U 98067A   25104.93771177  .00013802  00000+0  25327-3 0  9999",
        "2 25544  51.6362 260.3059 0005231  40.9775 319.1606 15.49550269505353",
    )
propagator = TLEPropagator.selectExtrapolator(tle)

target_frame = SUN.getInertiallyOrientedFrame()
print (target_frame)

x_earth = []
y_earth = []
el=[]
pv=[]
t = []
s = []

initialDate = AbsoluteDate(2025, 4, 15, 0, 0, 0.0,TimeScalesFactory.getUTC(),)

extrapDate = initialDate
finalDate = extrapDate.shiftedBy(60.0*60*24*1) #seconds - duration

rp = 400 * 1000         #  Perigee
ra = 2000 * 1000         #  Apoee
i = math.radians(90.0)      # inclinationa
omega = math.radians(90.0)   # perigee argument
raan = math.radians(0.0)  # right ascension of ascending node
lv = math.radians(0.0)    # True anomaly


a = (rp + ra + 2 * Constants.WGS84_EARTH_EQUATORIAL_RADIUS) / 2.0    
e = 1.0 - (rp + Constants.WGS84_EARTH_EQUATORIAL_RADIUS) / a

## Inertial frame where the satellite is defined
inertialFrame = FramesFactory.getEME2000()

## Orbit construction as Keplerian
initialOrbit = KeplerianOrbit(a, e, i, omega, raan, lv,
                              PositionAngleType.TRUE,
                              inertialFrame, initialDate, Constants.WGS84_EARTH_MU)

#propagator = KeplerianPropagator(initialOrbit)

while (extrapDate.compareTo(finalDate) <= 0.0):  
    s.append(propagator.propagate(extrapDate))
    t.append(extrapDate)
    extrapDate = extrapDate.shiftedBy(10.0) #time steps

for tmp_t, tmp_s in zip(t,s):
    trans = INERTIAL_FRAME.getTransformTo(target_frame, tmp_t)
    trans :StaticTransform= StaticTransform.cast_(trans)
    pv_coordinates : PVCoordinates=trans.transformPosition(tmp_s.getPVCoordinates())
    pos = pv_coordinates.getPosition()
    velocity = pv_coordinates.getVelocity()
    x_earth.append(pos.getX()/1000)
    y_earth.append(pos.getY()/1000)



plt.plot(x_earth,y_earth)
plt.show()