import orekit
from orekit.pyhelpers import setup_orekit_curdir, absolutedate_to_datetime
from org.orekit.utils import Constants, IERSConventions, TimeStampedPVCoordinates
from org.orekit.frames import FramesFactory, TopocentricFrame
from org.orekit.bodies import OneAxisEllipsoid, GeodeticPoint
from org.orekit.time import TimeScalesFactory, AbsoluteDate
from org.orekit.propagation import Propagator
from org.orekit.propagation.analytical.tle import TLE, TLEPropagator


from math import radians, pi
import plotly.express as px
import geopandas
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Initialize Orekit
vm = orekit.initVM()
setup_orekit_curdir()


# Define base frames
ITRF = FramesFactory.getITRF(IERSConventions.IERS_2010, True)
inertial_frame = FramesFactory.getEME2000()


# Load TLEs from file (only keep the first for now)
with open("data/sat000054227.txt") as tle_file:
    tle_lines = tle_file.readlines()

tles = [TLE(tle_lines[2 * i], tle_lines[2 * i + 1]) for i in range(len(tle_lines) // 2)]

tle = tles[0]

# Definition of Esrange station
earth = OneAxisEllipsoid(
    Constants.WGS84_EARTH_EQUATORIAL_RADIUS, Constants.WGS84_EARTH_FLATTENING, ITRF
)

longitude = radians(21.063)
latitude = radians(67.878)
altitude = 341.0
station = GeodeticPoint(latitude, longitude, altitude)
station_frame = TopocentricFrame(earth, station, "Esrange")

# Propagation
# (Cast is necessary here because Java does not have auto type casting so we have to do it in python)
propagator: Propagator = Propagator.cast_(TLEPropagator.selectExtrapolator(tle))

extrapolated_date = AbsoluteDate(2002, 5, 7, 12, 0, 0.0, TimeScalesFactory.getUTC())
final_date = extrapolated_date.shiftedBy(60.0 * 60 * 24)

pv_vectors: list[TimeStampedPVCoordinates] = []

while extrapolated_date.compareTo(final_date) <= 0.0:
    # Get Position and velocity
    pv = propagator.getPVCoordinates(extrapolated_date, inertial_frame)
    pv_vectors.append(pv)

    # Increment date
    extrapolated_date = extrapolated_date.shiftedBy(10.0)


# Populate data frame
data_frame = pd.DataFrame(data=pv_vectors, columns=["pv"])

data_frame["datetime"] = data_frame["pv"].apply(lambda x: absolutedate_to_datetime(x.getDate()))
data_frame["day"] = data_frame.datetime.dt.dayofyear
data_frame["hour"] = data_frame.datetime.dt.hour
data_frame.set_index("datetime", inplace=True, drop=False)
data_frame.index.name = "Timestamp"


data_frame["position"] = pv.getPosition()
data_frame["elevation"] = data_frame["pv"].apply(
    lambda x: station_frame.getElevation(x.getPosition(), inertial_frame, x.getDate()) * 180.0 / pi
)
data_frame["azimuth"] = data_frame["pv"].apply(
    lambda x: station_frame.getAzimuth(x.getPosition(), inertial_frame, x.getDate()) * 180.0 / pi
)

data_frame["ground_point"] = data_frame["pv"].apply(
    lambda pv: earth.transform(pv.position, inertial_frame, pv.date)
)
data_frame["latitude"] = np.degrees(data_frame.ground_point.apply(lambda gp: gp.latitude))
data_frame["longitude"] = np.degrees(data_frame.ground_point.apply(lambda gp: gp.longitude))

# Visible if satellite is in visibility cone of Esrange
data_frame["visible"] = data_frame.elevation.apply(
    lambda elevation: "Yes" if elevation > 0 else "No"
)
data_frame["visible_color"] = data_frame.elevation.apply(
    lambda elevation: "#FF0000" if elevation > 0 else "#0000FF"
)


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
    animation_frame="hour",
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
z = data_frame["visible_color"]
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
