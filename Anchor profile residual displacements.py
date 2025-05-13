# -*- coding: utf-8 -*-
"""
Created on Wed Apr  2 09:43:52 2025

This code plots the residual displacement of the anchor profiles in a single test,
measured from the initial test of the configuration to the current test whithin the same confifguration. 


@author: danie
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import re

# === Settings ===
data_folder = r"C:\Users\danie\Documents\Master\Numerisk analyse\Tester\Config3Disp[1]"
accel_file_path = r"C:\Users\danie\Documents\Master\Numerisk analyse\Tester\LAQUILA-IT.AVZ.00.HNN.D.IT-2009_LNEC3D.xlsx"
SAVE_PLOTS = False
SAVE_SUMMARIES = False
THRESHOLD = 0.3  # mm

# === File to Analyze ===
file_name = "ACQ_20240911_1941_Test26_T_CORR.xlsx"
file_path = os.path.join(data_folder, file_name)

# === Reference File for Normalization ===
reference_file = r"C:\Users\danie\Documents\Master\Numerisk analyse\Tester\Config1Disp[1]\ACQ_20240910_1547_Test02_T_CORR.xlsx"
ref_xls = pd.ExcelFile(reference_file)
ref_df = pd.read_excel(ref_xls, sheet_name=ref_xls.sheet_names[0])

# Extract test label
match = re.search(r"(Test\d+)", file_name)
test_label = match.group(1) if match else file_name

# Earthquake intensity lookup
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

# Get initial values of Disp[2] from reference
ref_initial_values = {
    col: ref_df.loc[0, col]
    for col in ref_df.columns if col.startswith("Disp[2]")
}

# Extract test label
match = re.search(r"(Test\d+)", file_name)
test_label = match.group(1) if match else file_name

# === Output folders ===
save_plot_folder = os.path.join(data_folder, "Disp2Residuals")
os.makedirs(save_plot_folder, exist_ok=True)

save_summary_folder = os.path.join(data_folder, "Disp2ResSummaries")
os.makedirs(save_summary_folder, exist_ok=True)



try:
    # Load test data
    xls = pd.ExcelFile(file_path)
    df = pd.read_excel(xls, sheet_name=xls.sheet_names[0])
    if "Time (s)" not in df.columns:
        raise ValueError("Missing 'Time (s)' column.")

    # Load acceleration data
    accel_df = pd.read_excel(accel_file_path)
    if "Time" in accel_df.columns:
        accel_df.rename(columns={"Time": "Time (s)"}, inplace=True)
    if "Time (s)" not in accel_df.columns:
        raise ValueError("Acceleration file missing 'Time (s)' column.")
    accel_col = next((col for col in accel_df.columns if "acc" in col.lower() and "cm/s" in col.lower()), None)
    if accel_col is None:
        raise ValueError("Acceleration column like 'Acc (cm/s²)' not found.")
    accel_interp = np.interp(df["Time (s)"], accel_df["Time (s)"], accel_df[accel_col])
    accel_series = pd.Series(accel_interp, index=df.index)

    # Select and normalize Disp[2] columns
    disp2_columns = [col for col in df.columns if col.startswith("Disp[2]")]
    df_disp2_normalized = pd.DataFrame()
    valid_columns = []

    for col in disp2_columns:
        ref_value = ref_initial_values.get(col, df[col].iloc[0])  # fallback if not found
        normalized = df[col] - ref_value
        if normalized.abs().max() >= THRESHOLD:  ##Hmm
            df_disp2_normalized[col] = normalized
            valid_columns.append(col)
        else:
            print(f"Skipped {col} — all values within ±{THRESHOLD} mm")

    time_series = df["Time (s)"]

    if not valid_columns:
        print("No valid Disp[2] columns found.")
        summary_df = pd.DataFrame(columns=["Damper", "Max Displacement (mm)", "Residual Displacement (mm)"])
    else:
        max_displacements = []
        residual_displacements = []

        for col in valid_columns:
            max_disp = df_disp2_normalized[col].abs().max()
            residual = df_disp2_normalized[col].iloc[-1]
            max_displacements.append(max_disp)
            residual_displacements.append(residual)

        summary_df = pd.DataFrame({
            "Damper": valid_columns,
            "Max Displacement (mm)": max_displacements,
            "Residual Displacement (mm)": residual_displacements
        })

        print(f"\nSummary for {file_name}:\n", summary_df)

        if SAVE_SUMMARIES:
            summary_path = os.path.join(save_summary_folder, f"{test_label}_summary.csv")
            summary_df.to_csv(summary_path, index=False)

        # --- PLOT ---
        num_plots = len(valid_columns)
        fig, axes = plt.subplots(num_plots, 1, figsize=(12, 3 * num_plots), sharex=True)
        if num_plots == 1:
            axes = [axes]

        plt.suptitle(f"{test_label} - L'Aquila {intensity_label} \n"
                     f"Residual displacement of anchor profiles, relative to 1st config. test", fontsize=14, fontweight="bold")


        for i, col in enumerate(valid_columns):
            ax_disp = axes[i]
            ax_disp.plot(time_series, df_disp2_normalized[col], label=col)
            ax_disp.set_ylabel("Displacement (mm)")
            ax_disp.set_title(col)
            ax_disp.set_ylim(-4.5, 4.5)
            ax_disp.grid(True)
            ax_disp.legend(loc="upper left")
            # Add manual legend entry for the t=50s annotation
            from matplotlib.lines import Line2D
            custom_legend = [Line2D([0], [0], marker='o', color='w', label='t = 50s value',
                                    markerfacecolor='red', markersize=6)]
            ax_disp.legend(handles=ax_disp.get_legend_handles_labels()[0] + custom_legend,
                           loc="upper left")


            ax_accel = ax_disp.twinx()
            ax_accel.plot(time_series, accel_series, color="gray", alpha=0.3, label="Acceleration (cm/s²)")
            ax_accel.set_ylabel("Acceleration (cm/s²)", color="gray")
            ax_accel.tick_params(axis='y', labelcolor="gray")

            # Align y=0 visually
            disp_ylim = ax_disp.get_ylim()
            accel_min = accel_series.min()
            accel_max = accel_series.max()
            zero_pos = (0 - disp_ylim[0]) / (disp_ylim[1] - disp_ylim[0])
            accel_range = accel_max - accel_min
            upper = 0 + (1 - zero_pos) * accel_range
            lower = 0 - zero_pos * accel_range
            ax_accel.set_ylim(lower, upper)
            ax_accel.legend(loc="upper right")
            
            # Add annotation for displacement at t = 50s
            try:
                t_50_index = np.argmin(np.abs(time_series - 50))
                disp_at_50 = df_disp2_normalized[col].iloc[t_50_index]
                ax_disp.annotate(f"{disp_at_50:.2f} mm",
                                 xy=(50, disp_at_50),
                                 xytext=(48, disp_at_50 + 2),
                                 arrowprops=dict(arrowstyle="->", color="red"),
                                 fontsize=9, color="black")
            except Exception as ann_e:
                print(f"Annotation error in {col}: {ann_e}")

        axes[-1].set_xlabel("Time (s)")
        # Add x-axis ticks every 5 seconds up to t=50
        xticks = np.arange(0, 51, 5)
        for ax in axes:
            ax.set_xticks(xticks)
    
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])

        if SAVE_PLOTS:
            plot_filename = f"{test_label}_disp2_plot.png"
            save_path = os.path.join(save_plot_folder, plot_filename)
            plt.savefig(save_path)
            print(f"Saved plot to: {save_path}")

        plt.show()

except Exception as e:
    print(f"⚠️ Error processing {file_name}: {e}")

