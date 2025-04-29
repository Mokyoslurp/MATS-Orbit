from functions import (
    ESRANGE_FRAME,
    INERTIAL_FRAME,
    load_tles,
    propagate_all,
    build_data_frame,
    build_eclipse_data_frame,
    plot_elevation,
    plot_earth_2D,
    plot_earth_3D,
    plot_local_orbit,
    plot_global_orbit,
    plot_sza,
)

from org.orekit.propagation.analytical.tle import TLE


# Set time interval: Year, Month, Day, Hour, Minute, Second (UTC)
start_date = [2025, 4, 15, 0, 0, 0.0]
end_date = [2025, 4, 16, 0, 0, 0.0]

# MATS:
mats_tles = load_tles("data/sat000054227.txt")

mats_pv_vectors, mats_events = propagate_all(mats_tles, start_date, end_date)

mats_data_frame = build_data_frame(mats_pv_vectors, INERTIAL_FRAME, ESRANGE_FRAME)
mats_eclipse_data_frame = build_eclipse_data_frame(mats_events)


# ISS:
iss_tles = [
    TLE(
        "1 25544U 98067A   25105.53237150  .00014782  00000+0  27047-3 0  9993",
        "2 25544  51.6375 257.3560 0005276  47.8113  31.7820 15.49569282505441",
    )
]

iss_pv_vectors, iss_events = propagate_all(iss_tles, start_date, end_date, time_step=10.0)

iss_data_frame = build_data_frame(iss_pv_vectors, INERTIAL_FRAME, ESRANGE_FRAME)
iss_eclipse_data_frame = build_eclipse_data_frame(iss_events)

# Plots
# plot_elevation(mats_data_frame)
# plot_earth_3D(mats_data_frame)
# plot_earth_2D(mats_data_frame)
# print(mats_eclipse_data_frame.head())

plot_sza([mats_data_frame, iss_data_frame])
plot_local_orbit([mats_data_frame, iss_data_frame])
plot_global_orbit([mats_data_frame, iss_data_frame])
