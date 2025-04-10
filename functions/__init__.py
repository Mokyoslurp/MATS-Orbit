import orekit
from orekit.pyhelpers import setup_orekit_curdir

vm = orekit.initVM()
setup_orekit_curdir()

from .build_data_frame import build_data_frame
from .constants import EARTH, INERTIAL_FRAME, ESRANGE_FRAME
