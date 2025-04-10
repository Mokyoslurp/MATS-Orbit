from org.orekit.utils import Constants, IERSConventions
from org.orekit.bodies import OneAxisEllipsoid, GeodeticPoint
from org.orekit.frames import FramesFactory, TopocentricFrame

from math import radians

ITRF = FramesFactory.getITRF(IERSConventions.IERS_2010, True)
INERTIAL_FRAME = FramesFactory.getEME2000()

EARTH = OneAxisEllipsoid(
    Constants.WGS84_EARTH_EQUATORIAL_RADIUS, Constants.WGS84_EARTH_FLATTENING, ITRF
)

# Definition of Esrange station
_longitude = radians(21.063)
_latitude = radians(67.878)
_altitude = 341.0
ESRANGE = GeodeticPoint(_latitude, _longitude, _altitude)
ESRANGE_FRAME = TopocentricFrame(EARTH, ESRANGE, "Esrange")
