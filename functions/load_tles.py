from org.orekit.propagation.analytical.tle import TLE  # type: ignore


def load_tles(file_path: str):
    # Load TLEs from file (only keep the first for now)
    with open(file_path) as tle_file:
        tle_lines = tle_file.readlines()

    tles = [TLE(tle_lines[2 * i], tle_lines[2 * i + 1]) for i in range(len(tle_lines) // 2)]

    return tles
