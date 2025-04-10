import orekit
from orekit.pyhelpers import setup_orekit_curdir
from org.orekit.utils import TimeStampedPVCoordinates

from org.orekit.time import TimeScalesFactory, AbsoluteDate
from org.orekit.propagation import Propagator
from org.orekit.propagation.analytical.tle import TLE, TLEPropagator


from functions import (
    ESRANGE_FRAME,
    INERTIAL_FRAME,
    build_data_frame,
    plot_elevation,
    plot_earth_2D,
    plot_earth_3D,
)

vm = orekit.initVM()
setup_orekit_curdir()


# Load TLEs from file (only keep the first for now)
with open("data/sat000054227.txt") as tle_file:
    tle_lines = tle_file.readlines()

tles = [TLE(tle_lines[2 * i], tle_lines[2 * i + 1]) for i in range(len(tle_lines) // 2)]

tle = tles[0]


# Propagation
# (Cast is necessary here because Java does not have auto type casting so we have to do it in python)
propagator: Propagator = Propagator.cast_(TLEPropagator.selectExtrapolator(tle))

extrapolated_date = AbsoluteDate(2002, 5, 7, 12, 0, 0.0, TimeScalesFactory.getUTC())
final_date = extrapolated_date.shiftedBy(60.0 * 60 * 24)

pv_vectors: list[TimeStampedPVCoordinates] = []

while extrapolated_date.compareTo(final_date) <= 0.0:
    # Get Position and velocity
    pv = propagator.getPVCoordinates(extrapolated_date, INERTIAL_FRAME)
    pv_vectors.append(pv)

    # Increment date
    extrapolated_date = extrapolated_date.shiftedBy(10.0)

data_frame = build_data_frame(pv_vectors, INERTIAL_FRAME, ESRANGE_FRAME)


# Plots
plot_elevation(data_frame)
plot_earth_3D(data_frame)
plot_earth_2D(data_frame)
