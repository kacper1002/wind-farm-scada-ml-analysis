import xarray as xr
import numpy as np

ds = xr.open_dataset("norre_m2_all.nc", engine="netcdf4")
#print(list(ds.data_vars))




# ---------------- Data explanation -----------------------
# *_pow -> power
# *_wsn -> nacelle wind speed
# *_ym -> yaw misalignment


import re

turbines = set()

for v in ds.data_vars:
    match = re.match(r'([a-f][1-7])_', v)
    if match:
        turbines.add(match.group(1))

# print(sorted(turbines))
# print("Number of turbines:", len(turbines))

# A. % of missing data
missing = ds.to_dataframe().isna().mean()*100
missing.sort_values(ascending=False).head(20)

print(missing)

# B. QC flag statistics
# How often the QC flag is triggered
qc_vars = [v for v in ds.data_vars if '_qc' in v]
qc_stats = {}

for v in qc_vars:
    qc_stats[v] = (ds[v] > 0).sum().values

print(qc_stats)


# C. Turbine availability
availability = {}

for t in turbines:
    pow_name = f"{t}_pow"
    
    if pow_name in ds.data_vars:
        power = ds[pow_name]
        availability[t] = (power > 0).mean().values * 100
    else:
        availability[t] = None
        print(f"Missing variable: {pow_name}")

# D. Turbines with available data
import re
all_positions = set()
power_turbines = set()
wsn_turbines = set()
ym_turbines = set()

print('##############')
print('Turbines with available data')
print('##############')

for v in ds.data_vars:
    m = re.match(r'([a-f][1-7])_(pow|wsn|ym)$', v)
    if m:
        turb, signal = m.groups()
        all_positions.add(turb)

        if signal == 'pow':
            power_turbines.add(turb)
        elif signal == 'wsn':
            wsn_turbines.add(turb)
        elif signal == 'ym':
            ym_turbines.add(turb)

print('All turbines positions: ', len(all_positions), sorted(all_positions))
print('Power Tubines: ', len(power_turbines), sorted(power_turbines))
print('WSN Turbines: ', len(wsn_turbines), sorted(wsn_turbines))
print('YM Turbines: ', len(ym_turbines), sorted(ym_turbines))

print('Missing power: ', sorted(all_positions - power_turbines))
print('Missing wsn: ', sorted(all_positions - wsn_turbines))
print('Missing ym: ', sorted(all_positions - ym_turbines))


# E. Confirm sampling interval
print('##############')
print('Confirming sampling interval')
print('##############')
dt = ds.time.diff('time')
print(dt.min().values)
print(dt.median().values)
print(dt.max().values)
print(ds.time.diff('time').median() / np.timedelta64(1,'m'))


# F. Check missing data percentage
import pandas as pd

print('##############')
print('Percentage of missing data')
print('##############')
missing_pct = (
    ds.to_dataframe()
    .isna()
    .mean()
    .mul(100)
    .sort_values(ascending=False)
)
print(missing_pct.head(20))


# G. QC Flag Frequency
print('##############')
print('QC flag frequency')
print('##############')

qc_vars = [v for v in ds.data_vars if v.endswith("_qc")]

qc_summary = []

for v in qc_vars:
    vals = ds[v].values
    total = (~pd.isna(vals)).sum()
    flagged = ((vals > 0) & ~pd.isna(vals)).sum()
    
    qc_summary.append({
        "variable": v,
        "non_nan_count": int(total),
        "flagged_count": int(flagged),
        "flagged_pct_of_non_nan": 100 * flagged / total if total > 0 else None
    })

qc_summary = pd.DataFrame(qc_summary).sort_values(
    "flagged_pct_of_non_nan", ascending=False
)

print(qc_summary.head(20))

# H. Plot of total wind farm production
import matplotlib.pyplot as plt
# ds['park'].plot(figsize=(12,4))
plt.figure(figsize=(12,6))

plt.plot(ds['time'], ds['park'], alpha=0.6)

plt.title('Wind Farm Total Power Production')
plt.xlabel('Time')
plt.ylabel('Power [kW]')

plt.grid(alpha=0.3)

plt.tight_layout()
plt.show()
x = 14000 / len(power_turbines)
print('Power per turbine: ', x)

# I. Additional plots for summary of Sprint 1

# Met mast wind speed over time
plt.figure(figsize=(12, 5))
plt.plot(ds["time"], ds["s31_1"], label="s31_1", alpha=0.7)
plt.plot(ds["time"], ds["s31_2"], label="s31_2", alpha=0.7)
plt.title("Met Mast Wind Speed Over Time")
plt.xlabel("Time")
plt.ylabel("Wind speed")
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()

# Met mast direction over time
plt.figure(figsize=(12, 5))
plt.plot(ds["time"], ds["d31_1"], label="d31_1", alpha=0.7)
plt.plot(ds["time"], ds["d34_2"], label="d34_2", alpha=0.7)
plt.title("Met Mast Wind Direction Over Time")
plt.xlabel("Time")
plt.ylabel("Direction [deg]")
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()

# Histogram of park power
plt.figure(figsize=(10, 5))

plt.hist(ds["park"].dropna(dim="time").values, bins=50)

plt.title("Distribution of Wind Farm Power")
plt.xlabel("Power [kW]")
plt.ylabel("Count")

plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()

# Missing data by variable type
import pandas as pd

missing_pct = ds.to_dataframe().isna().mean() * 100

summary = pd.DataFrame({
    "variable": missing_pct.index,
    "missing_pct": missing_pct.values
})

def classify_var(v):
    if v.endswith("_pow") or v.endswith("_pow_qc"):
        return "power"
    elif v.endswith("_wsn") or v.endswith("_wsn_qc"):
        return "wind speed"
    elif v.endswith("_ym") or v.endswith("_ym_qc"):
        return "yaw misalignment"
    elif v.startswith("s"):
        return "mast speed"
    elif v.startswith("d"):
        return "mast direction"
    else:
        return "park/connect"

summary["group"] = summary["variable"].apply(classify_var)

group_missing = summary.groupby("group")["missing_pct"].mean().sort_values(ascending=False)

plt.figure(figsize=(10, 5))
plt.bar(group_missing.index, group_missing.values)
plt.title("Average Missing Data by Variable Group")
plt.xlabel("Variable group")
plt.ylabel("Average missing [%]")
plt.xticks(rotation=20)
plt.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.show()

# Turbine average power map
import numpy as np
import pandas as pd

rows = list("abcdef")
cols = list(range(1, 8))

power_map = pd.DataFrame(index=rows, columns=cols, dtype=float)

for r in rows:
    for c in cols:
        t = f"{r}{c}"
        var = f"{t}_pow"
        if var in ds.data_vars:
            power_map.loc[r, c] = ds[var].mean().item()
        else:
            power_map.loc[r, c] = np.nan

plt.figure(figsize=(10, 5))
plt.imshow(power_map.astype(float), aspect="auto")
plt.colorbar(label="Mean power [kW]")
plt.title("Mean Turbine Power Across Wind Farm Layout")
plt.xlabel("Column")
plt.ylabel("Row")
plt.xticks(range(len(cols)), cols)
plt.yticks(range(len(rows)), [r.upper() for r in rows])

for i, r in enumerate(rows):
    for j, c in enumerate(cols):
        val = power_map.loc[r, c]
        label = f"{r.upper()}{c}"
        plt.text(j, i, label, ha="center", va="center", fontsize=8)

plt.tight_layout()
plt.show()

# Turbine data availability map
availability_map = pd.DataFrame(index=rows, columns=cols, dtype=float)

for r in rows:
    for c in cols:
        t = f"{r}{c}"
        var = f"{t}_pow"
        if var in ds.data_vars:
            availability_map.loc[r, c] = ds[var].notnull().mean().item() * 100
        else:
            availability_map.loc[r, c] = np.nan

plt.figure(figsize=(10, 5))
plt.imshow(availability_map.astype(float), aspect="auto")
plt.colorbar(label="Available power data [%]")
plt.title("Power Data Availability Across Wind Farm Layout")
plt.xlabel("Column")
plt.ylabel("Row")
plt.xticks(range(len(cols)), cols)
plt.yticks(range(len(rows)), [r.upper() for r in rows])

for i, r in enumerate(rows):
    for j, c in enumerate(cols):
        val = availability_map.loc[r, c]
        label = f"{r.upper()}{c}"
        plt.text(j, i, label, ha="center", va="center", fontsize=8)

plt.tight_layout()
plt.show()

# Sanity check plot
plt.figure(figsize=(8,6))

plt.scatter(
    ds["s31_1"],
    ds["park"],
    alpha=0.2,
    s=5
)

plt.title("Wind Speed vs Wind Farm Power (Sanity check)")
plt.xlabel("Met Mast Wind Speed")
plt.ylabel("Wind Farm Power [kW]")

plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()