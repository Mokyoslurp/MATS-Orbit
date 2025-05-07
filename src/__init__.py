import orekit
from orekit.pyhelpers import setup_orekit_curdir

vm = orekit.initVM()
setup_orekit_curdir()

from .constants import EARTH, INERTIAL_FRAME, ESRANGE_FRAME  # noqa: E402
from .util import load_tles, list_date_to_absolute_date  # noqa: E402
from .eclipse import get_eclipse, plot_eclipse  # noqa: E402
from .orbital_parameters import get_orbital_parameters, plot_orbital_parameters  # noqa: E402
from .trajectory import (  # noqa: E402
    get_trajectory,
    plot_earth_2D,
    plot_earth_3D,
    plot_elevation,
    plot_global_orbit,
    plot_local_orbit,
    plot_sza,
)
from .loop import loop_on_tles  # noqa: E402


__all__ = [
    EARTH,
    INERTIAL_FRAME,
    ESRANGE_FRAME,
    load_tles,
    list_date_to_absolute_date,
    loop_on_tles,
    get_eclipse,
    get_trajectory,
    get_orbital_parameters,
    plot_eclipse,
    plot_earth_2D,
    plot_earth_3D,
    plot_elevation,
    plot_global_orbit,
    plot_local_orbit,
    plot_sza,
    plot_orbital_parameters,
]
