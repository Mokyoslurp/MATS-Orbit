import plotly.express as px
import pandas as pd
from math import pi
from datetime import datetime

from orekit.pyhelpers import absolutedate_to_datetime
from org.orekit.utils import Constants  # type: ignore
from org.orekit.propagation.analytical.tle import TLE  # type: ignore


def get_orbital_parameters(tles: list[TLE]):
    dates: list[datetime] = []
    n: list[float] = []
    e: list[float] = []
    a: list[float] = []
    rp: list[float] = []
    ra: list[float] = []
    hp: list[float] = []
    ha: list[float] = []
    i: list[float] = []
    omega: list[float] = []
    raan: list[float] = []

    for tle in tles:
        dates.append(absolutedate_to_datetime(tle.getDate()))

        n.append(tle.getMeanMotion())
        e.append(tle.getE())
        i.append(tle.getI())
        raan.append(tle.getRaan())
        omega.append(tle.getPerigeeArgument())

        a.append(((Constants.WGS84_EARTH_MU * (86400 / (2 * pi * n[-1])) ** 2) ** (1 / 3)) / 10e3)
        rp.append(a[-1] * (1 - e[-1]))
        ra.append(a[-1] * (1 + e[-1]))
        hp.append(rp[-1] - Constants.WGS84_EARTH_EQUATORIAL_RADIUS / 10e3)
        ha.append(ra[-1] - Constants.WGS84_EARTH_EQUATORIAL_RADIUS / 10e3)

    data = zip(tles, dates, n, e, a, rp, ra, hp, ha, i, raan, omega)

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
            "inclination",
            "raan",
            "perigee_argument",
        ],
    )

    data_frame["day"] = data_frame.datetime.dt.dayofyear
    data_frame["hour"] = data_frame.datetime.dt.hour
    data_frame.set_index("datetime", inplace=True, drop=False)
    data_frame.index.name = "Timestamp"

    return data_frame


def plot_orbital_parameters(data_frame: pd.DataFrame):
    fig = px.line(
        data_frame,
        y=[
            "semi_major_axis",
            "mean_motion",
            "eccentricity",
            "inclination",
            "apogee",
            "perigee",
            "perigee_argument",
            "raan",
        ],
        x="datetime",
        hover_name="datetime",
    )

    fig.show()
