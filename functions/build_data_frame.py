import pandas as pd
from math import pi
import numpy as np

from orekit.pyhelpers import absolutedate_to_datetime
from org.orekit.utils import TimeStampedPVCoordinates
from org.orekit.frames import Frame


from .constants import EARTH


def build_data_frame(
    pv_vectors: list[TimeStampedPVCoordinates], inertial_frame: Frame, station_frame: Frame = None
) -> pd.DataFrame:
    """Populates a data frame of some satellite orbital parameters and variables.

    Variables in data frame :


    :param pv_vectors: A list of TimeStampedPVCoordinates of the satellite through time
    :return: The populated data frame
    """
    # Populate data frame
    data_frame = pd.DataFrame(data=pv_vectors, columns=["pv"])

    data_frame["datetime"] = data_frame["pv"].apply(lambda x: absolutedate_to_datetime(x.getDate()))
    data_frame["day"] = data_frame.datetime.dt.dayofyear
    data_frame["hour"] = data_frame.datetime.dt.hour
    data_frame.set_index("datetime", inplace=True, drop=False)
    data_frame.index.name = "Timestamp"

    data_frame["position"] = data_frame["pv"].apply(lambda x: x.getPosition())
    data_frame["elevation"] = data_frame["pv"].apply(
        lambda x: station_frame.getElevation(x.getPosition(), inertial_frame, x.getDate())
        * 180.0
        / pi
    )
    data_frame["azimuth"] = data_frame["pv"].apply(
        lambda x: station_frame.getAzimuth(x.getPosition(), inertial_frame, x.getDate())
        * 180.0
        / pi
    )

    data_frame["ground_point"] = data_frame["pv"].apply(
        lambda pv: EARTH.transform(pv.position, inertial_frame, pv.date)
    )
    data_frame["latitude"] = np.degrees(data_frame.ground_point.apply(lambda gp: gp.latitude))
    data_frame["longitude"] = np.degrees(data_frame.ground_point.apply(lambda gp: gp.longitude))

    # Visible if satellite is in visibility cone of Esrange, Red if visible, Blue if not
    data_frame["visible"] = data_frame.elevation.apply(
        lambda elevation: "#FF0000" if elevation > 0 else "#0000FF"
    )

    return data_frame
