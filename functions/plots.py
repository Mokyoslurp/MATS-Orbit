import plotly.express as px
import geopandas
import matplotlib.pyplot as plt
import pandas as pd


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
        data_frame["2002-05-07":"2002-05-07"],
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
