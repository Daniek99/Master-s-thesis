

#Plots and saves hysteresis diagrams for all active dampers per test, 
#plus a plot of energy dissipation over time per damper per test 
#plus total energy dissipated by damper and grand total

import os
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import matplotlib.patches as patches
from scipy.ndimage import gaussian_filter1d
from openpyxl import load_workbook



# === Settings ===
THRESHOLD = 0.4  # mm
FORCE_KN = 6
SMOOTHING_SIGMA = 2  # set to 0 to disable
SAVE_PLOTS = False

# === Test Intensity Lookup ===
test_intensity_lookup = {
    "Test02": 0.04, "Test03": 0.09, "Test04": 0.09, "Test05": 0.09, "Test06": 0.18,
    "Test07": 0.18, "Test08": 0.18, "Test09": 0.27, "Test10": 0.27, "Test11": 0.36,
    "Test12": 0.36, "Test13": 0.36, "Test14": 0.09, "Test15": 0.18, "Test16": 0.18,
    "Test17": 0.18, "Test18": 0.27, "Test19": 0.27, "Test20": 0.27, "Test21": 0.36,
    "Test22": 0.45, "Test23": 0.18, "Test24": 0.27, "Test25": 0.36, "Test26": 0.45,
    "Test27": 0.18, "Test28": 0.18
}

# === Input directory ===
data_folder = r"C:\Users\danie\Documents\Master\Numerisk analyse\Tester\Config3Disp[1]"
config_match = re.search(r"(Config\d+)", data_folder)
config_label = config_match.group(1) if config_match else "UnknownConfig"
save_folder = os.path.join(data_folder, "Damper hysteresis")
os.makedirs(save_folder, exist_ok=True)

# === Summary storage ===
summary_rows = []

combined_excel_path = os.path.join(save_folder, "CycleData_AllTests.xlsx")
writer = pd.ExcelWriter(combined_excel_path, engine='openpyxl')

summary_path = os.path.join(save_folder, "EnergySummary_SingleSheet.xlsx")

# Initialize file with header if not exists
if not os.path.exists(summary_path):
    df_header = pd.DataFrame(columns=["Test No", "Config", "PGA (g)", "Cum. Energy (J)"])
    df_header.to_excel(summary_path, sheet_name="Summary", index=False)

# === Loop through all Excel files ===
for file_name in os.listdir(data_folder):
    if not file_name.endswith(".xlsx") or "Test" not in file_name:
        continue

    print(f"\n🔄 Processing: {file_name}")
    file_path = os.path.join(data_folder, file_name)
    match = re.search(r"(Test\d+)", file_name)
    test_label = match.group(1) if match else "UnknownTest"
    intensity_g = test_intensity_lookup.get(test_label, None)
    intensity_label = f"{intensity_g:.2f} g" if intensity_g is not None else "Unknown"

    # Load data
    df = pd.read_excel(file_path)
    time_series = df["Time (s)"]

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

    # Compute cycles
    cycle_energy_data = []
    for col in valid_disp_columns:
        disp = df_adjusted[col].values
        if SMOOTHING_SIGMA > 0:
            disp = gaussian_filter1d(disp, sigma=SMOOTHING_SIGMA)
        time = time_series.values
        velocity = np.gradient(disp)
        sign_changes = np.diff(np.sign(velocity))
        peak_indices = np.where(sign_changes != 0)[0] + 1
        
        for i in range(len(peak_indices) - 1):
            idx1, idx2 = peak_indices[i], peak_indices[i + 1]
            t1, t2 = time[idx1], time[idx2]
            d1, d2 = disp[idx1], disp[idx2]
        
            # Define a valid cycle by amplitude and duration
            if abs(d2 - d1) < THRESHOLD:
                continue
            if t2 - t1 < 0.05:
                continue
        
            area = 2 * abs(d2 - d1) * 2 * FORCE_KN
            cycle_energy_data.append({
                "Damper": col,
                "Start Time (s)": t1,
                "End Time (s)": t2,
                "Displacement Start (mm)": d1,
                "Displacement End (mm)": d2,
                "Area (kN·mm)": area
            })


    # Summarize total energy
    cycle_df = pd.DataFrame(cycle_energy_data)
        # Only save non-empty cycle data
    if not cycle_df.empty:
        sheet_name = test_label  # e.g., "Test07"
        cycle_df.to_excel(writer, sheet_name=sheet_name, index=False)

    total_energy = cycle_df["Area (kN·mm)"].sum() if not cycle_df.empty else 0
    summary_row = pd.DataFrame([{
        "Test No": test_label,
        "Config": config_label,
        "PGA (g)": intensity_g,
        "Cum. Energy (J)": total_energy
    }])
    
    # Append row to existing Excel file
    with pd.ExcelWriter(summary_path, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
        startrow = writer.sheets["Summary"].max_row  # append after last row
        summary_row.to_excel(writer, sheet_name="Summary", index=False, header=False, startrow=startrow)



    # === Optional: Save plots ===
    if SAVE_PLOTS and not cycle_df.empty:
        # Color map
        unique_dampers = sorted(cycle_df["Damper"].unique())
        color_list = plt.cm.tab10(np.linspace(0, 1, len(unique_dampers)))
        color_map = dict(zip(unique_dampers, color_list))

        # Plot
        plt.figure(figsize=(12, 6))
        ax = plt.gca()
        legend_handles = []

        for damper, group in cycle_df.groupby("Damper"):
            group_sorted = group.sort_values("Start Time (s)")
            color = color_map[damper]
            for _, row in group_sorted.iterrows():
                start, end = row["Start Time (s)"], row["End Time (s)"]
                height = row["Area (kN·mm)"]
                width = end - start
                ax.add_patch(patches.Rectangle((start, 0), width, height,
                                               linewidth=0, facecolor=color, alpha=0.4))
            ax.plot(group_sorted["Start Time (s)"], group_sorted["Area (kN·mm)"],
                    color=color, linewidth=1.5, marker='o')
            legend_handles.append(patches.Patch(color=color, alpha=0.5,
                label=f"{damper} (Σ = {group_sorted['Area (kN·mm)'].sum():.0f} J)"))

        plt.text(0.98, 0.95, f"Total Energy: {total_energy:.0f} J",
                 transform=ax.transAxes, ha="right", va="top",
                 fontsize=11, fontweight="bold")

        plt.xlabel("Time (s)")
        plt.ylabel("Dissipated Energy per Cycle (J)")
        plt.title(f"{test_label} ({intensity_label}) - Energy Dissipation")
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.legend(handles=legend_handles, loc="center left", bbox_to_anchor=(1.02, 0.5), title="Damper + Energy")
        plt.tight_layout()

        save_path = os.path.join(save_folder, f"{test_label}_{intensity_label.replace(' ', '')}_EnergyDissipation.png")
        plt.savefig(save_path, dpi=300)
        # plt.show()
        print(f"✅ Saved: {save_path}")
        plt.close()

# === Save summary as Excel ===
summary_df = pd.DataFrame(summary_rows)
summary_path = os.path.join(save_folder, "EnergySummary.xlsx")
summary_df.to_excel(summary_path, index=True)
print(f"\n✅ Summary saved to: {summary_path}")
