from datetime import datetime
import pandas as pd
import plotly.express as px


filename = "data/dst01.txt"


def _dst_one_day(line: str):
    year = 2000 + int(line[3:5])
    month = int(line[5:7])
    day = int(line[8:10])

    datetimes = [datetime(year, month, day, hour) for hour in range(24)]
    dsts = [int(line[20 + 4 * i : 20 + 4 * (i + 1)]) for i in range(24)]

    return datetimes, dsts


def _dst_one_month(filename: str):
    datetimes = []
    dsts = []

    with open(filename) as file:
        lines = file.readlines()

    for line in lines[:-2]:
        datetimes_one_day, dsts_one_day = _dst_one_day(line)

        datetimes += datetimes_one_day
        dsts += dsts_one_day

    return datetimes, dsts


def _dst_all(filenames: list[str]):
    datetimes = []
    dsts = []

    for filename in filenames:
        datetimes_one_month, dsts_one_month = _dst_one_month("data/dst/" + filename + ".txt")
        datetimes += datetimes_one_month
        dsts += dsts_one_month

    return datetimes, dsts


def get_dsts(filenames: list[str]) -> pd.DataFrame:
    datetimes, dsts = _dst_all(filenames)
    data_frame = pd.DataFrame(data=zip(datetimes, dsts), columns=["datetime", "dst"])
    return data_frame


def plot_dsts(data_frame: pd.DataFrame):
    fig = px.line(
        data_frame,
        y=["dst"],
        x="datetime",
    )

    fig.show()
