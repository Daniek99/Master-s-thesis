# -*- coding: utf-8 -*-
"""
Created on Thu Apr 10 14:02:58 2025

@author: Johan Linstad
"""

"""
Created on Wed Feb 26 14:56:23 2025

@author: Johan Linstad
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os




def analyze_shaking_table_data(file_path):
    # Leser inn Excel-filen
    xls = pd.ExcelFile(file_path)
    df = pd.read_excel(xls, sheet_name=xls.sheet_names[0])
    
    # Henter testnummer fra filnavnet
    test_number_raw = file_path.split("Test")[1].split("_")[0]
    test_number1 = "Test " + test_number_raw
    test_number2 = "Test" + test_number_raw
    
    
    
    
    # Earthquake intensity lookup
    test_intensity_lookup = {
        "Test00": 0.04, "Test01": 0.04,
        "Test02": 0.04, "Test03": 0.09, "Test04": 0.09, "Test05": 0.09, "Test06": 0.18,
        "Test07": 0.18, "Test08": 0.18, "Test09": 0.27, "Test10": 0.27, "Test11": 0.36,
        "Test12": 0.36, "Test13": 0.36, "Test14": 0.09, "Test15": 0.18, "Test16": 0.18,
        "Test17": 0.18, "Test18": 0.27, "Test19": 0.27, "Test20": 0.27, "Test21": 0.36,
        "Test22": 0.45, "Test23": 0.18, "Test24": 0.27, "Test25": 0.36, "Test26": 0.45,
        "Test27": 0.18, "Test28": 0.18
        }
    intensity_g = test_intensity_lookup.get(test_number2, None)
    test_number = test_number1 + " " + f"({intensity_g:.2f} g)" if intensity_g is not None else test_number1

    
    
    
    # Lagre-mappe
    save_folder = os.path.join(os.path.dirname(file_path), "TAF 04.05", test_number)
    os.makedirs(save_folder, exist_ok=True)
    
    #Filtrerer ut displacement-sensorer (ekskluderer Disp[x])
    disp_columns_x = [col for col in df.columns if col.startswith("Disp") and not col.startswith("Disp[") and col.endswith("X")]
    disp_columns_y = [col for col in df.columns if col.startswith("Disp") and not col.startswith("Disp[") and col.endswith("Y")]
    
    #%%
    
    max_displacements = df[disp_columns_x].abs().max().sort_values(ascending=False)
    
   #%%


    plt.figure(figsize=(10, 6))
    max_displacements.plot(kind='bar')
    plt.title(f"{test_number} - Max Absolute Displacement per X-Sensor unfiltered")
    plt.ylabel("Max Displacement (mm)")
    plt.xticks(rotation=45, ha='right')
    plt.grid(True)
    for i, value in enumerate(max_displacements):
        plt.text(i, value, f"{value:.1f} mm", ha='center', va='bottom', fontsize=9, fontweight='bold')
    plt.tight_layout()
    plot_name = f"{test_number}_MaxDisplacement_X_unfiltered.png"
    plt.savefig(os.path.join(save_folder, plot_name))
    
    plt.show()
    plt.close()


#%%
    #disp_all = [col for col in df.columns if col.startswith("Disp")]
    acc_columns = [col for col in df.columns if col.startswith("Acc")]

    print(disp_columns_x)
    
    # Definerer bakkenivå-sensorer
    ground_sensor_x = "PosA1T"  # X-retning
    ground_sensor_y = "PosA2L"  # Y-retning
    
    
    
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


    # Kopierer relevante kolonner inkludert tid
    df_disp_x = df[["Time (s)"] + disp_columns_x + [ground_sensor_x]].copy()
    #df_disp = df[["Time (s)"] + disp_columns].copy()
    df_acc = df[["Time (s)"] + acc_columns].copy()

    # Trekker fra gjennomsnittet av de 5 første sekundene for å justere nullpunktet
    start_values = df_disp_x[df_disp_x["Time (s)"] <= 5].mean()
    df_disp_x.iloc[:, 1:] = df_disp_x.iloc[:, 1:] - start_values[1:]
    
    
    
    
    # Velger sensorer for interstory drift
    ground_floor_sensors = ["PosA1T"]
    first_floor_sensors = [col for col in disp_columns_x if "_1F" in col]
    second_floor_sensors = [col for col in disp_columns_x if "_2F" in col]
    
    ground_floor_sensors.sort()
    first_floor_sensors.sort()
    second_floor_sensors.sort()
    
    

    # Filtrer tidsområdet mellom 5 og 30 sekunder
    # df_disp = df_disp_x[(df_disp_x["Time (s)"] >= 5) & (df_disp_x["Time (s)"] <= 30)].reset_index(drop=True)
    mask_time = (df["Time (s)"] >= 5) & (df["Time (s)"] <= 30)
    df = df[mask_time].reset_index(drop=True)
    df_disp_x = df_disp_x[mask_time].reset_index(drop=True)
    df_acc = df_acc[mask_time].reset_index(drop=True)
    
    
    # Liste over sensorer som må inverteres
    inverted_sensors = ["Disp12_NE_1F_X", "Disp16_NE_2F_X", "Disp13_NE_1F_Y", "Disp15_SW_1F_Y"]
    #inverted_sensors = ["Disp09_NE_2F_X", "Disp05_NE_1F_X"]
    # Inverterer verdiene for sensorene i listen
    for sensor in inverted_sensors:
        if sensor in df_disp_x.columns:
            df_disp_x[sensor] = -df_disp_x[sensor]  # Endrer fortegnet
    
    
    
    
    df_disp = df_disp_x
    
    # Plotter displacement for alle sensorer delt opp etter etasje
    fig, axes = plt.subplots(3, 1, figsize=(12, 12), sharex=True)
    plt.suptitle(f"Shaking Table Test - {test_number}", fontsize=14, fontweight="bold")
    # Ground floor
    for sensor in ground_floor_sensors:
         axes[0].plot(df_disp["Time (s)"], df_disp[sensor], label=sensor)
    axes[0].set_title("Displacement - Ground Floor")
    axes[0].set_ylabel("Displacement (mm)")
    axes[0].legend()
    axes[0].grid(True)
     
    # First floor
    for sensor in first_floor_sensors:
        axes[1].plot(df_disp["Time (s)"], df_disp[sensor], label=sensor)
    axes[1].set_title("Displacement - First Floor")
    axes[1].set_ylabel("Displacement (mm)")
    axes[1].legend()
    axes[1].grid(True)
     
    # Second floor
    for sensor in second_floor_sensors:
        axes[2].plot(df_disp["Time (s)"], df_disp[sensor], label=sensor)
    axes[2].set_title("Displacement - Second Floor")
    axes[2].set_xlabel("Time (s)")
    axes[2].set_ylabel("Displacement (mm)")
    axes[2].legend()
    axes[2].grid(True)
     
    plt.tight_layout()
    plot_name = f"{test_number}_Displacement_X_unfiltrated.png"
    plt.gcf().text(0.8, 0.7, excluded_text, fontsize=9, color="red", ha="center", va="top", bbox=dict(facecolor='white', alpha=0.6, edgecolor='red'))

    plt.savefig(os.path.join(save_folder, plot_name))
    plt.show()
    plt.close()

    
    
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
    plt.tight_layout()
    plot_name = f"{test_number}_MaxDisplacement_X_filtered.png"
    plt.gcf().text(0.8, 0.9, excluded_text, fontsize=9, color="red", ha="center", va="top", bbox=dict(facecolor='white', alpha=0.6, edgecolor='red'))

    plt.savefig(os.path.join(save_folder, plot_name))
    plt.show()
    plt.close()

    
    
    
 #%%
    
   # Plotter displacement for alle sensorer delt opp etter etasje
    fig, axes = plt.subplots(2, 1, figsize=(12, 12), sharex=True)
    plt.suptitle(f"Displacement in Relation to Ground Movements - {test_number}", fontsize=14, fontweight="bold")
    
    
    # First floor
    for sensor in first_floor_sensors:
        axes[0].plot(df_disp["Time (s)"], df_disp[sensor], label=sensor)
    axes[0].set_title("Displacement - First Floor")
    axes[0].set_ylabel("Displacement (mm)")
    axes[0].legend()
    axes[0].grid(True)
    
    # Second floor
    for sensor in second_floor_sensors:
        axes[1].plot(df_disp["Time (s)"], df_disp[sensor], label=sensor)
    axes[1].set_title("Displacement - Second Floor")
    axes[1].set_xlabel("Time (s)")
    axes[1].set_ylabel("Displacement (mm)")
    axes[1].legend()
    axes[1].grid(True)
    
    plt.tight_layout()
    plot_name = f"{test_number}_Displacement_X_.png"
    plt.gcf().text(0.8, 0.65, excluded_text, fontsize=9, color="red", ha="center", va="top", bbox=dict(facecolor='white', alpha=0.6, edgecolor='red'))

    plt.savefig(os.path.join(save_folder, plot_name))
    plt.show()
    plt.close()

    
    # Endrer alle verdier i matrisen til absoluttverdier
    # df_disp[disp_columns] = df_disp[disp_columns].abs()
    
    # Beregner maksimal forskyvning og akselerasjon
    #Finner en maks verdi per sensor. I x retning er det 8 sensorer på prøven. 
    max_accelerations = df_acc[acc_columns].max()
    max_displacements = df_disp[disp_columns_x].max()
    sorted_displacements = np.sort(max_displacements)
    cdf_disp = np.arange(1, len(sorted_displacements) + 1) / len(sorted_displacements)
    
    # Beregner CDF for akselerasjon
    sorted_accelerations = np.sort(max_accelerations)
    cdf_acc = np.arange(1, len(sorted_accelerations) + 1) / len(sorted_accelerations)

    # Finne sensorene med størst displacement
    top_sensors = max_displacements.nlargest(2)
    print("Top 2 sensors with highest displacement:")
    print(top_sensors)
    
    # Plotter CDF av maksimal forskyvning
    plt.figure(figsize=(8, 5))
    plt.plot(sorted_displacements, cdf_disp, marker='o', linestyle='-', color='b', label='CDF')
    plt.xlabel("Max Displacement (mm)")
    plt.ylabel("CDF")
    plt.title(f"{test_number} - Cumulative Distribution Function of Max Displacement")
    plt.legend()
    plt.grid(True)
    plot_name = f"{test_number}_CDF_X_.png"
    plt.gcf().text(0.8, 0.3, excluded_text, fontsize=9, color="red", ha="center", va="top", bbox=dict(facecolor='white', alpha=0.6, edgecolor='red'))

    plt.savefig(os.path.join(save_folder, plot_name),bbox_inches="tight")
    plt.show()
    plt.close()

#%%

    # Beregner interstory drift mellom bakkenivå og 1. etasje
    df_disp_interstory_1F = df_disp[["Time (s)"]].copy()
    for sensor in first_floor_sensors:
        if sensor.endswith("_X"):
            drift_col = f"Drift_{sensor}_Ground_X"
            df_disp_interstory_1F[drift_col] = -df_disp[sensor] 
        elif sensor.endswith("_Y"):
            drift_col = f"Drift_{sensor}_Ground_Y"
            df_disp_interstory_1F[drift_col] = -df_disp[sensor] 
    
    sensor_pairs_2F_1F = [
    ("Disp09_NE_2F_X", "Disp05_NE_1F_X"),
    ("Disp11_SW_2F_X", "Disp07_SW_1F_X"),
    ("Disp16_NE_2F_X", "Disp12_NE_1F_X"),
    ("Disp18_SW_2F_X", "Disp14_SW_1F_X"),
    # legg til flere riktige par etter behov
]
        
    print("First floor sensor=",first_floor_sensors)
    print("second floor sensor=",second_floor_sensors)

    sensor_pairs_2F_1F = [
    ("Disp09_NE_2F_X", "Disp05_NE_1F_X"),
    ("Disp11_SW_2F_X", "Disp07_SW_1F_X"),
    ("Disp16_NE_2F_X", "Disp12_NE_1F_X"),
    ("Disp18_SW_2F_X", "Disp14_SW_1F_X"),
    # legg til flere riktige par etter behov
]


    df_disp_interstory_2F = df_disp[["Time (s)"]].copy()
    for second_sensor, first_sensor in sensor_pairs_2F_1F:
        if second_sensor in df_disp.columns and first_sensor in df_disp.columns:
            drift_col = f"Drift_{second_sensor}_{first_sensor}"
            df_disp_interstory_2F[drift_col] = df_disp[second_sensor] - df_disp[first_sensor]

        
    print("First floor SW:", [s for s in first_floor_sensors if "SW" in s])
    print("Second floor SW:", [s for s in second_floor_sensors if "SW" in s])

    print("First floor NE:", [s for s in first_floor_sensors if "NE" in s])
    print("Second floor NE:", [s for s in second_floor_sensors if "NE" in s])
    
    

    print("interstory drift 1st" , df_disp_interstory_1F.columns)
    print("interstory drift 2st" , df_disp_interstory_2F.columns)

#plotter interstory drift ground 1f 
    plt.figure(figsize=(14, 6)) 

    # Plot alle driftkurver
    for drift in df_disp_interstory_1F.columns[1:]:
        plt.plot(df_disp_interstory_1F["Time (s)"], df_disp_interstory_1F[drift], label=drift)

    # Finn drift-kolonnen med høyest absoluttverdi
    global_max_val = 0
    global_max_time = 0
    global_max_label = ""
    true_val = 0  # faktisk verdi (kan være negativ)

    for drift in df_disp_interstory_1F.columns[1:]:
        abs_series = df_disp_interstory_1F[drift].abs()
        local_max_index = abs_series.idxmax()
        local_max_val = abs_series.max()
        
        # ✅ Nå er denne IF inni løkka!
        if local_max_val > global_max_val:
            global_max_val = local_max_val
            global_max_time = df_disp_interstory_1F["Time (s)"][local_max_index]
            global_max_label = drift
            true_val = df_disp_interstory_1F[drift][local_max_index]

    # Marker kun det globale maksimumspunktet
    plt.plot(global_max_time, true_val, 'ro')
    x_offset = -1.0 
    y_offset = -1.0
    
    plt.text(global_max_time + x_offset, true_val + y_offset,
         f"{global_max_label}\n{true_val:.1f} mm\n@ {global_max_time:.2f}s",
         color='red', ha='right', va='center', fontsize=10)

    
    plt.xlabel("Time (s)")
    plt.ylabel("Interstory Drift (mm)")
    plt.title(f"{test_number} - Interstory Drift Between Ground Floor and 1st Floor Over Time")
    plt.legend()
    plt.grid(True)
    plot_name = f"{test_number}_ID1_X.png"
    plt.gcf().text(0.8, 0.2, excluded_text, fontsize=9, color="red", ha="center", va="top", bbox=dict(facecolor='white', alpha=0.6, edgecolor='red'))

    plt.savefig(os.path.join(save_folder, plot_name))
    plt.show()
    plt.close()


    
    # Plotter interstory drift mellom bakkenivå og 1. etasje
    plt.figure(figsize=(14, 6))
    for drift in df_disp_interstory_1F.columns[1:]:
        plt.plot(df_disp_interstory_1F["Time (s)"], df_disp_interstory_1F[drift], label=drift)
    
    plt.xlabel("Time (s)")
    plt.ylabel("Interstory Drift (mm)")
    plt.title(f"{test_number} - Interstory Drift Between Ground Floor and 1st Floor Over Time")
    plt.legend()
    plt.grid(True)
    plot_name = f"{test_number}_ID1_X1.png"
    plt.gcf().text(0.8, 0.2, excluded_text, fontsize=9, color="red", ha="center", va="top", bbox=dict(facecolor='white', alpha=0.6, edgecolor='red'))

    plt.savefig(os.path.join(save_folder, plot_name))
    plt.show()
    plt.close()

#%% --------- Interstory Drift: 1st Floor to 2nd Floor ---------
    plt.figure(figsize=(14, 6))
    for drift in df_disp_interstory_2F.columns[1:]:
        plt.plot(df_disp_interstory_2F["Time (s)"], df_disp_interstory_2F[drift], label=drift)

    # Finn drift med høyest absoluttverdi
    max_vals = {
        drift: df_disp_interstory_2F[drift].abs().max()
        for drift in df_disp_interstory_2F.columns[1:]
}

    max_drift_label = max(max_vals, key=max_vals.get)
    abs_series = df_disp_interstory_2F[max_drift_label].abs()
    local_max_index1 = abs_series.idxmax()
    true_val = df_disp_interstory_2F[max_drift_label][local_max_index1]
    global_max_time = df_disp_interstory_2F["Time (s)"][local_max_index1]

    plt.plot(global_max_time, true_val, 'ro')
    plt.text(global_max_time + 0.5, true_val,
         f"{max_drift_label}\n{true_val:.1f} mm\n@ {global_max_time:.2f}s",
         color='red', ha='left', va='center', fontsize=10)

    plt.xlabel("Time (s)")
    plt.ylabel("Interstory Drift (mm)")
    plt.title(f"{test_number} - Interstory Drift Between 1st Floor and 2nd Floor Over Time")
    plt.legend()
    plt.grid(True)
    plot_name = f"{test_number}_ID2_X.png"
    plt.gcf().text(0.8, 0.2, excluded_text, fontsize=9, color="red", ha="center", va="top", bbox=dict(facecolor='white', alpha=0.6, edgecolor='red'))

    plt.savefig(os.path.join(save_folder, plot_name))
    plt.show()
    plt.close()
    
    # Plotter interstory drift for 1. etasje og 2. etasje
    plt.figure(figsize=(14, 6))
    for drift in df_disp_interstory_2F.columns[1:]:
        plt.plot(df_disp_interstory_2F["Time (s)"], df_disp_interstory_2F[drift], label=drift)
    
    plt.xlabel("Time (s)")
    plt.ylabel("Interstory Drift (mm)")
    plt.title(f"{test_number} - Interstory Drift Between 1st Floor and 2nd Floor Over Time")
    plt.legend()
    plt.grid(True)
    plot_name = f"{test_number}_ID2_X2.png"
    plt.gcf().text(0.8, 0.2, excluded_text, fontsize=9, color="red", ha="center", va="top", bbox=dict(facecolor='white', alpha=0.6, edgecolor='red'))

    plt.savefig(os.path.join(save_folder, plot_name))
    plt.show()
    plt.close()
    
    #%% torsinal amplification factor 
    
    #trenger delta_avg for hver etasje, og delte_max 
    #1. etg 

    # Antall topper du vil analysere
    n_peaks = 3
    H = 2000  # mm etasjehøyde
    h0, h1, h2 = 0, 2, 4  # meter nivåer

    # Kolonner og gjennomsnitt
    drift_1f_cols = [col for col in df_disp_interstory_1F.columns if "Drift_" in col]
    drift_2f_cols = [col for col in df_disp_interstory_2F.columns if "Drift_" in col]
    drift_1F_mean = df_disp_interstory_1F[drift_1f_cols].abs().mean(axis=1)
    
    top_n_indices = drift_1F_mean.nlargest(n_peaks).index

    for i, idx in enumerate(top_n_indices):
        max_time = df_disp_interstory_1F["Time (s)"].iloc[idx]
        drift_1F_at_peak = df_disp_interstory_1F.iloc[idx]
        closest_idx_2F = df_disp_interstory_2F["Time (s)"].sub(max_time).abs().idxmin()
        drift_2F_at_peak = df_disp_interstory_2F.loc[closest_idx_2F]
        
        # SW og NE drift for begge etasjer
        drift_1F_SW = max([abs(drift_1F_at_peak[col]) for col in drift_1f_cols if "SW" in col])
        drift_1F_NE = max([abs(drift_1F_at_peak[col]) for col in drift_1f_cols if "NE" in col])
        drift_2F_SW = max([abs(drift_2F_at_peak[col]) for col in drift_2f_cols if "SW" in col])
        drift_2F_NE = max([abs(drift_2F_at_peak[col]) for col in drift_2f_cols if "NE" in col])
        
        
        
        
        # Konverter til prosent
        drift_1F_SW /= H
        drift_1F_NE /= H
        drift_2F_SW /= H
        drift_2F_NE /= H
        
        fig, ax = plt.subplots(figsize=(6, 6))
        
        # SW trapp
        ax.plot([drift_1F_SW * 100, drift_1F_SW * 100], [h0, h1], color='orange', marker='o')
        ax.plot([drift_1F_SW * 100, drift_2F_SW * 100], [h1, h1], color='orange', marker='o')
        ax.plot([drift_2F_SW * 100, drift_2F_SW * 100], [h1, h2], color='orange', marker='o', label="SW")
        
        # NE trapp
        ax.plot([drift_1F_NE * 100, drift_1F_NE * 100], [h0, h1], color='blue', marker='o')
        ax.plot([drift_1F_NE * 100, drift_2F_NE * 100], [h1, h1], color='blue', marker='o')
        ax.plot([drift_2F_NE * 100, drift_2F_NE * 100], [h1, h2], color='blue', marker='o', label="NE")
        
        # Annoteringer
        ax.text(drift_1F_SW * 100, 1.8, f"{drift_1F_SW * 100:.2f}%", color='orange', ha='right')
        ax.text(drift_2F_SW * 100, 3.8, f"{drift_2F_SW * 100:.2f}%", color='orange', ha='right')
        ax.text(drift_1F_NE * 100, 2.0, f"{drift_1F_NE * 100:.2f}%", color='blue', ha='left')
        ax.text(drift_2F_NE * 100, 4.0, f"{drift_2F_NE * 100:.2f}%", color='blue', ha='left')
        
        # Akser og stil
        ax.set_yticks([0, 2, 4])
        ax.set_yticklabels(["0 m", "2 m", "4 m"])
        ax.set_ylabel("Height [m]")
        ax.set_xlabel("Interstory Drift [%]")
        ax.set_xlim(0, 3.0)
        ax.set_title(f"{test_number} – Driftprofile at {max_time:.2f}s")
        ax.legend()
        ax.grid(True)
        
        
        
        # Lagre og vis
        plot_name = f"{test_number}_StairPlot_Peak_{i+1}_wTAF.png"
        plt.gcf().text(0.65, 0.65, excluded_text, fontsize=9, color="red", ha="center", va="top",
                       bbox=dict(facecolor='white', alpha=0.6, edgecolor='red'))
        plt.savefig(os.path.join(save_folder, plot_name), bbox_inches="tight")
        plt.show()
        plt.close()
        
    
    
    #%%    
    # Antall topper du vil analysere
    n_peaks = 3
    h0, h1, h2 = 0, 2000, 4000  # høyder i mm
    
    xlim = 60
    
    # Filtrer kun 1F- og 2F-sensorer
    disp_1F_cols = [col for col in df_disp.columns if "_1F" in col and col.endswith("_X")]
    disp_2F_cols = [col for col in df_disp.columns if "_2F" in col and col.endswith("_X")]
    
    # Beregn snitt-displacement i 1F for å finne toppene
    disp_1F_mean = df_disp[disp_1F_cols].abs().mean(axis=1)
    top_n_indices = disp_1F_mean.nlargest(n_peaks).index
    
    for i, idx in enumerate(top_n_indices):
        max_time = df_disp["Time (s)"].iloc[idx]
        disp_1F_at_peak = df_disp.iloc[idx]
        closest_idx_2F = df_disp["Time (s)"].sub(max_time).abs().idxmin()
        disp_2F_at_peak = df_disp.loc[closest_idx_2F]
    
        # SW og NE displacement på 1F og 2F
        disp_1F_SW = max([abs(disp_1F_at_peak[col]) for col in disp_1F_cols if "SW" in col])
        disp_1F_NE = max([abs(disp_1F_at_peak[col]) for col in disp_1F_cols if "NE" in col])
        disp_2F_SW = max([abs(disp_2F_at_peak[col]) for col in disp_2F_cols if "SW" in col])
        disp_2F_NE = max([abs(disp_2F_at_peak[col]) for col in disp_2F_cols if "NE" in col])
    
        # Interstory drift i mm
        drift_1F_SW = disp_1F_SW
        drift_1F_NE = disp_1F_NE
        drift_2F_SW = disp_2F_SW - disp_1F_SW
        drift_2F_NE = disp_2F_NE - disp_1F_NE
    
        # TAF for 1F og 2F
        avg_1F = (drift_1F_SW + drift_1F_NE) / 2
        max_1F = max(drift_1F_SW, drift_1F_NE)
        torsion_ratio_1F = (max_1F / ( avg_1F)) 
    
        avg_2F = (drift_2F_SW + drift_2F_NE) / 2
        max_2F = max(drift_2F_SW, drift_2F_NE)
        torsion_ratio_2F = (max_2F / (avg_2F))
        
    
        # Trappeplott
        fig, ax = plt.subplots(figsize=(6, 6))
    
        # SW
        ax.plot([drift_1F_SW, drift_1F_SW], [h0, h1], color='orange', marker='o')
        ax.plot([drift_1F_SW, drift_1F_SW + drift_2F_SW], [h1, h1], color='orange', marker='o')
        ax.plot([drift_1F_SW + drift_2F_SW, drift_1F_SW + drift_2F_SW], [h1, h2], color='orange', marker='o', label="SW")
    
        # NE
        ax.plot([drift_1F_NE, drift_1F_NE], [h0, h1], color='blue', marker='o')
        ax.plot([drift_1F_NE, drift_1F_NE + drift_2F_NE], [h1, h1], color='blue', marker='o')
        ax.plot([drift_1F_NE + drift_2F_NE, drift_1F_NE + drift_2F_NE], [h1, h2], color='blue', marker='o', label="NE")
    
        # Annoteringer
        ax.text(drift_1F_SW, 1800, f"{drift_1F_SW:.1f} mm", color='orange', ha='right')
        ax.text(drift_1F_SW + drift_2F_SW, 3800, f"{drift_2F_SW:.1f} mm", color='orange', ha='right')
        ax.text(drift_1F_NE, 2000, f"{drift_1F_NE:.1f} mm", color='blue', ha='left')
        ax.text(drift_1F_NE + drift_2F_NE, 4000, f"{drift_2F_NE:.1f} mm", color='blue', ha='left')
    
        # Oppsett
        ax.set_yticks([0, 2000, 4000])
        ax.set_yticklabels(["0 m", "2 m", "4 m"])
        ax.set_ylabel("Height [m]")
        ax.set_xlabel("Displacement [mm]")
        ax.set_xlim(0, xlim)
        ax.set_title(f"{test_number} – Displacement Profile at {max_time:.2f}s")
        ax.legend()
        ax.grid(True)
    
        # TAF-verdier
        ax.text(0.2, 0.80, 
        rf"$1st = \frac{{\max(\Delta SW, \Delta NE)}}{{\Delta avg}}$ = {torsion_ratio_1F:.2f}",
        transform=ax.transAxes,
        fontsize=12,
        ha='right',
        va='center',
        color='darkred' if torsion_ratio_1F > 1.2 else 'black')
        
        ax.text(0.2, 0.70, 
        rf"$2nd = \frac{{\max(\Delta_SW, \Delta_NE)}}{{\Delta avg}}$ = {torsion_ratio_2F:.2f}",
        transform=ax.transAxes,
        fontsize=12,
        ha='right',
        va='center',
        color='darkred' if torsion_ratio_2F > 1.2 else 'black')

    
        # Lagre
        plot_name = f"{test_number}_StairPlot_PeakDisp_{i+1}_TAFmm.png"
        plt.gcf().text(0.65, 0.75, excluded_text, fontsize=9, color="red", ha="center", va="top",
                       bbox=dict(facecolor='white', alpha=0.6, edgecolor='red'))
        plt.savefig(os.path.join(save_folder, plot_name), bbox_inches="tight")
        plt.show()
        plt.close()        
        return df_disp_interstory_1F, df_disp_interstory_2F, save_folder, test_number
    

#%%
import numpy as np
import pandas as pd
import os
from scipy.signal import find_peaks

def calculate_taf_with_theta(df_disp_interstory_1F, df_disp_interstory_2F, H, n_peaks, save_folder, test_number, L=4500, sampling_rate=50, freq_estimate=2.8):
    # Filtrer X-retning
    drift_1f_cols = [col for col in df_disp_interstory_1F.columns if "Ground_X" in col]
    drift_2f_cols = [col for col in df_disp_interstory_2F.columns if "_X" in col]

    drift_1F_mean = df_disp_interstory_1F[drift_1f_cols].abs().mean(axis=1)

    # Beregn antall punkter per bølgeperiode
    T = 1 / freq_estimate  # periode
    min_distance_points = int(T * sampling_rate)

    # Finn topper med min avstand mellom dem
    peaks, _ = find_peaks(drift_1F_mean, distance=min_distance_points)

    # Velg de høyeste toppene
    peak_values = drift_1F_mean.iloc[peaks]
    top_n_indices = peak_values.nlargest(n_peaks).index

    taf_theta_results = []

    for i, idx in enumerate(top_n_indices):
        peak_time = df_disp_interstory_1F["Time (s)"].iloc[idx]
        drift_1F_at_peak = df_disp_interstory_1F.iloc[idx]
        closest_idx_2F = df_disp_interstory_2F["Time (s)"].sub(peak_time).abs().idxmin()
        drift_2F_at_peak = df_disp_interstory_2F.iloc[closest_idx_2F]

        # 1F
        drift_1F_SW_mm = max([abs(drift_1F_at_peak[col]) for col in drift_1f_cols if "SW" in col])
        drift_1F_NE_mm = max([abs(drift_1F_at_peak[col]) for col in drift_1f_cols if "NE" in col])
        drift_1F_SW = drift_1F_SW_mm / H
        drift_1F_NE = drift_1F_NE_mm / H

        # 2F
        drift_2F_SW_mm = max([abs(drift_2F_at_peak[col]) for col in drift_2f_cols if "SW" in col])
        drift_2F_NE_mm = max([abs(drift_2F_at_peak[col]) for col in drift_2f_cols if "NE" in col])
        drift_2F_SW = drift_2F_SW_mm / H
        drift_2F_NE = drift_2F_NE_mm / H
        
        
    


        # TAF beregning
        avg_1F = (drift_1F_SW_mm + drift_1F_NE_mm) / 2
        max_1F = max(drift_1F_SW_mm, drift_1F_NE_mm)
        taf_1F = max_1F / avg_1F if avg_1F != 0 else np.nan

        avg_2F = (drift_2F_SW_mm + drift_2F_NE_mm) / 2
        max_2F = max(drift_2F_SW_mm, drift_2F_NE_mm)
        taf_2F = max_2F / avg_2F if avg_2F != 0 else np.nan
        
        if avg_1F < 5:
            taf_1F = 0
        if avg_2F < 5:
            taf_2F = 0


        # Theta for 1F
        delta_max_1F = max(drift_1F_SW_mm, drift_1F_NE_mm)
        delta_min_1F = min(drift_1F_SW_mm, drift_1F_NE_mm)
        theta_rad_1F = (delta_max_1F - delta_min_1F) / L
        theta_deg_1F = np.degrees(theta_rad_1F)

        # Theta for 2F
        delta_max_2F = max(drift_2F_SW_mm, drift_2F_NE_mm)
        delta_min_2F = min(drift_2F_SW_mm, drift_2F_NE_mm)
        theta_rad_2F = (delta_max_2F - delta_min_2F) / L
        theta_deg_2F = np.degrees(theta_rad_2F)

        taf_theta_results.append({
            "Test": test_number,
            "Peak Number": i + 1,
            "Time (s)": peak_time,
            "Disp_1F_SW (mm)": drift_1F_SW_mm,
            "Disp_1F_NE (mm)": drift_1F_NE_mm,
            "Disp_2F_SW (mm)": drift_2F_SW_mm,
            "Disp_2F_NE (mm)": drift_2F_NE_mm,
            "Drift_1F_SW (%)": drift_1F_SW * 100,
            "Drift_1F_NE (%)": drift_1F_NE * 100,
            "Drift_2F_SW (%)": drift_2F_SW * 100,
            "Drift_2F_NE (%)": drift_2F_NE * 100,
            "TAF 1F": taf_1F,
            "TAF 2F": taf_2F,
            "Theta_1F (radianer)": theta_rad_1F,
            "Theta_1F (grader)": theta_deg_1F,
            "Theta_2F (radianer)": theta_rad_2F,
            "Theta_2F (grader)": theta_deg_2F,
        })

    taf_theta_df = pd.DataFrame(taf_theta_results)
    os.makedirs(save_folder, exist_ok=True)
    taf_theta_df.to_excel(os.path.join(save_folder, f"{test_number}_TAF_theta_results_updated.xlsx"), index=False)

    return taf_theta_df

#%%



def run_all_tests_from_paths(file_paths, save_to_folder, H=2000, n_peaks=3, L=4500):
    if not file_paths:
        print("🚨 Ingen filbaner oppgitt.")
        return

    print(f"\U0001F4C2 Starter analyse av {len(file_paths)} testfiler...")

    all_taf_theta_dfs = []

    for file_path in file_paths:
        print(f"\U0001F50D Analyserer: {os.path.basename(file_path)}")

        # Fanger opp alt analyze_shaking_table_data returnerer
        df_disp_interstory_1F, df_disp_interstory_2F, save_folder_single, test_number = analyze_shaking_table_data(file_path)

        # Beregner TAF + theta
        taf_theta_df = calculate_taf_with_theta(
            df_disp_interstory_1F,
            df_disp_interstory_2F,
            H=H,
            n_peaks=n_peaks,
            save_folder=save_folder_single,
            test_number=test_number,
            L=L
        )

        all_taf_theta_dfs.append(taf_theta_df)

    # Samler alt til EN fil
    if all_taf_theta_dfs:
        final_df = pd.concat(all_taf_theta_dfs, ignore_index=True)
        os.makedirs(save_to_folder, exist_ok=True)
        final_save_path = os.path.join(save_to_folder, "All_TAF_theta_results.xlsx")
        final_df.to_excel(final_save_path, index=False)
        print(f"✅ Alle tester er analysert og samlet i: {final_save_path}")
    else:
        print("🚨 Ingen resultater ble generert!")

    return

# Eksempel på kall:
# run_all_tests_from_paths(file_paths, save_all_to_folder="C:/Path/To/SaveAll")



def gather_all_taf(main_folder_path):
    import pandas as pd
    import os
    import glob

    taf_files = glob.glob(os.path.join(main_folder_path, "**", "*_TAF_results.csv"), recursive=True)

    all_taf = []
    for file in taf_files:
        df = pd.read_csv(file)
        all_taf.append(df)

    if all_taf:
        final_df = pd.concat(all_taf, ignore_index=True)
        final_df.to_csv(os.path.join(main_folder_path, "All_TAF_Results.csv"), index=False)
        print(f"✅ Samlet {len(taf_files)} TAF-filer til én fil!")
    else:
        print("🚨 Ingen TAF-filer funnet!")

    return
  
save_to_folder = "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\TAF 27.04"
file_paths = [
    "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240909_1308_Test00_T_CORR.xlsx",
    "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240909_1321_Test01_T_CORR.xlsx",
    "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240910_1547_Test02_T_CORR.xlsx",
    "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240910_1619_Test03_T_CORR.xlsx",
    "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240910_1623_Test04_T_CORR.xlsx",
    "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240910_1627_Test05_T_CORR.xlsx",
    "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240910_1645_Test06_T_CORR.xlsx",
    
    "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240910_1649_Test07_T_CORR.xlsx",
    "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240910_1652_Test08_T_CORR.xlsx",
    "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240910_1719_Test09_T_CORR.xlsx",

    
    "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240910_1723_Test10_T_CORR.xlsx",
    "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240910_1803_Test11_T_CORR.xlsx",
    "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240910_1814_Test12_T_CORR.xlsx",

    "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240910_1822_Test13_T_CORR.xlsx",
    "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1513_Test14_T_CORR.xlsx",
    "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1530_Test15_T_CORR.xlsx",
    "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1536_Test16_T_CORR.xlsx",

    "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1543_Test17_T_CORR.xlsx",
    "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1600_Test18_T_CORR.xlsx",

    "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1604_Test19_T_CORR.xlsx",
    "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1611_Test20_T_CORR.xlsx",

    "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1644_Test21_T_CORR.xlsx",
    "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1718_Test22_T_CORR.xlsx",
    "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1838_Test23_T_CORR.xlsx",
    "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1853_Test24_T_CORR.xlsx",
    "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1915_Test25_T_CORR.xlsx",
    "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1941_Test26_T_CORR.xlsx",
    "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240912_1157_Test27_T_CORR.xlsx", 
    "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240913_1443_Test28_T_CORR.xlsx"
    ]
johan = run_all_tests_from_paths(file_paths, save_to_folder)

# file_paths = [
#     "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1513_Test14_T_CORR.xlsx",
#     "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1543_Test17_T_CORR.xlsx",
#     "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1604_Test19_T_CORR.xlsx",
#     "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1644_Test21_T_CORR.xlsx",
#     "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1718_Test22_T_CORR.xlsx"
#     ]
    
# johan = run_all_tests_from_paths(file_paths, save_to_folder) 

# file_paths = [
#     "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1838_Test23_T_CORR.xlsx",
#     "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1853_Test24_T_CORR.xlsx",
#     "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1915_Test25_T_CORR.xlsx",
#     "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1941_Test26_T_CORR.xlsx",
#     ]
    
# johan = run_all_tests_from_paths(file_paths, save_to_folder)    
