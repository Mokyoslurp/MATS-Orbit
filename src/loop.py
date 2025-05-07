from org.orekit.time import AbsoluteDate  # type: ignore
from org.orekit.propagation import Propagator  # type: ignore
from org.orekit.propagation.analytical.tle import TLE, TLEPropagator  # type: ignore


from .util import _find_closest_tle
from .eclipse import _detect_eclipse
from .trajectory import _propagate_trajectory


def loop_on_tles(
    tles: list[TLE],
    start_date=AbsoluteDate,
    end_date=AbsoluteDate,
    time_step: float = 10.0,
):
    dates = [tle.getDate() for tle in tles]
    length = len(dates)

    if not start_date:
        start_date = dates[0]
    if not end_date:
        end_date = dates[-1]

    date = start_date

    pv_vectors = []
    events = []

    while date.compareTo(end_date) < 0:
        i, tle = _find_closest_tle(tles, date)

        print(f"{date} : TLE n° {i + 1}/{length}")

        if i + 1 == length:
            next_date = end_date
        else:
            next_date = dates[i + 1]
            if end_date.compareTo(next_date) < 0:
                next_date = end_date

        # (Cast is necessary here because Java does not have auto type casting so we have to do it in python)
        propagator: Propagator = Propagator.cast_(TLEPropagator.selectExtrapolator(tle))

        # Main place to put what is to be done during the loop
        pv_vectors += _propagate_trajectory(propagator, date, next_date, time_step)
        events += _detect_eclipse(propagator, date, next_date)

        date = next_date

    return pv_vectors, events
