import plotly.express as px
import pandas as pd

from orekit.pyhelpers import absolutedate_to_datetime
from org.orekit.time import AbsoluteDate  # type: ignore
from org.orekit.propagation import Propagator  # type: ignore
from org.orekit.propagation.events import EclipseDetector, EventsLogger  # type: ignore
from org.orekit.propagation.events.handlers import ContinueOnEvent  # type: ignore

from .constants import SUN_RADIUS, SUN, EARTH


def _detect_eclipse(
    propagator: Propagator,
    start_date: AbsoluteDate,
    end_date: AbsoluteDate,
) -> list[EventsLogger.LoggedEvent]:
    logger = EventsLogger()
    detector = EclipseDetector(SUN, SUN_RADIUS, EARTH).withUmbra().withHandler(ContinueOnEvent())
    logged_detector = logger.monitorDetector(detector)
    propagator.addEventDetector(logged_detector)

    # Used to trigger events
    propagator.propagate(start_date, end_date)

    return logger.getLoggedEvents()


def get_eclipse(events: list[EventsLogger.LoggedEvent]):
    start_time = None
    result = []

    for event in events:
        if not event.isIncreasing():
            start_time = event.getState().getDate()
        elif start_time:
            stop_time = event.getState().getDate()
            result.append(
                {
                    "Start": absolutedate_to_datetime(start_time),
                    "Stop": absolutedate_to_datetime(stop_time),
                    "EclipseDuration": stop_time.durationFrom(start_time) / 60,
                }
            )
            start_time = None
    result_df = pd.DataFrame.from_dict(result)
    return result_df


def plot_eclipse(data_frame: pd.DataFrame):
    if not data_frame.empty:
        fig = px.line(
            data_frame,
            x="Start",
            y="EclipseDuration",
        )
        fig.show()
