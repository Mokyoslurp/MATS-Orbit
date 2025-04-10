import orekit
from orekit.pyhelpers import setup_orekit_curdir


from functions import (
    ESRANGE_FRAME,
    INERTIAL_FRAME,
    load_tles,
    propagate_all,
    build_data_frame,
    plot_elevation,
    plot_earth_2D,
    plot_earth_3D,
)

vm = orekit.initVM()
setup_orekit_curdir()


tles = load_tles("data/sat000054227.txt")
tles = tles[0:3]

# Propagation
pv_vectors = propagate_all(tles)

data_frame = build_data_frame(pv_vectors, INERTIAL_FRAME, ESRANGE_FRAME)

# Plots
plot_elevation(data_frame)
plot_earth_3D(data_frame)
plot_earth_2D(data_frame)
