from functions import (
    ESRANGE_FRAME,
    INERTIAL_FRAME,
    load_tles,
    propagate_all,
    build_data_frame,
    plot_elevation,
    plot_earth_2D,
    plot_earth_3D,
)


tles = load_tles("data/sat000054227.txt")

# Set time interval: Year, Month, Day, Hour, Minute, Second (UTC)
start_date = [2025, 2, 25, 0, 0, 0.0]
end_date = [2025, 2, 27, 0, 0, 0.0]

# Propagation
pv_vectors = propagate_all(tles, start_date, end_date)

data_frame = build_data_frame(pv_vectors, INERTIAL_FRAME, ESRANGE_FRAME)

# Plots
plot_elevation(data_frame)
plot_earth_3D(data_frame)
plot_earth_2D(data_frame)
