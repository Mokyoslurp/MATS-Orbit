import orekit
from orekit.pyhelpers import setup_orekit_curdir

vm = orekit.initVM()
setup_orekit_curdir()

from .load_tles import load_tles  # noqa: E402
from .propagate import propagate_all  # noqa: E402
from .build_data_frame import build_data_frame  # noqa: E402
from .constants import EARTH, INERTIAL_FRAME, ESRANGE_FRAME  # noqa: E402
from .plots import plot_earth_2D, plot_earth_3D, plot_elevation  # noqa: E402

__all__ = [
    load_tles,
    propagate_all,
    build_data_frame,
    EARTH,
    INERTIAL_FRAME,
    ESRANGE_FRAME,
    plot_earth_2D,
    plot_earth_3D,
    plot_elevation,
]
