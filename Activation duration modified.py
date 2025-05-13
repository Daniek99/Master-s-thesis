import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# === Load Excel ===
file_path = r"C:\Users\danie\Documents\Master\Numerisk analyse\Tester\Config1Disp[1]\ACQ_20240910_1822_Test13_T_CORR.xlsx"
xls = pd.ExcelFile(file_path)
df = pd.read_excel(xls, sheet_name=xls.sheet_names[0])


# === Settings ===
THRESHOLD = 0.4
time_series = df["Time (s)"]
accel_series = df["accT"] / 1000  # mg to g

disp_columns = [col for col in df.columns if col.startswith("Disp[1]")]
disp2_columns = [col for col in df.columns if col.startswith("Disp[2]")]


# Normalize Disp[2] to t=0
df_disp2_normalized = pd.DataFrame()
for col in disp2_columns:
    df_disp2_normalized[col] = df[col] - df[col].iloc[0]

# Adjust Disp[1]
df_adjusted = df.copy()
valid_disp_columns = []
for col1 in disp_columns:
    suffix = col1.split("Disp[1]")[-1]
    col2 = f"Disp[2]{suffix}"
    if col2 in df_disp2_normalized.columns:
        df_adjusted[col1] = df[col1] - df_disp2_normalized[col2]
    normalized = df_adjusted[col1] - df_adjusted[col1].iloc[0]
    deviation_from_start = normalized - normalized.iloc[0]
    if deviation_from_start.max() >= THRESHOLD or deviation_from_start.min() <= -THRESHOLD:
        df_adjusted[col1] = normalized
        valid_disp_columns.append(col1)

valid_disp_columns.sort(key=lambda col: (col.endswith("2F"), col))
num_plots = len(valid_disp_columns)
fig, axes = plt.subplots(num_plots, 1, figsize=(12, 3 * num_plots), sharex=True)
if num_plots == 1:
    axes = [axes]

plt.suptitle("Test13 - L'Aquila 0.36 g\nRelative displacement: Top component of Friction Damper and RC frame",
             fontsize=14, fontweight="bold")

dt = np.diff(time_series).mean()
window_length = int(3.0 / dt)

for i, col in enumerate(valid_disp_columns):
    ax_disp = axes[i]
    series = df_adjusted[col]
    start_val = series.iloc[0]
    above_thresh = (series >= start_val + THRESHOLD) | (series <= start_val - THRESHOLD)
    if not above_thresh.any():
        ax_disp.plot(time_series, series, label=col, color="red")
        continue

    activation_idx = above_thresh.idxmax()
    t_activation = time_series[activation_idx]

    try:
        target_val = series[time_series >= 50].iloc[0]
    except IndexError:
        target_val = series.iloc[-1]
    lower_bound = target_val - THRESHOLD
    upper_bound = target_val + THRESHOLD
    post_activation = series[activation_idx:]
    within_bounds = (post_activation >= lower_bound) & (post_activation <= upper_bound)

    deactivation_idx = None
    for start in range(len(within_bounds) - window_length):
        if within_bounds.iloc[start:start + window_length].all():
            deactivation_idx = within_bounds.index[start]
            break

    if deactivation_idx:
        t_deactivation = time_series[deactivation_idx]
        active_mask = (time_series >= t_activation) & (time_series <= t_deactivation)
    else:
        active_mask = (time_series >= t_activation)

    # Plot active/inactive segments
    t = time_series.to_numpy()
    y = series.to_numpy()
    active = active_mask.to_numpy()
    segments = []
    current_color = "red" if not active[0] else "blue"
    seg_start = 0
    for j in range(1, len(active)):
        if active[j] != active[j - 1]:
            segments.append((t[seg_start:j], y[seg_start:j], current_color))
            seg_start = j
            current_color = "blue" if active[j] else "red"
    segments.append((t[seg_start:], y[seg_start:], current_color))
    for seg_t, seg_y, color in segments:
        ax_disp.plot(seg_t, seg_y, color=color, linewidth=1.8)

    # Max/min annotations
    max_idx = series.idxmax()
    min_idx = series.idxmin()
    max_time, max_val = time_series[max_idx], series[max_idx]
    min_time, min_val = time_series[min_idx], series[min_idx]
    ax_disp.plot(max_time, max_val, 'o', label="Max disp", color="orange")
    ax_disp.annotate(f"t = {max_time:.1f}s\n{max_val:.1f} mm", xy=(max_time, max_val),
                     xytext=(max_time + 0.5, max_val + 2), fontsize=8,
                     arrowprops=dict(arrowstyle="->", color="red"))
    ax_disp.plot(min_time, min_val, 'o', label="Min disp", color="green")
    ax_disp.annotate(f"t = {min_time:.1f}s\n{min_val:.1f} mm", xy=(min_time, min_val),
                     xytext=(min_time + 0.5, min_val - 2), fontsize=8,
                     arrowprops=dict(arrowstyle="->", color="blue"))

    ax_disp.set_ylabel("Disp (mm)")
    ax_disp.set_ylim(-25, 25)
    ax_disp.set_title(col)
    ax_disp.grid(True)
    ax_disp.legend(loc="upper left")

    # Acceleration overlay
    ax_accel = ax_disp.twinx()
    ax_accel.plot(time_series, accel_series, color="gray", alpha=0.3, label="Acceleration (g)")
    ax_accel.set_ylabel("Accel (g)", color="gray")
    ax_accel.tick_params(axis='y', labelcolor="gray")
    ax_accel.legend(loc="upper right")

axes[-1].set_xlabel("Time (s)")
for ax in axes:
    ax.set_xticks(np.arange(0, 51, 5))

plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.show()
