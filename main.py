from src.util import load_tles, list_date_to_absolute_date  # noqa: E402
from src.loop import loop_on_tles  # noqa: E402

from src.eclipse import get_eclipse, plot_eclipse  # noqa: E402
from src.orbital_parameters import get_orbital_parameters, plot_orbital_parameters  # noqa: E402
from src.trajectory import (  # noqa: E402
    get_trajectory,
    plot_earth_2D,
    plot_earth_3D,
    plot_elevation,
    plot_global_orbit,
    plot_local_orbit,
    plot_sza,
)
from src.dst import get_dsts, plot_dsts


# Set time interval: Year, Month, Day, Hour, Minute, Second (UTC)
start_date = list_date_to_absolute_date([2023, 1, 1, 0, 0, 0.0])
end_date = list_date_to_absolute_date([2023, 1, 2, 0, 0, 0.0])

# MATS:
mats_tles = load_tles("data/sat000054227_fixed.txt")

mats_pv_vectors, mats_events = loop_on_tles(mats_tles, start_date, end_date, time_step=1 * 60.0)

mats_trajectory = get_trajectory(mats_pv_vectors)
mats_eclipse = get_eclipse(mats_events)
mats_orbital_parameters = get_orbital_parameters(mats_tles)


# DSTS
dsts_files = ["dst01"]
dsts = get_dsts(dsts_files)

# Plots

plot_elevation(mats_trajectory)
plot_earth_3D(mats_trajectory)
plot_earth_2D(mats_trajectory)
plot_eclipse(mats_eclipse)


plot_sza(mats_trajectory)
plot_local_orbit(mats_trajectory)
plot_global_orbit(mats_trajectory)

plot_orbital_parameters(mats_orbital_parameters)

plot_dsts(dsts)
