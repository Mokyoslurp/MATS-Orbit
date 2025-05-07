from typing import Union

from org.orekit.time import AbsoluteDate, TimeScalesFactory  # type: ignore
from org.orekit.propagation.analytical.tle import TLE  # type: ignore


def load_tles(file_path: str):
    # Load TLEs from file (only keep the first for now)
    with open(file_path) as tle_file:
        tle_lines = tle_file.readlines()

    tles = [TLE(tle_lines[2 * i], tle_lines[2 * i + 1]) for i in range(len(tle_lines) // 2)]

    return tles


def _find_closest_tle(tles: list[TLE], date: AbsoluteDate):
    i = len(tles) - 1
    tle = tles[i]
    while tle.getDate().compareTo(date) > 0 and i >= 0:
        i -= 1
        tle = tles[i]

    return i, tle


def list_date_to_absolute_date(date: list[Union[float, int]]):
    absolute_date = AbsoluteDate(
        date[0],
        date[1],
        date[2],
        date[3],
        date[4],
        date[5],
        TimeScalesFactory.getUTC(),
    )
    return absolute_date
