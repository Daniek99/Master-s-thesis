# -*- coding: utf-8 -*-
"""
Created on Wed Apr  2 19:55:26 2025

This code plots the displacement as a function of time of each active damper for a single, selected test.
The values are normalized for t=0, and corrected for anchor profile movement (Disp[2])
Max/min values are annotated, and input acceleration is plotted in a faint gray in the background. 


@author: danie
"""
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import re

# === Settings ===
data_folder = r"C:\Users\danie\Documents\Master\Numerisk analyse\Tester\Config3Disp[1]"
#accel_file_path = r"C:\Users\danie\Documents\Master\Numerisk analyse\Tester\LAQUILA-IT.AVZ.00.HNN.D.IT-2009_LNEC3D.xlsx"
SAVE_PLOTS = False
SAVE_SUMMARIES = False
THRESHOLD = 0.4  # mm

# === File to Analyze ===
file_name = "ACQ_20240911_1941_Test26_T_CORR.xlsx"  
file_path = os.path.join(data_folder, file_name)
print(f"\nProcessing file: {file_name}")

# Extract "TestXX" from the file name
match = re.search(r"(Test\d+)", file_name)
test_label = match.group(1) if match else file_name

test_intensity_lookup = {
    "Test02": 0.04, "Test03": 0.09, "Test04": 0.09, "Test05": 0.09, "Test06": 0.18,
    "Test07": 0.18, "Test08": 0.18, "Test09": 0.27, "Test10": 0.27, "Test11": 0.36,
    "Test12": 0.36, "Test13": 0.36, "Test14": 0.09, "Test15": 0.18, "Test16": 0.18,
    "Test17": 0.18, "Test18": 0.27, "Test19": 0.27, "Test20": 0.27, "Test21": 0.36,
    "Test22": 0.45, "Test23": 0.18, "Test24": 0.27, "Test25": 0.36, "Test26": 0.45,
    "Test27": 0.18, "Test28": 0.18
}

intensity_g = test_intensity_lookup.get(test_label, None)
intensity_label = f"{intensity_g:.2f} g" if intensity_g is not None else test_label

# === Output folders ===
save_plot_folder = os.path.join(data_folder, "DisplacementPlots")
os.makedirs(save_plot_folder, exist_ok=True)

save_summary_folder = os.path.join(data_folder, "DisplacementSummaries")
os.makedirs(save_summary_folder, exist_ok=True)

try:
    # Load displacement file
    xls = pd.ExcelFile(file_path)
    df = pd.read_excel(xls, sheet_name=xls.sheet_names[0])
    if "Time (s)" not in df.columns:
        raise ValueError("Missing 'Time (s)' column.")

    # Use 'accT' from the same file and convert from mg to g
    if "accT" not in df.columns:
        raise ValueError("Acceleration column 'accT' not found in the file.")
    
    accel_series = df["accT"] / 1000  # Convert from mg to g

    # --- Displacement columns ---
    disp_columns = [col for col in df.columns if col.startswith("Disp[1]")]
    disp2_columns = [col for col in df.columns if col.startswith("Disp[2]")]
    if not disp_columns:
        raise ValueError("No 'Disp[1]' columns found.")

    # --- Normalize Disp[2] to its own t=0 value ---
    df_disp2_normalized = pd.DataFrame()
    for col in disp2_columns:
        df_disp2_normalized[col] = df[col] - df[col].iloc[0]

    # --- Subtract Disp[2] from Disp[1] ---
    for col1 in disp_columns:
        suffix = col1.split("Disp[1]")[-1]
        col2 = f"Disp[2]{suffix}"
        if col2 in df_disp2_normalized.columns:
            df[col1] = df[col1] - df_disp2_normalized[col2]
            print(f"Applied Disp[2] correction to {col1}")
        else:
            print(f"⚠️ No matching Disp[2] column found for {col1}")

    # --- Normalize Disp[1] to its own t=0 value ---
    df_adjusted = df.copy()
    valid_disp_columns = []
    for col in disp_columns:
        normalized = df[col] - df[col].iloc[0]
        deviation_from_start = normalized - normalized.iloc[0]
        if deviation_from_start.max() >= THRESHOLD or deviation_from_start.min() <= -THRESHOLD:
            df_adjusted[col] = normalized
            valid_disp_columns.append(col)
        else:
            print(f"Skipped {col} — no deviation beyond ±{THRESHOLD} mm from normalized start value")

    time_series = df["Time (s)"]

    if not valid_disp_columns:
        print("No valid displacement columns found.")
        summary_df = pd.DataFrame(columns=[
            "Damper", "Activation Time (s)", "Deactivation Time (s)",
            "Activation Duration (s)", "Max Displacement (mm)", "Residual Displacement (mm)"
        ])
    else:
        # --- ANALYSIS ---
        activation_times = []
        deactivation_times = []
        activation_durations = []
        max_displacements = []
        residual_displacements = []
        damper_ids = []

        # Sample interval
        time_diffs = np.diff(time_series)
        if not np.allclose(time_diffs, time_diffs[0], atol=1e-6):
            raise ValueError("Time steps are not uniform.")
        dt = time_diffs[0]
        window_length = int(3.0 / dt)  # 3 seconds

        for col in valid_disp_columns:
            series = df_adjusted[col]
            start_value = series.iloc[0]
            abs_series = series.abs()
            residual_disp = series.iloc[-1]

            # --- Activation ---
            above_thresh = (series >= start_value + THRESHOLD) | (series <= start_value - THRESHOLD)
            if not above_thresh.any():
                activation_times.append(np.nan)
                deactivation_times.append(np.nan)
                activation_durations.append(0)
                max_displacements.append(abs_series.max())
                residual_displacements.append(residual_disp)
                damper_ids.append(col)
                continue

            activation_idx = above_thresh.idxmax()
            t_activation = time_series[activation_idx]

            # --- Deactivation: signal stays within ±0.4 mm of value at t=50s for 3s ---
            try:
                target_value = series[time_series >= 50].iloc[0]
            except IndexError:
                print(f"⚠️ Not enough time data for t=50s in {col}.")
                target_value = series.iloc[-1]

            lower_bound = target_value - THRESHOLD
            upper_bound = target_value + THRESHOLD
            post_activation_series = series[activation_idx:]
            within_bounds = (post_activation_series >= lower_bound) & (post_activation_series <= upper_bound)

            deactivation_idx = np.nan
            for start in range(len(within_bounds) - window_length):
                if within_bounds.iloc[start:start + window_length].all():
                    deactivation_idx = within_bounds.index[start]
                    break

            if pd.notna(deactivation_idx):
                t_deactivation = time_series[deactivation_idx]
                duration = t_deactivation - t_activation
            else:
                t_deactivation = np.nan
                duration = 0

            damper_ids.append(col)
            activation_times.append(t_activation)
            deactivation_times.append(t_deactivation)
            activation_durations.append(duration)
            max_displacements.append(abs_series.max())
            residual_displacements.append(residual_disp)

        summary_df = pd.DataFrame({
            "Damper": damper_ids,
            "Activation Time (s)": activation_times,
            "Deactivation Time (s)": deactivation_times,
            "Activation Duration (s)": activation_durations,
            "Max Displacement (mm)": max_displacements,
            "Residual Displacement (mm)": residual_displacements
        })

        print(f"\nSummary for {file_name}:\n", summary_df)

        if SAVE_SUMMARIES:
            summary_path = os.path.join(save_summary_folder, f"{test_label}_summary.csv")
            summary_df.to_csv(summary_path, index=False)

        # --- INDIVIDUAL SUBPLOTS with Acceleration Overlay ---
        # Sort so that 1F comes before 2F
        valid_disp_columns.sort(key=lambda col: (col.endswith("2F"), col))
        num_plots = len(valid_disp_columns)
        fig, axes = plt.subplots(num_plots, 1, figsize=(12, 3 * num_plots), sharex=True)
        if num_plots == 1:
            axes = [axes]

        plt.suptitle(f"{test_label} - L'Aquila {intensity_label} \n Relative displacement: Top component of Friction Damper and RC frame", fontsize=14, fontweight="bold")

        for i, col in enumerate(valid_disp_columns):
            ax_disp = axes[i]
            ax_disp.plot(time_series, df_adjusted[col], label=col)
            # --- Mark and annotate max and min displacements ---
            series = df_adjusted[col]
            
            # Max
            max_idx = series.idxmax()
            max_time = time_series[max_idx]
            max_value = series[max_idx]
            ax_disp.plot(max_time, max_value, 'o', markersize=8, label="Max disp")
            ax_disp.annotate(f"t = {max_time:.1f}s\n{max_value:.1f} mm", xy=(max_time, max_value),
                              xytext=(max_time + 0.5, max_value + 2),
                              textcoords='data', fontsize=8,
                              arrowprops=dict(arrowstyle="->", color="red"))
            
            # Min
            min_idx = series.idxmin()
            min_time = time_series[min_idx]
            min_value = series[min_idx]
            ax_disp.plot(min_time, min_value, 'o', markersize=8, label="Min disp")
            ax_disp.annotate(f"t = {min_time:.1f}s\n{min_value:.1f} mm", xy=(min_time, min_value),
                              xytext=(min_time + 0.5, min_value - 2),
                              textcoords='data', fontsize=8,
                              arrowprops=dict(arrowstyle="->", color="blue"))
            
            ax_disp.set_ylabel("Displacement (mm)")
            ax_disp.set_title(col)
            ax_disp.set_ylim(-25, 25)
            ax_disp.legend(loc="upper left")
            ax_disp.grid(True)

            ax_accel = ax_disp.twinx()
            ax_accel.plot(time_series, accel_series, color="gray", alpha=0.3, label="Acceleration (g)")
            ax_accel.set_ylabel("Acceleration (g)", color="gray")
            ax_accel.tick_params(axis='y', labelcolor="gray")

            # Align y=0 visually on both axes
            disp_ylim = ax_disp.get_ylim()
            accel_min = accel_series.min()
            accel_max = accel_series.max()
            zero_pos_disp = (0 - disp_ylim[0]) / (disp_ylim[1] - disp_ylim[0])
            accel_range = accel_max - accel_min
            accel_center = 0
            upper = accel_center + (1 - zero_pos_disp) * accel_range
            lower = accel_center - zero_pos_disp * accel_range
            ax_accel.set_ylim(lower-0.1, upper+0.1)
            ax_accel.legend(loc="upper right")

        axes[-1].set_xlabel("Time (s)")
        # Optional: add ticks every 5s from 0 to 50
        xticks = np.arange(0, 51, 5)
        for ax in axes:
            ax.set_xticks(xticks)

        plt.tight_layout(rect=[0, 0.03, 1, 0.95])

        if SAVE_PLOTS:
            plot_filename = f"{test_label}_displacement_plot.png"
            save_path = os.path.join(save_plot_folder, plot_filename)
            plt.savefig(save_path)
            print(f"Saved plot to: {save_path}")

    # # --- COMBINED PLOTS BY FLOOR ---
    # first_floor_cols = [col for col in valid_disp_columns if col.endswith("1F")]
    # second_floor_cols = [col for col in valid_disp_columns if col.endswith("2F")]
    
    # # First floor
    # if first_floor_cols:
    #     plt.figure(figsize=(12, 6))
    #     for col in first_floor_cols:
    #         plt.plot(time_series, df_adjusted[col], label=col, alpha=0.6)
    #     plt.xlabel("Time (s)", fontsize=22)
    #     plt.ylabel("Displacement (mm)", fontsize=22)
    #     plt.title(f"{test_label} - L'Aquila {intensity_label} - 1st Floor dampers displacement vs time",
    #               fontsize=22, fontweight="bold")
    #     plt.xticks(fontsize=20)
    #     plt.yticks(fontsize=20)
    #     plt.ylim(-25, 25)
    #     plt.grid(True)
    #     plt.legend(loc='upper right', fontsize=20)
    #     plt.tight_layout()
    #     if SAVE_PLOTS:
    #         first_combined_filename = f"{test_label}_1F_combined_plot.png"
    #         first_combined_path = os.path.join(save_plot_folder, first_combined_filename)
    #         plt.savefig(first_combined_path)
    #         print(f"Saved 1st floor combined plot to: {first_combined_path}")
    #     plt.show()
    
    # # Second floor
    # if second_floor_cols:
    #     plt.figure(figsize=(12, 6))
    #     for col in second_floor_cols:
    #         plt.plot(time_series, df_adjusted[col], label=col, alpha=0.6)
    #     plt.xlabel("Time (s)", fontsize=22)
    #     plt.ylabel("Displacement (mm)", fontsize=22)
    #     plt.title(f"{test_label} - L'Aquila {intensity_label} - 2nd Floor dampers displacement vs time",
    #               fontsize=22, fontweight="bold")
    #     plt.xticks(fontsize=20)
    #     plt.yticks(fontsize=20)
    #     plt.ylim(-25, 25)
    #     plt.grid(True)
    #     plt.legend(loc='upper right', fontsize=20)
    #     plt.tight_layout()
    #     if SAVE_PLOTS:
    #         second_combined_filename = f"{test_label}_2F_combined_plot.png"
    #         second_combined_path = os.path.join(save_plot_folder, second_combined_filename)
    #         plt.savefig(second_combined_path)
    #         print(f"Saved 2nd floor combined plot to: {second_combined_path}")
    #     plt.show()


except Exception as e:
    print(f"⚠️ Error processing {file_name}: {e}")


