from org.orekit.utils import TimeStampedPVCoordinates
from org.orekit.time import AbsoluteDate
from org.orekit.propagation import Propagator
from org.orekit.propagation.analytical.tle import TLE, TLEPropagator


from .constants import INERTIAL_FRAME


def propagate_one(
    tle: TLE, start_date: AbsoluteDate, end_date: AbsoluteDate, time_step: float = 10.0
):
    # (Cast is necessary here because Java does not have auto type casting so we have to do it in python)
    propagator: Propagator = Propagator.cast_(TLEPropagator.selectExtrapolator(tle))

    pv_vectors: list[TimeStampedPVCoordinates] = []

    extrapolated_date = start_date

    while extrapolated_date.compareTo(end_date) <= 0.0:
        # Get Position and velocity
        pv = propagator.getPVCoordinates(extrapolated_date, INERTIAL_FRAME)
        pv_vectors.append(pv)

        # Increment date
        extrapolated_date = extrapolated_date.shiftedBy(time_step)

    return pv_vectors


def propagate_all(tles: list[TLE], time_step: float = 10.0):
    dates = [tle.getDate() for tle in tles]
    length = len(dates)

    pv_vectors = []

    for i, tle in enumerate(tles):
        if i + 1 == length:
            end_date = dates[i].shiftedBy(time_step)
        else:
            end_date = dates[i + 1]
        pv_vectors += propagate_one(tle, dates[i], end_date, time_step)

    return pv_vectors
