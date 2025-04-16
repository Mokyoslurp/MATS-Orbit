import orekit
from orekit.pyhelpers import setup_orekit_curdir

vm = orekit.initVM()
vm = setup_orekit_curdir()

from org.orekit.data import DataProvidersManager, ZipJarCrawler
from org.orekit.utils import IERSConventions
from org.orekit.frames import FramesFactory
from org.orekit.bodies import OneAxisEllipsoid, CelestialBodyFactory
from org.orekit.time import AbsoluteDate, TimeScalesFactory
from org.orekit.propagation.analytical.tle import TLE, TLEPropagator
from org.orekit.models.earth import ReferenceEllipsoid
from org.orekit.utils import Constants
from org.orekit.utils import PVCoordinatesProvider
from org.hipparchus.geometry.euclidean.threed import Vector3D


from datetime import timedelta
import numpy as np
import matplotlib.pyplot as plt

# === Setup Orekit data === 
orekit_data_path = "C:\Users\Valentin Linz\Desktop\Studium\Space\Lab_1_MATS\MATS-Orbit\examples\orekit-data.zip"  # path to my Orekit-Files
DataProvidersManager.getInstance().addProvider(ZipJarCrawler(orekit_data_path))

# === example: one TLE from Files ===
line1 = "1 54227U 22147A   22308.79105818 -.00000055  00000+0  00000+0 0  9999"
line2 = "2 54227  97.6565 311.5159 0011681 302.3480 246.6083 14.92786674    05"
tle = TLE(line1, line2)

# === Initialisation ===
utc = TimeScalesFactory.getUTC()
propagator = TLEPropagator.selectExtrapolator(tle)
start_date = tle.getDate()
duration_minutes = 1440  # z.B. 1 Tag
step_seconds = 60

# === Referencesystem to body ===
inertial_frame = FramesFactory.getEME2000()
earth_frame = FramesFactory.getITRF(IERSConventions.IERS_2010, True)
earth = OneAxisEllipsoid(Constants.WGS84_EARTH_EQUATORIAL_RADIUS,
                         Constants.WGS84_EARTH_FLATTENING,
                         earth_frame)
sun = CelestialBodyFactory.getSun()

# === Calculation SZA over time ===
times = []
sza_values = []

for i in range(0, duration_minutes * 60, step_seconds):
    current_date = start_date.shiftedBy(i)
    pv_sat = propagator.getPVCoordinates(current_date, inertial_frame)
    geodetic_point = earth.transform(pv_sat.getPosition(), inertial_frame, current_date)
    
    # Zenitvektor am Ort (nach oben)
    zenith_vector = earth.transform(geodetic_point).getZenith()
    
    # Sonnenposition im gleichen Frame
    sun_pos = sun.getPVCoordinates(current_date, earth_frame).getPosition()
    
    # Ortsvektor vom Beobachter zur Sonne
    observer_pos = earth.transform(geodetic_point, earth_frame, current_date)
    sun_vector = sun_pos.subtract(observer_pos.getPosition())
    
    # Winkel zwischen Zenit und Sonne = SZA
    sza_rad = Vector3D.angle(zenith_vector, sun_vector)
    sza_deg = np.degrees(sza_rad)
    
    times.append(current_date.durationFrom(start_date) / 3600)  # in Stunden
    sza_values.append(sza_deg)

# === Plot ===
plt.figure(figsize=(10, 5))
plt.plot(times, sza_values)
plt.xlabel("Zeit seit Start (Stunden)")
plt.ylabel("Solar Zenith Angle (°)")
plt.title("Solar Zenith Angle entlang der Umlaufbahn")
plt.grid()
plt.show()