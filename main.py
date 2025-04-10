import orekit
from orekit.pyhelpers import setup_orekit_curdir
from org.orekit.propagation.analytical.tle import TLE

from functions import (
    ESRANGE_FRAME,
    INERTIAL_FRAME,
    propagate_all,
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
tles = tles[0:2]


# Propagation
pv_vectors = propagate_all(tles)

data_frame = build_data_frame(pv_vectors, INERTIAL_FRAME, ESRANGE_FRAME)

# Plots
plot_elevation(data_frame)
plot_earth_3D(data_frame)
plot_earth_2D(data_frame)
