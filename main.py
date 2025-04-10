import orekit
from orekit.pyhelpers import setup_orekit_curdir
from org.orekit.utils import TimeStampedPVCoordinates

from org.orekit.time import TimeScalesFactory, AbsoluteDate
from org.orekit.propagation import Propagator
from org.orekit.propagation.analytical.tle import TLE, TLEPropagator


import plotly.express as px
import geopandas
import matplotlib.pyplot as plt

from functions import (
    ESRANGE_FRAME,
    INERTIAL_FRAME,
    build_data_frame,
)

vm = orekit.initVM()
setup_orekit_curdir()


# Load TLEs from file (only keep the first for now)
with open("data/sat000054227.txt") as tle_file:
    tle_lines = tle_file.readlines()

tles = [TLE(tle_lines[2 * i], tle_lines[2 * i + 1]) for i in range(len(tle_lines) // 2)]

tle = tles[0]


# Propagation
# (Cast is necessary here because Java does not have auto type casting so we have to do it in python)
propagator: Propagator = Propagator.cast_(TLEPropagator.selectExtrapolator(tle))

extrapolated_date = AbsoluteDate(2002, 5, 7, 12, 0, 0.0, TimeScalesFactory.getUTC())
final_date = extrapolated_date.shiftedBy(60.0 * 60 * 24)

pv_vectors: list[TimeStampedPVCoordinates] = []

while extrapolated_date.compareTo(final_date) <= 0.0:
    # Get Position and velocity
    pv = propagator.getPVCoordinates(extrapolated_date, INERTIAL_FRAME)
    pv_vectors.append(pv)

    # Increment date
    extrapolated_date = extrapolated_date.shiftedBy(10.0)

data_frame = build_data_frame(pv_vectors, INERTIAL_FRAME, ESRANGE_FRAME)


# Plot

fig1 = px.line(
    data_frame[data_frame.elevation > 0],
    y="elevation",
    x="datetime",
    hover_name="datetime",
    hover_data=["azimuth", "elevation", "latitude", "longitude"],
)

fig2 = px.scatter_geo(
    data_frame["2002-05-07":"2002-05-07"],
    color="visible",
    lat="latitude",
    lon="longitude",
    opacity=0.3,
    hover_data=["elevation", "azimuth"],
    projection="orthographic",
)

fig1.show()
fig2.show()


# Getting world map data from geo pandas
url = "https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip"
worldmap = geopandas.read_file(url)

# Creating axes and plotting world map
fig, ax = plt.subplots(figsize=(16, 10))
worldmap.plot(color="lightgrey", ax=ax)

x = data_frame["longitude"]
y = data_frame["latitude"]
z = data_frame["visible"]
plt.scatter(
    x,
    y,
    c=z,
    alpha=0.6,
    cmap="autumn",
)
# plt.colorbar(label='Ground track')

# Creating axis limits and title
plt.xlim([-180, 180])
plt.ylim([-90, 90])

plt.title("Ground track")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.show()
