import pandas as pd
from math import pi
import numpy as np
from datetime import datetime

from org.hipparchus.geometry.euclidean.threed import Vector3D  # type: ignore

from orekit.pyhelpers import absolutedate_to_datetime
from org.orekit.utils import TimeStampedPVCoordinates, Constants  # type: ignore
from org.orekit.frames import Frame  # type: ignore
from org.orekit.propagation.events import EventsLogger  # type: ignore
from org.orekit.propagation.analytical.tle import TLE  # type: ignore
from org.orekit.frames import StaticTransform  # type: ignore
from org.orekit.time import AbsoluteDate  # type: ignore


from .constants import EARTH, SUN, INERTIAL_FRAME


def build_data_frame(
    pv_vectors: list[TimeStampedPVCoordinates], inertial_frame: Frame, station_frame: Frame = None
) -> pd.DataFrame:
    """Populates a data frame of some satellite orbital parameters and variables.

    Variables in data frame :


    :param pv_vectors: A list of TimeStampedPVCoordinates of the satellite through time
    :return: The populated data frame
    """
    # Lists initialization
    earth_positions: list[Vector3D] = []
    positions: list[Vector3D] = []
    positions_from_earth: list[Vector3D] = []
    dates: list[AbsoluteDate] = []

    # Fill lists
    for pv_vector in pv_vectors:
        dates.append(pv_vector.getDate())
        # transform from Earth inertial frame to Sun inertial frame
        transform: StaticTransform = StaticTransform.cast_(
            INERTIAL_FRAME.getTransformTo(SUN.getInertiallyOrientedFrame(), dates[-1])
        )

        earth_positions.append(transform.transformPosition(Vector3D.ZERO))
        positions.append(transform.transformPosition(pv_vector.getPosition()))
        positions_from_earth.append(pv_vector.getPosition())

    # Convert Vector3D structure to a numpy array
    earth_positions = np.array([[p.getX(), p.getY(), p.getZ()] for p in earth_positions]) / 1000
    positions = np.array([[p.getX(), p.getY(), p.getZ()] for p in positions]) / 1000
    positions_from_earth = (
        np.array([[p.getX(), p.getY(), p.getZ()] for p in positions_from_earth]) / 1000
    )

    # Vectors of interest
    earth_satellite_vector = positions - earth_positions
    satellite_sun_vector = -positions

    # Compute Solar Zenith Angle
    num = np.multiply(earth_satellite_vector, satellite_sun_vector).sum(1)
    den = np.multiply(
        np.linalg.norm(earth_satellite_vector, axis=1), np.linalg.norm(satellite_sun_vector, axis=1)
    )

    sza = np.rad2deg(np.acos(np.divide(num, den)))

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

    # Positions of objects
    data_frame["x_earth"] = earth_positions[:, 0]
    data_frame["y_earth"] = earth_positions[:, 1]
    data_frame["z_earth"] = earth_positions[:, 2]
    data_frame["x"] = positions[:, 0]
    data_frame["y"] = positions[:, 1]
    data_frame["z"] = positions[:, 2]
    data_frame["x_local"] = positions_from_earth[:, 0]
    data_frame["y_local"] = positions_from_earth[:, 1]
    data_frame["z_local"] = positions_from_earth[:, 2]

    data_frame["sza"] = sza

    return data_frame


def build_orbit_parameters_data_frame(tles: list[TLE]):
    dates: list[datetime] = []
    n: list[float] = []
    e: list[float] = []
    a: list[float] = []
    rp: list[float] = []
    ra: list[float] = []
    hp: list[float] = []
    ha: list[float] = []

    for tle in tles:
        dates.append(absolutedate_to_datetime(tle.getDate()))

        n.append(tle.getMeanMotion())
        e.append(tle.getE())

        a.append(((Constants.WGS84_EARTH_MU * (86400 / (2 * pi * n[-1])) ** 2) ** (1 / 3)) / 10e3)
        rp.append(a[-1] * (1 - e[-1]))
        ra.append(a[-1] * (1 + e[-1]))
        hp.append(rp[-1] - Constants.WGS84_EARTH_EQUATORIAL_RADIUS / 10e3)
        ha.append(ra[-1] - Constants.WGS84_EARTH_EQUATORIAL_RADIUS / 10e3)

    data = zip(tles, dates, n, e, a, rp, ra, hp, ha)

    data_frame = pd.DataFrame(
        data=data,
        columns=[
            "tle",
            "datetime",
            "mean_motion",
            "eccentricity",
            "semi_major_axis",
            "perigee",
            "apogee",
            "perigee_altitude",
            "apogee_altitude",
        ],
    )

    data_frame["day"] = data_frame.datetime.dt.dayofyear
    data_frame["hour"] = data_frame.datetime.dt.hour
    data_frame.set_index("datetime", inplace=True, drop=False)
    data_frame.index.name = "Timestamp"

    return data_frame


def build_eclipse_data_frame(events: list[EventsLogger.LoggedEvent]):
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
