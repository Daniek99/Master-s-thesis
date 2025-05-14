# -*- coding: utf-8 -*-
"""
Created on Thu May  8 17:20:32 2025

@author: Johan Linstad
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Mar 31 14:08:04 2025

@author: Johan Linstad
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Mar 27 20:06:28 2025

@author: Johan Linstad
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Mar 27 19:25:13 2025

@author: Johan Linstad
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
import os

from scipy.stats import lognorm
plt.rcParams.update({
    "font.size": 20,        # Øk font-størrelse på aksetitler, ticks osv.
    "axes.titlesize": 30,   # Tittel-størrelse
    "axes.labelsize": 30,   # Aksenes label-størrelse
    "legend.fontsize": 20,  # Legende-størrelse
    "xtick.labelsize": 30,  # X-ticks størrelse
    "ytick.labelsize": 30   # Y-ticks størrelse
})



# Høyde per etasje i mm
H = 2000  

# Liste med filbaner
file_paths = [
        "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240910_1649_Test07_T_CORR.xlsx",
        "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1543_Test17_T_CORR.xlsx",
        "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1838_Test23_T_CORR.xlsx",
        ]

file_paths = [
        "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240910_1723_Test10_T_CORR.xlsx",
        "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1604_Test19_T_CORR.xlsx",
        "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1853_Test24_T_CORR.xlsx",
        ]

file_paths = [
        "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240910_1822_Test13_T_CORR.xlsx",
        "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1644_Test21_T_CORR.xlsx",
        "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1915_Test25_T_CORR.xlsx",
        ]
#file_paths = [
    #"C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1513_Test14_T_CORR.xlsx",
    #C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1543_Test17_T_CORR.xlsx",
    #"C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1604_Test19_T_CORR.xlsx",
    #"C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1644_Test21_T_CORR.xlsx",
    #"C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1718_Test22_T_CORR.xlsx"
    #]


# file_paths = [
#     "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1838_Test23_T_CORR.xlsx",
#     "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1853_Test24_T_CORR.xlsx",
#     "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1915_Test25_T_CORR.xlsx",
#     "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1941_Test26_T_CORR.xlsx",
#     ]


# file_paths = [
#     "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1644_Test21_T_CORR.xlsx",
#     "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1915_Test25_T_CORR.xlsx",
#     "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240910_1803_Test11_T_CORR.xlsx",
#     "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240910_1814_Test12_T_CORR.xlsx",
#     "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240910_1822_Test13_T_CORR.xlsx",
#     "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240910_1645_Test06_T_CORR.xlsx",
    
#     "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240910_1649_Test07_T_CORR.xlsx",
#     "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240910_1652_Test08_T_CORR.xlsx",
#     ]





# Damage state grenser (interstory drift i % og akselerasjon i g)
drift_ds_bounds = [0.0, 0.5, 1.0, 2.0, 3.5]
acc_ds_bounds = [0.0, 0.25, 0.5, 1.0, 2.5]
colors = ['green', 'yellow', 'orange', 'red']

drift_data = {}
acc_data = {}

# Hent data for hver fil
for file_path in file_paths:
    df = pd.read_excel(file_path)
    # Henter testnummer fra filnavnet
    test_number_raw = file_path.split("Test")[1].split("_")[0]
    test_number1 = "Test " + test_number_raw
    test_number2 = "Test" + test_number_raw
    
    
    
    
    # Earthquake intensity lookup
    test_intensity_lookup = {
        "Test02": 0.04, "Test03": 0.09, "Test04": 0.09, "Test05": 0.09, "Test06": 0.18,
        "Test07": 0.18, "Test08": 0.18, "Test09": 0.27, "Test10": 0.27, "Test11": 0.36,
        "Test12": 0.36, "Test13": 0.36, "Test14": 0.09, "Test15": 0.18, "Test16": 0.18,
        "Test17": 0.18, "Test18": 0.27, "Test19": 0.27, "Test20": 0.27, "Test21": 0.36,
        "Test22": 0.45, "Test23": 0.18, "Test24": 0.27, "Test25": 0.36, "Test26": 0.45,
        "Test27": 0.18, "Test28": 0.18
        }
    intensity_g = test_intensity_lookup.get(test_number2, None)
    test_number = test_number1 + " " + f"({intensity_g:.2f} g)" if intensity_g is not None else test_number1


    # Displacement-kolonner (kun X-retning)
    disp_columns_x = [col for col in df.columns if col.startswith("Disp") and col.endswith("_X")]
    acc_cols = [col for col in df.columns if col.startswith("Acc") and "_X" in col]
    
    # --- NY KODE: Sensordrop for enkelte tester ---
    sensors_to_remove = {
        "04": ["Disp06", "Disp07"],
        "11": ["Disp06", "Disp07"], 
        "15": ["Disp06", "Disp07"],
        "16": ["Disp06", "Disp07"],
        "18": ["Disp06", "Disp07"],
        "20": ["Disp06", "Disp07"],
        "21": ["Disp04", "Disp05"],
        "22": ["Disp06", "Disp07"], 
        "25": ["Disp09", "Disp08"],
        "26": ["Disp09", "Disp08"],
        "27": ["Disp14", "Disp18"]
        }
        # Legg til flere tester og sensorer her hvis nødvendig
       


    # Fjern sensorer som skal ekskluderes for gjeldende test
    if test_number_raw in sensors_to_remove:
        sensors_to_exclude = sensors_to_remove[test_number_raw]
        disp_columns_x = [col for col in disp_columns_x if not any(excl in col for excl in sensors_to_exclude)]
    
    excluded_text = ""
    if test_number_raw in sensors_to_remove:
        sensors_to_exclude = sensors_to_remove[test_number_raw]
        excluded_text = f"Sensors excluded for {test_number}:\n" + ", ".join(sensors_to_exclude)

    
    # Fjern sensorer fra listen over X-displacement-sensorer
    #sensorer_å_utelate = ["Disp04_NE_1F_Y", "Disp05_NE_1F_X"]
    #disp_columns_x = [col for col in disp_columns_x if col not in sensorer_å_utelate]

    ground_sensor_x = "PosA1T"
    df_disp = df[["Time (s)"] + disp_columns_x + [ground_sensor_x]].copy()
    df_disp = df_disp[(df_disp["Time (s)"] >= 5) & (df_disp["Time (s)"] <= 30)].reset_index(drop=True)

    #%%
    max_displacements = df[disp_columns_x].abs().max().sort_values(ascending=False)


    plt.figure(figsize=(10, 6))
    max_displacements.plot(kind='bar')
    plt.title(f"{test_number} - Max Absolute Displacement per X-Sensor unfiltered")
    plt.ylabel("Max Displacement (mm)")
    plt.xticks(rotation=45, ha='right')
    plt.grid(True)
    for i, value in enumerate(max_displacements):
        plt.text(i, value, f"{value:.1f} mm", ha='center', va='bottom', fontsize=9, fontweight='bold')
    plt.gcf().text(0.8, 0.3, excluded_text, fontsize=9, color="red", ha="center", va="top", bbox=dict(facecolor='white', alpha=0.6, edgecolor='red'))
    plt.tight_layout()
    plot_name = f"{test_number}_MaxDisplacement_X_unfiltered.png"
    #plt.savefig(os.path.join(save_folder, plot_name))
    plt.show()
    plt.close()


    #%%
    # desired_acc_sensors = [
    #     "Acc07_1F_NE_X", "Acc08_1F_NE_Y",
    #     "Acc09_1F_SW_X", "Acc10_1F_SW_Y",
    #     "Acc11_2F_NE_X", "Acc12_2F_NE_Y",
    #     "Acc13_2F_SW_X", "Acc14_2F_SW_Y"
    # ]
    
    # # Sjekk hvilke som finnes
    # existing_sensors = [col for col in desired_acc_sensors if col in df.columns]
    existing_sensors = [col for col in df.columns if col.startswith("Acc") and "_X" in col]
    
    # Fjern sensorer med outliers
    outlier_threshold = 3000
    acc_columns = [col for col in existing_sensors if df[col].abs().max() <= outlier_threshold]
    
    # Eventuell advarsel
    # missing_cols = [col for col in desired_acc_sensors if col not in df.columns]
    # if missing_cols:
    #     print(f"⚠️ Manglende akselerometerkolonner i {test_number}: {missing_cols}")
  
    print(disp_columns_x)
        
    # Definerer bakkenivå-sensorer
    
    ground_sensor_y = "PosA2L"  # Y-retning
        

    # Kopierer relevante kolonner inkludert tid
    df_disp_x = df[["Time (s)"] + disp_columns_x + [ground_sensor_x]].copy()
    #df_disp = df[["Time (s)"] + disp_columns].copy()
    df_acc = df[["Time (s)"] + acc_columns].copy()

    # Trekker fra gjennomsnittet av de 5 første sekundene for å justere nullpunktet
    start_values = df_disp_x[df_disp_x["Time (s)"] <= 5].mean()
    df_disp_x.iloc[:, 1:] = df_disp_x.iloc[:, 1:] - start_values[1:]
    


    #%%
            
    # Velger sensorer for interstory drift
    ground_floor_sensors = ["PosA1T"]
    first_floor_sensors = [col for col in disp_columns_x if "_1F" in col]
    second_floor_sensors = [col for col in disp_columns_x if "_2F" in col]
        
    ground_floor_sensors.sort()
    first_floor_sensors.sort()
    second_floor_sensors.sort()
        
        

    
        
    # Liste over sensorer som må inverteres
    inverted_sensors = ["Disp12_NE_1F_X", "Disp16_NE_2F_X"]
    #inverted_sensors = ["Disp09_NE_2F_X", "Disp05_NE_1F_X"]
    # Inverterer verdiene for sensorene i listen
    for sensor in inverted_sensors:
            if sensor in df_disp_x.columns:
                df_disp_x[sensor] = -df_disp_x[sensor]  # Endrer fortegnet
                
    # Filtrer tidsområdet mellom 5 og 30 sekunder
    df_disp = df_disp_x[(df_disp_x["Time (s)"] >= 5) & (df_disp_x["Time (s)"] <= 30)].reset_index(drop=True)
        
        
    # Justerer displacement for bakkenivå
    for col in disp_columns_x:
        if col.endswith("_X"):  # X-retning
                df_disp[col] =  df_disp_x[col] - df_disp_x[ground_sensor_x]
            #elif col.endswith("_Y"):  # Y-retning
                #df_disp[col] =  df_disp[col] - df_disp[ground_sensor_y]
       
                
    
        
    #%% Etter justering for bakkenivå:
    max_displacements1 = df_disp[disp_columns_x].abs().max().sort_values(ascending=False)
    
    plt.figure(figsize=(10, 6))
    max_displacements1.plot(kind='bar')
    plt.title(f"{test_number} - Max Absolute Displacement per X-Sensor (Ground Adjusted)")
    plt.ylabel("Max Displacement (mm)")
    plt.xticks(rotation=45, ha='right')
    plt.grid(True)
    for i, value in enumerate(max_displacements1):
            plt.text(i, value, f"{value:.1f} mm", ha='center', va='bottom', fontsize=9, fontweight='bold')
    plt.gcf().text(0.8, 0.3, excluded_text, fontsize=9, color="red", ha="center", va="top", bbox=dict(facecolor='white', alpha=0.6, edgecolor='red'))
    plt.tight_layout()
    plot_name = f"{test_number}_MaxDisplacement_X_filtered.png"
    #plt.savefig(os.path.join(save_folder, plot_name))
    plt.show()
    plt.close()
    #%%
    first_floor_sensors = [col for col in df_disp.columns if "_1F" in col]
    second_floor_sensors = [col for col in df_disp.columns if "_2F" in col]
    drift_vals = []

    for i in range(min(len(first_floor_sensors), len(second_floor_sensors))):
        drift_0_1 = (df_disp[first_floor_sensors[i]]).abs().max() / H * 100
        drift_2_1 = (df_disp[second_floor_sensors[i]] - df_disp[first_floor_sensors[i]]).abs().max() / H * 100
        drift_vals.extend([drift_0_1, drift_2_1])

    drift_data[test_number] = np.sort(drift_vals)

    # Akselerasjon
    
    df_acc = df_acc[(df_acc["Time (s)"] >= 5) & (df_acc["Time (s)"] <= 30)].reset_index(drop=True)
    acc_vals = []

    for col in acc_columns:
        if ("1F" in col or "2F" in col):
            val = df_acc[col].abs().max()
            if val < 3000:
                acc_vals.append(val / 981)  # cm/s² -> g

    acc_data[test_number] = np.sort(acc_vals)
    
    print (acc_vals)
#%%
# Plot akselerometerdata over tid for én test
plt.figure(figsize=(14, 6))
for col in acc_columns:
    plt.plot(df_acc["Time (s)"], df_acc[col], label=col, linewidth=1)

plt.title(f"{test_number} – Acceleration Over Time (All Accelerometers)")
plt.xlabel("Time [s]")
plt.ylabel("Acceleration [cm/s²]")
plt.grid(True)
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
plt.tight_layout()
plt.show()



# Plotter alle testene i én figur
fig, axs = plt.subplots(1, 2, figsize=(16, 5), sharey=True)



# --- Drift ---
for test, values in drift_data.items():
    if len(values) > 0:
        cdf = np.arange(1, len(values)+1) / len(values)
        axs[0].step(values, cdf, where="post", label=test)

for i in range(len(drift_ds_bounds)-1):
    axs[0].axvspan(drift_ds_bounds[i], drift_ds_bounds[i+1], color=colors[i], alpha=0.2)

axs[0].set_title("Inter-story drift (all tests)")
axs[0].set_xlabel("Max inter-story drift [%]")
axs[0].set_ylabel("CDF")
axs[0].legend()
axs[0].grid(True)
axs[0].set_xlim(0, 3.5)
axs[0].set_ylim(0, 1.05)

# --- Akselerasjon ---
for test, values in acc_data.items():
    if len(values) > 0:
        cdf = np.arange(1, len(values)+1) / len(values)
        axs[1].step(values, cdf, where="post", label=test, linestyle='--')

for i in range(len(acc_ds_bounds)-1):
    axs[1].axvspan(acc_ds_bounds[i], acc_ds_bounds[i+1], color=colors[i], alpha=0.2)

axs[1].set_title("Acceleration (all tests)")
axs[1].set_xlabel("Max acceleration [g]")
axs[1].grid(True)
axs[1].set_xlim(0, 2)
axs[1].set_ylim(0, 1.05)
plt.gcf().text(0.8, 0.3, excluded_text, fontsize=9, color="red", ha="center", va="top", bbox=dict(facecolor='white', alpha=0.6, edgecolor='red'))
plt.tight_layout()
plt.show()



# def plot_lognormal_fragility_curves_combined(values_dict, thresholds, labels, title, xlabel):
#     fig, ax = plt.subplots(figsize=(12, 6))
#     colors = ['green', 'yellow', 'orange', 'red']

#     # Fargelag bakgrunn for skadegrenser
#     for i in range(len(thresholds) - 1):
#         ax.axvspan(thresholds[i], thresholds[i + 1], color=colors[i], alpha=0.3, label=labels[i])

    

#     # Plot alle tester
#     for test_name, values in values_dict.items():
#         values = np.array(values)
#         if len(values) < 2 or np.any(values <= 0):
#             continue

#         # Empirisk CDF (trapp)
#         sorted_vals = np.sort(values)
#         cdf = np.arange(1, len(sorted_vals) + 1) / len(sorted_vals)
#         ax.step(sorted_vals, cdf, where="post", linestyle='--', linewidth=1.5, label=f"{test_name} – CDF")

#         # Lognormal kurve
#         log_vals = np.log(values)
#         mu = np.mean(log_vals)
#         beta = np.std(log_vals)

#         x_vals = np.linspace(min(values)*0.8, max(values)*1.5, 300)
#         lognorm_cdf = norm.cdf((np.log(x_vals) - mu) / beta)
#         ax.plot(x_vals, lognorm_cdf, linewidth=2, label=f"{test_name} – Fit")

#     ax.set_xlim(0, max(thresholds))
#     ax.set_ylim(0, 1.05)
#     ax.set_xlabel(xlabel, fontsize=20)
#     ax.set_ylabel("Probability of exceedance", fontsize=18)
#     ax.set_title(title, fontsize=20)
#     ax.tick_params(axis='both', labelsize=20)  # Du kan justere '12' til ønsket størrelse
#     ax.grid(True)
#     ax.legend(loc="lower right", fontsize=14)
#     plt.gcf().text(0.8, 0.75, excluded_text, fontsize=16, color="red", ha="center", va="top", bbox=dict(facecolor='white', alpha=0.6, edgecolor='red'))
#     plt.tight_layout()
#     return fig

def plot_lognormal_fragility_curves_combined(values_dict, thresholds, labels, title, xlabel):
    fig, ax = plt.subplots(figsize=(12, 6))
    colors = ['green', 'yellow', 'orange', 'red']

    # Bakgrunn med skadegrenser
    for i in range(len(thresholds) - 1):
        ax.axvspan(thresholds[i], thresholds[i + 1], color=colors[i], alpha=0.3, label=labels[i])

    # Plot hver test
    for test_name, values in values_dict.items():
        values = np.array(values)
        values = values[values > 0]  # Fjern null/negative verdier (lognorm krever >0)
        if len(values) < 2:
            continue

        # Empirisk CDF
        sorted_vals = np.sort(values)
        cdf = np.arange(1, len(sorted_vals) + 1) / len(sorted_vals)
        ax.step(sorted_vals, cdf, where="post", linestyle='--', linewidth=1.5,
                label=f"{test_name} – CDF (n={len(values)})")

        # Lognormal fit via MLE
        shape, loc, scale = lognorm.fit(values, floc=0)
        x_vals = np.linspace(min(values)*0.8, max(values)*1.5, 1000)
        lognorm_cdf = lognorm.cdf(x_vals, shape, loc=loc, scale=scale)
        ax.plot(x_vals, lognorm_cdf, linewidth=2, label=f"{test_name} – Fit")

    # Plotoppsett
    ax.set_xlim(0, max(thresholds))
    ax.set_ylim(0, 1.05)
    ax.set_xlabel(xlabel, fontsize=20)
    ax.set_ylabel("CDF", fontsize=18)
    ax.set_title(title, fontsize=20)
    ax.tick_params(axis='both', labelsize=20)
    ax.grid(True)
    ax.legend(loc="lower right", fontsize=14)

    # Ekskluderte sensorer (hvis definert)
    try:
        plt.gcf().text(0.8, 0.75, excluded_text, fontsize=16, color="red", ha="center", va="top",
                        bbox=dict(facecolor='white', alpha=0.6, edgecolor='red'))
    except NameError:
        pass  # excluded_text ikke definert

    plt.tight_layout()
    return fig

#%%
# Legg denne delen helt nederst etter at drift_data og acc_data er fylt ut.
# Grenseverdier for drift og akselerasjon
drift_thresholds = [0, 0.5, 1.0, 2.0, 3.5]
acc_thresholds = [0, 0.25, 0.5, 1.0, 2.0]
ds_labels = ['Slight', 'Moderate', 'Extensive', 'Possible Collapse']

# # === Samle grupper for DRIFT og ACCELERASJON ===
# gruppe_1_navn = ["Test11", "Test12", "Test13"]
# gruppe_2_navn = ["Test13"]

# gruppe_1_drift = []
# gruppe_2_drift = []

# gruppe_1_acc = []
# gruppe_2_acc = []

# for testnavn, drift_vals in drift_data.items():
#     navn_renset = testnavn.replace(" ", "")
#     if any(g in navn_renset for g in gruppe_1_navn):
#         gruppe_1_drift.extend(drift_vals)
#     elif any(g in navn_renset for g in gruppe_2_navn):
#         gruppe_2_drift.extend(drift_vals)

# for testnavn, acc_vals in acc_data.items():
#     navn_renset = testnavn.replace(" ", "")
#     if any(g in navn_renset for g in gruppe_1_navn):
#         gruppe_1_acc.extend(acc_vals)
#     elif any(g in navn_renset for g in gruppe_2_navn):
#         gruppe_2_acc.extend(acc_vals)
# === Samle grupper for DRIFT og ACCELERASJON ===
gruppe_1_navn = ["Test06", "Test08"]
gruppe_2_navn = ["Test07"]

gruppe_1_drift = []
gruppe_2_drift = []

gruppe_1_acc = []
gruppe_2_acc = []

# Fyll gruppe 1 uten Test13
for testnavn, drift_vals in drift_data.items():
    navn_renset = testnavn.replace(" ", "")
    if any(g in navn_renset for g in gruppe_1_navn):
        gruppe_1_drift.extend(drift_vals)

for testnavn, acc_vals in acc_data.items():
    navn_renset = testnavn.replace(" ", "")
    if any(g in navn_renset for g in gruppe_1_navn):
        gruppe_1_acc.extend(acc_vals)

# Fyll gruppe 2 med kun Test13
for testnavn, drift_vals in drift_data.items():
    if "Test07" in testnavn.replace(" ", ""):
        gruppe_2_drift.extend(drift_vals)

for testnavn, acc_vals in acc_data.items():
    if "Test07" in testnavn.replace(" ", ""):
        gruppe_2_acc.extend(acc_vals)

# === Plot fragility for grupper ===
def plot_fragility_groups(grupper_dict, thresholds, labels, title, xlabel):
    fig, ax = plt.subplots(figsize=(12, 6))
    colors = ['green', 'yellow', 'orange', 'red']
    group_colors = ['blue', 'darkorange']  # Tilpass farger per gruppe

    # Skadegrenser
    for i in range(len(thresholds) - 1):
        ax.axvspan(thresholds[i], thresholds[i + 1], color=colors[i], alpha=0.2, label=labels[i])

    for i, (group_name, values) in enumerate(grupper_dict.items()):
        values = np.array(values)
        values = values[values > 0]
        if len(values) < 2:
            continue

        sorted_vals = np.sort(values)
        cdf = np.arange(1, len(sorted_vals)+1) / len(sorted_vals)
        ax.step(sorted_vals, cdf, where="post", linestyle='--', linewidth=1.5,
                label=f"{group_name} – CDF (n={len(values)})", color=group_colors[i])

        shape, loc, scale = lognorm.fit(values, floc=0)
        x_vals = np.linspace(min(values)*0.8, max(values)*1.5, 1000)
        lognorm_cdf = lognorm.cdf(x_vals, shape, loc=loc, scale=scale)
        ax.plot(x_vals, lognorm_cdf, linewidth=2, label=f"{group_name} – Fit", color=group_colors[i])

    ax.set_xlim(0, max(thresholds))
    ax.set_ylim(0, 1.05)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("CDF")
    ax.set_title(title)
    ax.grid(True)
    ax.legend(loc="lower right")
    plt.tight_layout()
    return fig

# === Plot begge fragilitetsplottene ===

# plot_fragility_groups(
#     {
#         "Merge": gruppe_1_drift,
#         "Test 13": gruppe_2_drift
#     },
#     drift_thresholds,
#     ds_labels,
#     "Fragility Comparison – Interstory Drift",
#     "Interstory drift [%]"
# )

# plot_fragility_groups(
#     {
#         "Lav intensitet": gruppe_1_acc,
#         "Høy intensitet": gruppe_2_acc
#     },
#     acc_thresholds,
#     ds_labels,
#     "Fragility Comparison – Acceleration",
#     "Acceleration [g]"
# )
# plot_fragility_groups(
#     {
#         "Test 06 + 07 + 08": gruppe_1_drift,
#         "Kun Test 07": gruppe_2_drift
#     },
#     drift_thresholds,
#     ds_labels,
#     "Fragility Comparison – Interstory Drift",
#     "Interstory drift [%]"
# )

# plot_fragility_groups(
#     {
#         "Test 06 + 07 + 08": gruppe_1_acc,
#         "Kun Test 07": gruppe_2_acc
#     },
#     acc_thresholds,
#     ds_labels,
#     "Fragility Comparison – Acceleration",
#     "Acceleration [g]"
# )


#%%

# Grenseverdier for drift og akselerasjon
drift_thresholds = [0, 0.5, 1.0, 2.0, 3.5]
acc_thresholds = [0, 0.25, 0.5, 1.0, 2.0]
ds_labels = ['Slight', 'Moderate', 'Extensive', 'Possible Collapse']

plot_lognormal_fragility_curves_combined(
    drift_data,
    drift_thresholds,
    ds_labels,
    "Lognormal Fragility Curves – Interstory Drift",
    "Interstory drift [%]"
)


plot_lognormal_fragility_curves_combined(
    acc_data,
    acc_thresholds,
    ds_labels,
    "Lognormal Fragility Curves – Acceleration",
    "Acceleration [g]"
)


