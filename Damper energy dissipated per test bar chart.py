#Total dissipated energy by dampers per test, bar chart

import os
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d

# === Settings ===
THRESHOLD = 0.4  # mm
SMOOTHING_SIGMA = 2
data_folder = r"C:\Users\danie\Documents\Master\Numerisk analyse\Tester\Alletester"

# === PGA Lookup ===
test_intensity_lookup = {
    "Test02": 0.04, "Test03": 0.09, "Test04": 0.09, "Test05": 0.09, "Test06": 0.18,
    "Test07": 0.18, "Test08": 0.18, "Test09": 0.27, "Test10": 0.27, "Test11": 0.36,
    "Test12": 0.36, "Test13": 0.36, "Test14": 0.09, "Test15": 0.18, "Test16": 0.18,
    "Test17": 0.18, "Test18": 0.27, "Test19": 0.27, "Test20": 0.27, "Test21": 0.36,
    "Test22": 0.45, "Test23": 0.18, "Test24": 0.27, "Test25": 0.36, "Test26": 0.45
}

# === Marker and color by config ===
config_marker = {"Config1": "o", "Config2": "s", "Config3": "v"}
config_color = {"Config1": "#1f77b4", "Config2": "#2ca02c", "Config3": "#d62728"}

summary = []

# === Loop through all Excel test files ===
for file_name in os.listdir(data_folder):
    if not file_name.endswith(".xlsx") or "Test" not in file_name:
        continue

    test_match = re.search(r"(Test\d+)", file_name)
    if not test_match:
        continue

    test_label = test_match.group(1)
    test_number = int(re.search(r"\d+", test_label).group())

    # Assign config manually
    if 2 <= test_number <= 13:
        config_label = "Config1"
    elif 14 <= test_number <= 22:
        config_label = "Config2"
    elif 23 <= test_number <= 26:
        config_label = "Config3"
    else:
        config_label = "UnknownConfig"

    intensity_g = test_intensity_lookup.get(test_label, None)
    if intensity_g is None:
        continue

    file_path = os.path.join(data_folder, file_name)
    df = pd.read_excel(file_path)
    time_series = df["Time (s)"]

    # Determine force based on test number
    FORCE_KN = 7.5 if test_number <= 22 else 5

    # Normalize displacement
    disp_columns = [col for col in df.columns if col.startswith("Disp[1]")]
    disp2_columns = [col for col in df.columns if col.startswith("Disp[2]")]
    df_disp2_norm = pd.DataFrame()
    for col in disp2_columns:
        df_disp2_norm[col] = df[col] - df[col].iloc[0]

    df_adjusted = df.copy()
    valid_disp_columns = []
    for col1 in disp_columns:
        suffix = col1.split("Disp[1]")[-1]
        col2 = f"Disp[2]{suffix}"
        if col2 in df_disp2_norm.columns:
            df_adjusted[col1] = df[col1] - df_disp2_norm[col2]
        normalized = df_adjusted[col1] - df_adjusted[col1].iloc[0]
        if normalized.max() >= THRESHOLD or normalized.min() <= -THRESHOLD:
            df_adjusted[col1] = normalized
            valid_disp_columns.append(col1)

    # Detect cycles and compute energy
    cycle_energy_data = []
    for col in valid_disp_columns:
        disp = df_adjusted[col].values
        if SMOOTHING_SIGMA > 0:
            disp = gaussian_filter1d(disp, sigma=SMOOTHING_SIGMA)
        velocity = np.gradient(disp)
        peak_indices = np.where(np.diff(np.sign(velocity)) != 0)[0] + 1
        time = time_series.values

        for i in range(len(peak_indices) - 1):
            idx1, idx2 = peak_indices[i], peak_indices[i + 1]
            d1, d2 = disp[idx1], disp[idx2]
            t1, t2 = time[idx1], time[idx2]

            if abs(d2 - d1) < THRESHOLD or (t2 - t1) < 0.05:
                continue

            area = abs(d2 - d1) * 2 * FORCE_KN
            cycle_energy_data.append(area)

    total_energy = sum(cycle_energy_data)
    summary.append({
        "Test No": test_label,
        "PGA (g)": intensity_g,
        "Config": config_label,
        "Energy (kJ)": 2*total_energy / 1000  # Convert J -> kJ
    })

# === Plotting ===
summary_df = pd.DataFrame(summary)
summary_df = summary_df.sort_values(["PGA (g)", "Test No"])
summary_df["PlotIndex"] = range(len(summary_df))

fig, ax1 = plt.subplots(figsize=(14, 6))
ax2 = ax1.twinx()

# Plot faint red bars for PGA
bar_width = 0.8
for _, row in summary_df.iterrows():
    ax2.bar(row["PlotIndex"], row["PGA (g)"], width=bar_width, color="red", alpha=0.2, zorder=0)

ax2.set_ylim(0, 0.5)
ax2.set_yticks(sorted(summary_df["PGA (g)"].unique()))
ax2.set_ylabel("PGA (g)", color="red")

# Plot energy points and annotate
for config in summary_df["Config"].unique():
    data = summary_df[summary_df["Config"] == config]
    ax1.scatter(data["PlotIndex"], data["Energy (kJ)"],
                label=config,
                marker=config_marker.get(config, "o"),
                color=config_color.get(config, "gray"),
                s=80,
                edgecolor="black",
                zorder=3)
    
    # Annotate energy value
    for _, row in data.iterrows():
        ax1.text(row["PlotIndex"], row["Energy (kJ)"] + 0.5,  # offset above point
                 f"{row['Energy (kJ)']:.1f}", 
                 ha="center", va="bottom", fontsize=12, color="black")

ax1.set_xlabel("Test No (ordered by PGA)", fontsize=16)
ax1.set_ylabel("Cumulative Energy Dissipated [kJ]", fontsize=16)
ax1.set_xticks(summary_df["PlotIndex"], fontsize=14)
ax1.set_xticklabels(summary_df["Test No"], rotation=45, fontsize=16)
ax1.set_title("Cumulative energy dissipation by dampers per test (sorted by PGA)", fontsize=18)
ax1.grid(True, linestyle="--", alpha=0.5)
ax1.legend(title="Configuration", loc="upper left", fontsize=14)

plt.tight_layout()
plt.show()
