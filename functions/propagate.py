from org.orekit.utils import TimeStampedPVCoordinates  # type: ignore
from org.orekit.time import AbsoluteDate, TimeScalesFactory  # type: ignore
from org.orekit.propagation import Propagator  # type: ignore
from org.orekit.propagation.analytical.tle import TLE, TLEPropagator  # type: ignore
from org.orekit.propagation.events import EclipseDetector, EventsLogger, AbstractDetector  # type: ignore
from org.orekit.propagation.events.handlers import ContinueOnEvent  # type: ignore


from .constants import INERTIAL_FRAME, SUN_RADIUS, SUN, EARTH


def _find_tle(tles: list[TLE], date: AbsoluteDate):
    i = len(tles) - 1
    tle = tles[i]
    while tle.getDate().compareTo(date) > 0 and i >= 0:
        i -= 1
        tle = tles[i]

    return i, tle


def detect_events(
    tle: TLE,
    start_date: AbsoluteDate,
    end_date: AbsoluteDate,
    detectors: list[AbstractDetector],
):
    propagator: Propagator = Propagator.cast_(TLEPropagator.selectExtrapolator(tle))

    logger = EventsLogger()
    for detector in detectors:
        logged_detector = logger.monitorDetector(detector)
        propagator.addEventDetector(logged_detector)

    # Used to trigger events
    propagator.propagate(start_date, end_date)

    return logger.getLoggedEvents()


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


def propagate_all(
    tles: list[TLE],
    start_date=list[int],
    end_date=list[int],
    time_step: float = 10.0,
    detect_eclipse: bool = True,
):
    start_date = AbsoluteDate(
        start_date[0],
        start_date[1],
        start_date[2],
        start_date[3],
        start_date[4],
        start_date[5],
        TimeScalesFactory.getUTC(),
    )
    end_date = AbsoluteDate(
        end_date[0],
        end_date[1],
        end_date[2],
        end_date[3],
        end_date[4],
        end_date[5],
        TimeScalesFactory.getUTC(),
    )

    dates = [tle.getDate() for tle in tles]
    length = len(dates)

    if not start_date:
        start_date = dates[0]
    if not end_date:
        end_date = dates[-1]

    date = start_date

    # Initialize the detectors
    detectors = []
    if detect_eclipse:
        detectors.append(
            EclipseDetector(SUN, SUN_RADIUS, EARTH).withUmbra().withHandler(ContinueOnEvent())
        )

    pv_vectors = []
    events = []

    while date.compareTo(end_date) < 0:
        i, tle = _find_tle(tles, date)

        print(f"{date} : TLE n° {i + 1}/{length}")

        if i + 1 == length:
            next_date = end_date
        else:
            next_date = dates[i + 1]
            if end_date.compareTo(next_date) < 0:
                next_date = end_date

        pv_vectors += propagate_one(tle, date, next_date, time_step)
        events += detect_events(tle, start_date, end_date, detectors)

        date = next_date

    return pv_vectors, events
