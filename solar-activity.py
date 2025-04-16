import math
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

def parse_epoch(epoch_str):
    year = int(epoch_str[0:2])
    year += 2000 if year < 57 else 1900
    day_of_year = float(epoch_str[2:])
    date = datetime(year, 1, 1) + timedelta(days=day_of_year - 1)
    return date

# constants
mu = 398600.4418  # km^3/s^2
RE = 6371.0       # middle earth radius
seconds_per_day = 86400

# TLE 
with open("tle.txt") as f:
    lines = [line.strip() for line in f if line.strip()]
    tle_list = list(zip(lines[::2], lines[1::2]))

# results
dates, perigees, apogees = [], [], []

for line1, line2 in tle_list:
    n = float(line2[52:63])  # mean motion
    e = float("0." + line2[26:33].strip())  # eccentricity
    epoch_str = line1[18:32]
    date = parse_epoch(epoch_str)
    
    a = (mu * (seconds_per_day / (2 * math.pi * n))**2) ** (1/3)
    rp = a * (1 - e)
    ra = a * (1 + e)
    hp = rp - RE
    ha = ra - RE

    dates.append(date)
    perigees.append(hp)
    apogees.append(ha)

# Plot
plt.figure(figsize=(10, 5))
plt.plot(dates, perigees, label="Perigee Altitude", marker='o')
plt.plot(dates, apogees, label="Apogee Altitude", marker='x')
plt.xlabel("Date")
plt.ylabel("Altitude over earth surface (km)")
plt.title("Perigee- and Apogee over time")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()