from org.orekit.utils import Constants, IERSConventions
from org.orekit.bodies import OneAxisEllipsoid
from org.orekit.frames import FramesFactory

ITRF = FramesFactory.getITRF(IERSConventions.IERS_2010, True)
INERTIAL_FRAME = FramesFactory.getEME2000()

EARTH = OneAxisEllipsoid(
    Constants.WGS84_EARTH_EQUATORIAL_RADIUS, Constants.WGS84_EARTH_FLATTENING, ITRF
)
