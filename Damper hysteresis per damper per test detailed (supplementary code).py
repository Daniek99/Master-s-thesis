
#Damper enegy dissipation per damper, per cycle per test visualized with hysteresis diagrams and bar charts



import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors

# === Load Data ===
file_path = r"C:\Users\danie\Documents\Master\Numerisk analyse\Tester\Config1Disp[1]\ACQ_20240910_1822_Test13_T_CORR.xlsx"
df = pd.read_excel(file_path)
time_series = df["Time (s)"]

# === Settings ===
THRESHOLD = 0.4  # mm
FORCE_KN = 7.5    # ±7.5(?) kN constant force
dt = np.diff(time_series).mean()
window_length = int(3.0 / dt)

# === Normalize Displacement ===
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

# === Compute and Plot Hysteresis Cycles ===
cycle_energy_data = []

for col in valid_disp_columns:
    disp = df_adjusted[col].values
    time = time_series.values

    velocity = np.gradient(disp)
    peak_indices = np.where(np.diff(np.sign(velocity)) != 0)[0] + 1
    peak_indices = [i for i in peak_indices if abs(disp[i]) >= THRESHOLD]

    if len(peak_indices) < 2:
        continue

    # === Plotting the hysteresis loops ===
    plt.figure(figsize=(8, 6))
    colors = plt.get_cmap("tab10")
    cycle_num = 1
    damper_area_sum = 0

    for i in range(len(peak_indices) - 1):
        idx1 = peak_indices[i]
        idx2 = peak_indices[i + 1]

        d1 = disp[idx1]
        d2 = disp[idx2]
        t1 = time[idx1]
        t2 = time[idx2]

        if np.sign(d1) == np.sign(d2):
            continue

        delta_disp = abs(d2 - d1)
        area = delta_disp * 2 * FORCE_KN
        damper_area_sum += area

        cycle_energy_data.append({
            "Damper": col,
            "Cycle": cycle_num,
            "Start Time (s)": t1,
            "End Time (s)": t2,
            "Displacement Start (mm)": d1,
            "Displacement End (mm)": d2,
            "Area (kN·mm)": area
        })

        color = colors((cycle_num - 1) % 10)
        y_top = FORCE_KN if d1 > 0 else -FORCE_KN
        y_bottom = -y_top

        # Rectangle loop
        plt.plot([d1, d2], [y_top, y_top], color=color, linewidth=2, label=f"Cycle {cycle_num}")
        plt.plot([d2, d2], [y_top, y_bottom], color=color, linewidth=2)
        plt.plot([d2, d1], [y_bottom, y_bottom], color=color, linewidth=2)
        plt.plot([d1, d1], [y_bottom, y_top], color=color, linewidth=2)

        # Annotate times
        plt.text(d1 - 0.5, (y_bottom + y_top) / 2, f"{t1:.2f}s", fontsize=8,
                 ha="right", va="center", rotation=90, color=color)
        plt.text(d2 + 0.5, (y_bottom + y_top) / 2, f"{t2:.2f}s", fontsize=8,
                 ha="left", va="center", rotation=90, color=color)

        cycle_num += 1

    # === Bar Chart of Energy per Cycle (Smooth Look) ===
    cycle_df = pd.DataFrame([row for row in cycle_energy_data if row["Damper"] == col])
    
    plt.figure(figsize=(10, 4))
    bar_positions = np.arange(len(cycle_df))
    
    # Set edge colors: no edge for most, only for first/last bars
    edge_colors = ['black' if i == 0 or i == len(cycle_df) - 1 else 'none' for i in range(len(cycle_df))]
    
    bars = plt.bar(bar_positions,
                   cycle_df["Area (kN·mm)"],
                   width=1.0,
                   color="skyblue",
                   edgecolor=edge_colors)
    
    # Annotate times inside bars
    for bar, start, end in zip(bars, cycle_df["Start Time (s)"], cycle_df["End Time (s)"]):
        plt.text(bar.get_x() + bar.get_width() / 2,
                 bar.get_height() / 2,
                 f"{start:.1f}s\n→\n{end:.1f}s",
                 ha='center', va='center', fontsize=8, color="black")
    
    total_energy = cycle_df["Area (kN·mm)"].sum()
    plt.xlabel("Cycle Number")
    plt.ylabel("Dissipated Energy (kN·mm)")
    plt.title(f"Energy Dissipation per Cycle - {col}")
    plt.xticks(bar_positions, [f"{c}" for c in cycle_df["Cycle"]])
    plt.ylim(0, max(cycle_df["Area (kN·mm)"]) * 1.2)
    plt.text(len(bar_positions) - 0.5, max(cycle_df["Area (kN·mm)"]) * 1.1,
             f"Total: {total_energy:.1f} kN·mm", ha="right", fontsize=10, fontweight="bold")
    plt.grid(True, axis='y', linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.show()

# === Final Output ===
cycle_df = pd.DataFrame(cycle_energy_data)
print("\nSummary of all cycles:\n")
print(cycle_df)

summary = cycle_df.groupby("Damper")["Area (kN·mm)"].sum().reset_index()
summary.columns = ["Damper", "Total Energy (kN·mm)"]
print("\nTotal energy dissipated per damper:\n")
print(summary)
