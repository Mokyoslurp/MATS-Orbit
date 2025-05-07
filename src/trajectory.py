import plotly.express as px
import plotly.graph_objects as go
import geopandas
import matplotlib.pyplot as plt
import pandas as pd
from math import pi
import numpy as np

from org.hipparchus.geometry.euclidean.threed import Vector3D  # type: ignore

from orekit.pyhelpers import absolutedate_to_datetime
from org.orekit.utils import TimeStampedPVCoordinates  # type: ignore
from org.orekit.frames import StaticTransform  # type: ignore
from org.orekit.propagation import Propagator  # type: ignore
from org.orekit.time import AbsoluteDate  # type: ignore


from .constants import EARTH, SUN, INERTIAL_FRAME, ESRANGE_FRAME


def _propagate_trajectory(
    propagator: Propagator,
    start_date: AbsoluteDate,
    end_date: AbsoluteDate,
    time_step: float = 10.0,
):
    pv_vectors: list[TimeStampedPVCoordinates] = []

    extrapolated_date = start_date

    while extrapolated_date.compareTo(end_date) <= 0.0:
        # Get Position and velocity
        pv = propagator.getPVCoordinates(extrapolated_date, INERTIAL_FRAME)
        pv_vectors.append(pv)

        # Increment date
        extrapolated_date = extrapolated_date.shiftedBy(time_step)

    return pv_vectors


def get_trajectory(pv_vectors: list[TimeStampedPVCoordinates]) -> pd.DataFrame:
    """Populates a data frame of some satellite orbital parameters and variables.

    Variables in data frame :


    :param pv_vectors: A list of TimeStampedPVCoordinates of the satellite through time
    :return: The populated data frame
    """
    station_frame = ESRANGE_FRAME

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
        lambda x: station_frame.getElevation(x.getPosition(), INERTIAL_FRAME, x.getDate())
        * 180.0
        / pi
    )
    data_frame["azimuth"] = data_frame["pv"].apply(
        lambda x: station_frame.getAzimuth(x.getPosition(), INERTIAL_FRAME, x.getDate())
        * 180.0
        / pi
    )

    data_frame["ground_point"] = data_frame["pv"].apply(
        lambda pv: EARTH.transform(pv.position, INERTIAL_FRAME, pv.date)
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


def plot_local_orbit(data_frame: pd.DataFrame):
    fig = go.Figure()
    fig.add_trace(
        go.Scatter3d(
            x=data_frame["x_local"],
            y=data_frame["y_local"],
            z=data_frame["z_local"],
        )
    )
    fig.add_trace(go.Scatter3d(x=[0, 0], y=[0, 0], z=[0, 0]))

    fig.show()


def plot_global_orbit(data_frame: pd.DataFrame):
    fig = go.Figure()
    fig.add_trace(
        go.Scatter3d(
            x=data_frame["x"],
            y=data_frame["y"],
            z=data_frame["z"],
        )
    )
    fig.add_trace(
        go.Scatter3d(
            x=data_frame["x_earth"],
            y=data_frame["y_earth"],
            z=data_frame["z_earth"],
        )
    )
    fig.show()


def plot_sza(data_frame: pd.DataFrame):
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=data_frame["datetime"],
            y=data_frame["sza"],
        )
    )
    fig.show()


def plot_elevation(data_frame: pd.DataFrame):
    fig = px.line(
        data_frame[data_frame.elevation > 0],
        y="elevation",
        x="datetime",
        hover_name="datetime",
        hover_data=["azimuth", "elevation", "latitude", "longitude"],
    )

    fig.show()


def plot_earth_3D(data_frame: pd.DataFrame):
    fig = px.scatter_geo(
        data_frame,
        color="visible",
        lat="latitude",
        lon="longitude",
        opacity=0.3,
        hover_data=["elevation", "azimuth"],
        projection="orthographic",
    )

    fig.show()


def plot_earth_2D(data_frame: pd.DataFrame):
    # Getting world map data from geo pandas
    url = "https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip"
    worldmap = geopandas.read_file(url)

    # Creating axes and plotting world map
    fig, ax = plt.subplots(figsize=(16, 10))
    worldmap.plot(color="lightgrey", ax=ax)

    plt.scatter(
        x=data_frame["longitude"],
        y=data_frame["latitude"],
        c=data_frame["visible"],
        alpha=0.6,
    )

    # Creating axis limits and title
    plt.xlim([-180, 180])
    plt.ylim([-90, 90])

    plt.title("Ground track")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.show()
