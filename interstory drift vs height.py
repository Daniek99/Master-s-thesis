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
plt.rcParams.update({
    "font.size": 16,        # Øk font-størrelse på aksetitler, ticks osv.
    "axes.titlesize": 18,   # Tittel-størrelse
    "axes.labelsize": 16,   # Aksenes label-størrelse
    "legend.fontsize": 14,  # Legende-størrelse
    "xtick.labelsize": 16,  # X-ticks størrelse
    "ytick.labelsize": 16   # Y-ticks størrelse
})



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
    save_folder = os.path.join(os.path.dirname(file_path), "test13.05", test_number)
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
        #"27": ["Disp14", "Disp18", "Disp07"],
        "27": ["Disp12", "Disp14", "Disp16", "Disp18", "Disp13", "Disp15", "Disp17", "Disp19"]
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
    df_disp = df_disp_x[(df_disp_x["Time (s)"] >= 5) & (df_disp_x["Time (s)"] <= 30)].reset_index(drop=True)
    
    
    
    # Liste over sensorer som må inverteres
    inverted_sensors = ["Disp12_NE_1F_X", "Disp16_NE_2F_X", "Disp18_NE_1F_Y", "Disp15_SW_1F_Y"]
    #inverted_sensors = ["Disp12_NE_1F_X", "Disp16_NE_2F_X", "Disp13_NE_1F_Y", "Disp15_SW_1F_Y"]
    #inverted_sensors = ["Disp09_NE_2F_X", "Disp05_NE_1F_X"]
    # Inverterer verdiene for sensorene i listen
    for sensor in inverted_sensors:
        if sensor in df_disp_x.columns:
            df_disp_x[sensor] = -df_disp_x[sensor]  # Endrer fortegnet
    
    
    
    
    df_disp = df_disp_x
    
    # Filtrer tidsområdet mellom 5 og 30 sekunder
    df_disp = df_disp_x[(df_disp_x["Time (s)"] >= 10) & (df_disp_x["Time (s)"] <= 30)].reset_index(drop=True)
    
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
            df_disp_interstory_1F[drift_col] = df_disp[sensor] 
        elif sensor.endswith("_Y"):
            drift_col = f"Drift_{sensor}_Ground_Y"
            df_disp_interstory_1F[drift_col] = df_disp[sensor] 
    
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
            df_disp_interstory_2F[drift_col] =   df_disp[second_sensor] - df_disp[first_sensor] 

        
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




    
    
    
   
    #%% Beregner maksimal forskyvning for South og North frames
    max_south_1F = df_disp[[col for col in disp_columns_x if "SW" in col and "1F" in col]].max().max()
    max_south_2F = df_disp[[col for col in disp_columns_x if "SW" in col and "2F" in col]].max().max()
    max_north_1F = df_disp[[col for col in disp_columns_x if "NE" in col and "1F" in col]].max().max()
    max_north_2F = df_disp[[col for col in disp_columns_x if "NE" in col and "2F" in col]].max().max()
    
    
    


    
    
    # Beregner interstory drift for SW og NE sensorer
    df_drift = df_disp[disp_columns_x]#.diff() #.abs()
    H = 2000 #mm
    
    print("df_disp_interstory_2F=", df_disp_interstory_2F.columns)

    # Finn kolonner for SW og NE i drift-dataene
    drift_1F_SW_cols = [col for col in df_disp_interstory_1F.columns if "SW" in col]
    drift_1F_NE_cols = [col for col in df_disp_interstory_1F.columns if "NE" in col]

    drift_2F_SW_cols = [col for col in df_disp_interstory_2F.columns if "SW" in col]
    drift_2F_NE_cols = [col for col in df_disp_interstory_2F.columns if "NE" in col]
    
    
    print("drift_1F_SW_cols", drift_1F_SW_cols)    
    print("drift_1F_NE_cols", drift_1F_NE_cols)

    print("drift_2F_SW_cols", drift_2F_SW_cols)    
    print("drift_2F_NE_cols", drift_2F_NE_cols)
    
    
    
    # Hent maks driftverdier og normaliser til Δ/H
    max_drift_1F_SW = df_disp_interstory_1F[drift_1F_SW_cols].abs().max().max() / H *100
    max_drift_1F_NE = df_disp_interstory_1F[drift_1F_NE_cols].abs().max().max() / H *100
    
    max_drift_2F_SW = df_disp_interstory_2F[drift_2F_SW_cols].abs().max().max() / H *100
    max_drift_2F_NE = df_disp_interstory_2F[drift_2F_NE_cols].abs().max().max() / H *100
    fig, ax = plt.subplots(figsize=(6, 6))

    print("max_drift_1F_SW", max_drift_1F_SW)
    print("max_drift_1F_NE", max_drift_1F_NE)


    print("max_drift_2F_SW", max_drift_2F_SW)
    print("max_drift_2F_NE", max_drift_2F_NE)




    # Høyder i meter
    h0 = 0      # Bakkenivå
    h1 = 2      # 1. etasje
    h2 = 4      # 2. etasje
    
    # SW Trapp (bruker kumulativ drift)
    ax.step([max_drift_1F_SW, max_drift_1F_SW], [h0, h1], color='orange', marker='o')
    ax.step([max_drift_1F_SW, max_drift_2F_SW], [h1, h1], color='orange', marker='o')
    ax.step([max_drift_2F_SW, max_drift_2F_SW], [h1, h2], color='orange', marker='o', label='Drift x-direction - corner SW')
    
        
    # NE Trapp (bruker kumulativ drift)
    ax.step([max_drift_1F_NE, max_drift_1F_NE], [h0, h1], color='blue', marker='o')
    ax.step([max_drift_1F_NE, max_drift_2F_NE], [h1, h1], color='blue', marker='o')
    ax.step([max_drift_2F_NE, max_drift_2F_NE], [h1, h2], color='blue', marker='o', label='Drift x-direction - corner NE')



    # Tekstetiketter
    ax.text(max_drift_1F_SW, 1.8, f"{max_drift_1F_SW:.4f}", color='orange', ha='right', va='bottom')
    ax.text(max_drift_2F_SW, 3.8, f"{(max_drift_2F_SW):.4f}", color='orange', ha='right', va='bottom')
    ax.text(max_drift_1F_NE, h1, f"{max_drift_1F_NE:.4f}", color='blue', ha='left', va='bottom')
    ax.text(max_drift_2F_NE, h2, f"{(max_drift_2F_NE):.4f}", color='blue', ha='left', va='bottom')

    # Akser og merking
    ax.set_yticks([0, 2, 4])
    ax.set_yticklabels(["0 m (Ground)", "2 m (1st Floor)", "4 m (2nd Floor)"])
    ax.set_ylabel("Height [m]")
    ax.set_xlabel("Interstory Drift % (Δ/H)")
    ax.set_title(f"{test_number} - Maximum Interstory Drift vs Height")
    ax.set_xlim(0, 3.0)  

    ax.legend()
    ax.grid(True)
    
    plot_name = f"{test_number}_InterstoryDrift_vs_Height.png"
    plt.gcf().text(0.65, 0.75, excluded_text, fontsize=9, color="red", ha="center", va="top", bbox=dict(facecolor='white', alpha=0.6, edgecolor='red'))

    plt.savefig(os.path.join(save_folder, plot_name),bbox_inches="tight")
    plt.show()
    plt.close()

    
#%% inter story drift at the time when 1st floor max i..  for a know time

    

    # Kombiner driftkolonner for SW og NE fra df_disp_interstory_1F
    drift_1f_cols = [col for col in df_disp_interstory_1F.columns if "Drift_" in col]

    # Finn den kolonnen med størst absoluttverdi (uansett ramme)
    max_1f_col = df_disp_interstory_1F[drift_1f_cols].abs().max().idxmax()
    max_time_index = df_disp_interstory_1F[max_1f_col].abs().idxmax()
    max_time = df_disp_interstory_1F["Time (s)"].iloc[max_time_index]
    
    print(f"🕒 Maks interstory drift i 1F skjer ved {max_time:.2f} sek i kolonnen {max_1f_col}")

    # Hent driftverdier for både 1F og 2F ved dette tidspunktet
    drift_1F_at_peak = df_disp_interstory_1F.iloc[max_time_index]
    drift_2F_at_peak = df_disp_interstory_2F[df_disp_interstory_2F["Time (s)"] == max_time].iloc[0]

    H = 2000  # mm

    # Finn maks verdier for hver ramme ved peak-tidspunkt
    max_drift_1F_SW_time = max([abs(drift_1F_at_peak[col]) for col in drift_1f_cols if "SW" in col]) / H *100
    max_drift_1F_NE_time = max([abs(drift_1F_at_peak[col]) for col in drift_1f_cols if "NE" in col]) / H *100

    max_drift_2F_SW_time = max([abs(drift_2F_at_peak[col]) for col in drift_2F_at_peak.index if "SW" in col]) / H *100
    max_drift_2F_NE_time = max([abs(drift_2F_at_peak[col]) for col in drift_2F_at_peak.index if "NE" in col]) / H *100

    fig, ax = plt.subplots(figsize=(6, 6))

    # SW trapp
    ax.plot([max_drift_1F_SW_time, max_drift_1F_SW_time], [h0, h1], color='orange', marker='o')
    ax.plot([max_drift_1F_SW_time, max_drift_2F_SW_time], [h1, h1], color='orange', marker='o')
    ax.plot([max_drift_2F_SW_time, max_drift_2F_SW_time], [h1, h2], color='orange', marker='o', label="Drift x-direction - corner SW")


    # NE trapp
    ax.plot([max_drift_1F_NE_time, max_drift_1F_NE_time], [h0, h1], color='blue', marker='o')
    ax.plot([max_drift_1F_NE_time, max_drift_2F_NE_time], [h1, h1], color='blue', marker='o')
    ax.plot([max_drift_2F_NE_time, max_drift_2F_NE_time], [h1, h2], color='blue', marker='o', label="Drift x-direction - corner NE")


    # Annoteringer
    ax.text(max_drift_1F_SW_time, 1.8, f"{max_drift_1F_SW_time:.4f}", color='orange', ha='right', va='bottom')
    ax.text(max_drift_2F_SW_time, 3.8, f"{(max_drift_2F_SW_time):.4f}", color='orange', ha='right', va='bottom')
    ax.text(max_drift_1F_NE_time, 2, f"{max_drift_1F_NE_time:.4f}", color='blue', ha='left', va='bottom')
    ax.text(max_drift_2F_NE_time, 4, f"{(max_drift_2F_NE_time):.4f}", color='blue', ha='left', va='bottom')

    # Akseoppsett
    ax.set_yticks([0, 2, 4])
    ax.set_yticklabels(["0 m (Ground)", "2 m (1st Floor)", "4 m (2nd Floor)"])
    ax.set_ylabel("Height [m]")
    ax.set_xlabel("Interstory Drift % (Δ/H)")
    ax.set_title(f"{test_number} - Driftprofile at {max_time:.2f}s (Peak Drift in 1F)")
    ax.set_xlim(0, 3.0)  

    ax.legend()
    ax.grid(True)

    plot_name = f"{test_number}_StairPlot_PeakDrift1F.png"
    plt.gcf().text(0.65, 0.75, excluded_text, fontsize=9, color="red", ha="center", va="top", bbox=dict(facecolor='white', alpha=0.6, edgecolor='red'))

    plt.savefig(os.path.join(save_folder, plot_name), bbox_inches="tight")
    plt.show()
    plt.close()
    

    print(max_drift_1F_SW, max_drift_2F_SW, max_drift_1F_NE, max_drift_2F_NE)

    #%%
    # Finn alle drift-kolonner for hver etasje
    drift_1f_cols = [col for col in df_disp_interstory_1F.columns if "Drift_" in col]
    drift_2f_cols = [col for col in df_disp_interstory_2F.columns if "Drift_" in col]
    print("drift_1f_cols=", drift_1f_cols)
    print("drift_2f_cols=", drift_2f_cols)



    # Beregn gjennomsnittlig drift over tid (radvis snitt)
    mean_drift_1F = df_disp_interstory_1F[drift_1f_cols].mean(axis=1)
    mean_drift_2F = df_disp_interstory_2F[drift_2f_cols].mean(axis=1)

    # Hent tidsvektor (samme for begge)
    time = df_disp_interstory_1F["Time (s)"]

    # Plot
    plt.figure(figsize=(14, 6))
    plt.plot(time, mean_drift_1F, label="Mean Drift: Ground to 1st Floor", color="blue")
    plt.plot(time, mean_drift_2F, label="Mean Drift: 1st to 2nd Floor", color="orange")
    plt.axhline(0, color='black', linewidth=0.5, linestyle='--')

    plt.title(f"{test_number} - Mean Interstory Drift per Level")
    plt.xlabel("Time (s)")
    plt.ylabel("Interstory Drift (mm)")
    
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    
    plot_name = f"{test_number}_Mean_InterstoryDrift_BothLevels.png"
    plt.gcf().text(0.9, 0.2, excluded_text, fontsize=9, color="red", ha="center", va="top", bbox=dict(facecolor='white', alpha=0.6, edgecolor='red'))

    plt.savefig(os.path.join(save_folder, plot_name))
    plt.show()
    plt.close()
    
    mean_drift_1F_value = mean_drift_1F.abs().mean()
    mean_drift_2F_value = mean_drift_2F.abs().mean()
    
    # Returnerer den korrigerte displacement-matrisen
    return {
    "test_number": test_number,
    "max_drift_1F_SW": max_drift_1F_SW,
    "max_drift_2F_SW": max_drift_2F_SW,
    "max_drift_1F_NE": max_drift_1F_NE,
    "max_drift_2F_NE": max_drift_2F_NE,
    "drift_1F_SW_time": max_drift_1F_SW_time,
    "drift_2F_SW_time": max_drift_2F_SW_time,
    "drift_1F_NE_time": max_drift_1F_NE_time,
    "drift_2F_NE_time": max_drift_2F_NE_time,
    "save_folder": save_folder,
    "excluded_text": excluded_text,
    "mean_drift_1F_value": mean_drift_1F_value,
    "mean_drift_2F_value": mean_drift_2F_value
}
    



# Eksempel på bruk
#0,04g config 0
#file_path = "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240909_1308_Test00_T_CORR.xlsx"
#file_path = "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240909_1321_Test01_T_CORR.xlsx"

#0,04g config 1
#file_path = "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240910_1547_Test02_T_CORR.xlsx"

#0.09g config 1
#file_path = "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240910_1619_Test03_T_CORR.xlsx"
#file_path = "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240910_1623_Test04_T_CORR.xlsx"
#file_path = "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240910_1627_Test05_T_CORR.xlsx"

#0.18g config 1 
#file_path = "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240910_1645_Test06_T_CORR.xlsx"
#file_path = "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240910_1649_Test07_T_CORR.xlsx"
#file_path = "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240910_1652_Test08_T_CORR.xlsx"

#0,27g config 1
#file_path = "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240910_1719_Test09_T_CORR.xlsx"
#file_path = "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240910_1723_Test10_T_CORR.xlsx"

#0,36g config 1
#file_path = "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240910_1803_Test11_T_CORR.xlsx"
#file_path = "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240910_1814_Test12_T_CORR.xlsx"
#file_path = "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240910_1822_Test13_T_CORR.xlsx"

#0,09 config 2
#file_path = "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1513_Test14_T_CORR.xlsx"
#file_path = "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1530_Test15_T_CORR.xlsx"

#file_path = "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1644_Test21_T_CORR.xlsx"
#file_path = "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1718_Test22_T_CORR.xlsx"


#%%
def run_all_tests_from_paths(file_paths):
    if not file_paths:
        print("🚨 Ingen filbaner oppgitt.")
        return

    print(f"📂 Starter analyse av {len(file_paths)} testfiler...")

    for file_path in file_paths:
        print(f"🔍 Analyserer: {os.path.basename(file_path)}")
        analyze_shaking_table_data(file_path)

    print("✅ Alle tester er analysert og plott lagret!")
    
    
file_paths = [
    # "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240909_1308_Test00_T_CORR.xlsx",
    # "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240909_1321_Test01_T_CORR.xlsx",

    # #0,04g config 1
    # "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240910_1547_Test02_T_CORR.xlsx",

    # #0.09g config 1
    # "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240910_1619_Test03_T_CORR.xlsx",
    # "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240910_1623_Test04_T_CORR.xlsx",
    # "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240910_1627_Test05_T_CORR.xlsx",

    # #0.18g config 1 
    # "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240910_1645_Test06_T_CORR.xlsx",
    "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240910_1649_Test07_T_CORR.xlsx",
    # "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240910_1652_Test08_T_CORR.xlsx",

    # #0,27g config 1
    # "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240910_1719_Test09_T_CORR.xlsx",
    # "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240910_1723_Test10_T_CORR.xlsx",

    # #0,36g config 1
    # "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240910_1803_Test11_T_CORR.xlsx",
    # "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240910_1814_Test12_T_CORR.xlsx",
    # "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240910_1822_Test13_T_CORR.xlsx",

    # #0,09 config 2
    # "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1513_Test14_T_CORR.xlsx",
    # "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1530_Test15_T_CORR.xlsx",
    
    # "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1536_Test16_T_CORR.xlsx",
    "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1543_Test17_T_CORR.xlsx",
    # "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1600_Test18_T_CORR.xlsx",
    # "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1604_Test19_T_CORR.xlsx",
    # "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1611_Test20_T_CORR.xlsx",

    # "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1644_Test21_T_CORR.xlsx",
    # "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1718_Test22_T_CORR.xlsx", 
    
    "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1838_Test23_T_CORR.xlsx", 
    # "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1853_Test24_T_CORR.xlsx", 
    # "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1915_Test25_T_CORR.xlsx", 
    # "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1941_Test26_T_CORR.xlsx", 
    #"C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240912_1157_Test27_T_CORR.xlsx", 
    #"C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240913_1443_Test28_T_CORR.xlsx", 
    ]

# file_paths = [
#     "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240910_1547_Test02_T_CORR.xlsx",
#     "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240910_1627_Test05_T_CORR.xlsx",
#     "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240910_1649_Test07_T_CORR.xlsx",
#     "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240910_1723_Test10_T_CORR.xlsx",
#     "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240910_1822_Test13_T_CORR.xlsx"
#     ]
# johan = run_all_tests_from_paths(file_paths)


# file_paths = [
#     "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1513_Test14_T_CORR.xlsx",
#     "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1543_Test17_T_CORR.xlsx",
#     "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1604_Test19_T_CORR.xlsx",
#     "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1644_Test21_T_CORR.xlsx",
#     "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1718_Test22_T_CORR.xlsx"
#     ]
    
# johan = run_all_tests_from_paths(file_paths)
 

# file_paths = [
#     "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1838_Test23_T_CORR.xlsx",
#     "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1853_Test24_T_CORR.xlsx",
#     "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1915_Test25_T_CORR.xlsx",
#     "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1941_Test26_T_CORR.xlsx",
#     ]
    
# johan = run_all_tests_from_paths(file_paths)


# #for 0,.18 pga
# file_paths = [
#     "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240910_1649_Test07_T_CORR.xlsx",
#     "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1543_Test17_T_CORR.xlsx",
#     "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1838_Test23_T_CORR.xlsx",
#     ]

# #for 0,.27 pga
# file_paths = [
#     "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240910_1723_Test10_T_CORR.xlsx",
#     "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1604_Test19_T_CORR.xlsx",
#     "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1853_Test24_T_CORR.xlsx",
#     ]

#for 0,36 pga
# file_paths = [
#     "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240910_1822_Test13_T_CORR.xlsx",
#     "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1644_Test21_T_CORR.xlsx",
#     "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1915_Test25_T_CORR.xlsx",
#     ]

# file_paths = [
#     "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240910_1649_Test07_T_CORR.xlsx",
#     "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240910_1652_Test08_T_CORR.xlsx",
#     ]

#%% combined stair plot 
def combined_stair_plot(results_list):
    import matplotlib.pyplot as plt
    import numpy as np
    import os
    import itertools


    h0, h1, h2 = 0, 2, 4
    fig, ax = plt.subplots(figsize=(12, 8))
    #colors = ["#1f77b4", "#2ca02c", "#d62728", "#9467bd"]  # blå, grønn, rød, lilla
    color_cycle = itertools.cycle(["#1f77b4", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"])


    for idx, result in enumerate(results_list):
        test_number = result["test_number"]
        #color = colors[idx]
        color = next(color_cycle)

        drift_1F_SW = result["drift_1F_SW_time"]
        drift_2F_SW = result["drift_2F_SW_time"]
        drift_1F_NE = result["drift_1F_NE_time"]
        drift_2F_NE = result["drift_2F_NE_time"]
        
        x_offset = 0.15  # Horisontal variasjon (-0.07, 0, +0.07)
        y_offset_up = (idx % 4) * 0.1

        # SW
        ax.plot([drift_1F_SW, drift_1F_SW], [h0, h1], color=color, linestyle='-', linewidth=3, marker='o', markersize=6,
                label=f"{test_number} SW")
        ax.plot([drift_1F_SW, drift_2F_SW], [h1, h1], color=color, linestyle='-', linewidth=3)
        ax.plot([drift_2F_SW, drift_2F_SW], [h1, h2], color=color, linestyle='-', linewidth=3)

        # NE
        ax.plot([drift_1F_NE, drift_1F_NE], [h0, h1], color=color, linestyle='--', linewidth=3, marker='s', markersize=6,
                alpha=0.8, label=f"{test_number} NE")
        ax.plot([drift_1F_NE, drift_2F_NE], [h1, h1], color=color, linestyle='--', linewidth=3, alpha=0.8)
        ax.plot([drift_2F_NE, drift_2F_NE], [h1, h2], color=color, linestyle='--', linewidth=3, alpha=0.8)
        
        
        # Opprett en ekstra akse for tekst (uten ramme)
        ax_text = fig.add_axes([0.75, 0.2, 0.2, 0.6], frameon=False)
        ax_text.set_axis_off()
        
        # Skriver én linje per test
        for idx, result in enumerate(results_list):
            test_number = result["test_number"]
            drift_1F_SW = result["drift_1F_SW_time"]
            drift_2F_SW = result["drift_2F_SW_time"]
            drift_1F_NE = result["drift_1F_NE_time"]
            drift_2F_NE = result["drift_2F_NE_time"]
            
            #color = colors[idx]
            color = next(color_cycle)

            text = (f"{test_number}\n"
                    f" SW: 1F={drift_1F_SW:.2f}%, 2F={drift_2F_SW:.2f}%\n"
                    f" NE: 1F={drift_1F_NE:.2f}%, 2F={drift_2F_NE:.2f}%\n")
        
            ax_text.text(0, 1 - idx * 0.2, text, color=color, fontsize=14, va='top')
                

    # Akseinnstillinger
    ax.set_yticks([0, 2, 4])
    ax.set_yticklabels(["Ground", "1st Floor", "2nd Floor"], fontsize=12)
    ax.set_ylabel("Height [m]", fontsize=14)
    ax.set_xlabel("Interstory Drift % (Δ/H)", fontsize=14)
    ax.set_title("Interstory Drift Profiles at Max 1F Drift", fontsize=16)
    ax.set_xlim(0, 3.0)
    ax.tick_params(axis='both', labelsize=12)
    ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.7)

    # Legende
    handles, labels = ax.get_legend_handles_labels()
    unique = dict(zip(labels, handles))
    ax.legend(unique.values(), unique.keys(), loc="lower right", fontsize=10, framealpha=0.9)

    # Sensorinfo
    excluded_text = results_list[0].get("excluded_text", "")
    if excluded_text:
        plt.gcf().text(0.72, 0.88, excluded_text, fontsize=9, color="red", ha="center", va="top",
                       bbox=dict(facecolor='white', alpha=0.6, edgecolor='red'))

    plt.tight_layout()
    
    # Lagre
    save_folder = results_list[0].get("save_folder", ".")
    plot_name = "Combined_InterstoryDrift_vs_Height.png"
    plt.savefig(os.path.join(save_folder, plot_name), bbox_inches="tight", dpi=300)
    print(f"💾 Lagret forbedret plott til: {os.path.join(save_folder, plot_name)}")
    plt.show()

    

def combined_stair_plot_max_values(results_list):
    import matplotlib.pyplot as plt
    import numpy as np
    import os
    import itertools

    h0, h1, h2 = 0, 2, 4
    fig, ax = plt.subplots(figsize=(12, 8))
    #colors = ["#1f77b4", "#2ca02c", "#d62728", "#9467bd"]  # blå, grønn, rød, lilla
    color_cycle = itertools.cycle(["#1f77b4", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"])


    for idx, result in enumerate(results_list):
        test_number = result["test_number"]
        #color = colors[idx]
        color = next(color_cycle)


        drift_1F_SW = result["max_drift_1F_SW"]
        drift_2F_SW = result["max_drift_2F_SW"]
        drift_1F_NE = result["max_drift_1F_NE"]
        drift_2F_NE = result["max_drift_2F_NE"]

        ax.plot([drift_1F_SW, drift_1F_SW], [h0, h1], color=color, linestyle='-', linewidth=3, marker='o', markersize=6,
                label=f"{test_number} SW")
        ax.plot([drift_1F_SW, drift_2F_SW], [h1, h1], color=color, linestyle='-', linewidth=3)
        ax.plot([drift_2F_SW, drift_2F_SW], [h1, h2], color=color, linestyle='-', linewidth=3)

        ax.plot([drift_1F_NE, drift_1F_NE], [h0, h1], color=color, linestyle='--', linewidth=3, marker='s', markersize=6,
                alpha=0.8, label=f"{test_number} NE")
        ax.plot([drift_1F_NE, drift_2F_NE], [h1, h1], color=color, linestyle='--', linewidth=3, alpha=0.8)
        ax.plot([drift_2F_NE, drift_2F_NE], [h1, h2], color=color, linestyle='--', linewidth=3, alpha=0.8)

        # Opprett en ekstra akse for tekst (uten ramme)
        ax_text = fig.add_axes([0.75, 0.2, 0.2, 0.6], frameon=False)
        ax_text.set_axis_off()
        
        # Skriver én linje per test
        for idx, result in enumerate(results_list):
            test_number = result["test_number"]
            drift_1F_SW = result["max_drift_1F_SW"]
            drift_2F_SW = result["max_drift_2F_SW"]
            drift_1F_NE = result["max_drift_1F_NE"]
            drift_2F_NE = result["max_drift_2F_NE"]
            
            #color = colors[idx]
            color = next(color_cycle)

            text = (f"{test_number}\n"
                    f" SW: 1F={drift_1F_SW:.2f}%, 2F={drift_2F_SW:.2f}%\n"
                    f" NE: 1F={drift_1F_NE:.2f}%, 2F={drift_2F_NE:.2f}%\n")
        
            ax_text.text(0, 1 - idx * 0.2, text, color=color, fontsize=14, va='top')


    ax.set_yticks([0, 2, 4])
    ax.set_yticklabels(["Ground", "1st Floor", "2nd Floor"], fontsize=12)
    ax.set_ylabel("Height [m]", fontsize=14)
    ax.set_xlabel("Interstory Drift % (Δ/H)", fontsize=14)
    ax.set_title("Interstory Drift Profiles (Max Drift Values)", fontsize=16)
    ax.set_xlim(0, 3.0)
    ax.tick_params(axis='both', labelsize=12)
    ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.7)

    handles, labels = ax.get_legend_handles_labels()
    unique = dict(zip(labels, handles))
    ax.legend(unique.values(), unique.keys(), loc="lower right", fontsize=10, framealpha=0.9)

    # Sensorinfo
    excluded_text = results_list[0].get("excluded_text", "")
    if excluded_text:
        plt.gcf().text(0.72, 0.88, excluded_text, fontsize=9, color="red", ha="center", va="top",
                       bbox=dict(facecolor='white', alpha=0.6, edgecolor='red'))


    plt.tight_layout()
    # Lagre
    save_folder = results_list[0].get("save_folder", ".")
    plot_name = "Combined_InterstoryDrift_MaxValues.png"
    plt.savefig(os.path.join(save_folder, plot_name), bbox_inches="tight", dpi=300)
    print(f"💾 Lagret maksverdi-plott til: {os.path.join(save_folder, plot_name)}")
    plt.show()

    



results = []
for path in file_paths:
    result = analyze_shaking_table_data(path)
    results.append(result)

# 👇 NY KODE FOR Å LAGRE DRIFT I EXCEL
summary_data = []
for res in results:
    summary_data.append({
        "Test": res["test_number"],
        "Drift_1F_SW_max": res["max_drift_1F_SW"],
        "Drift_2F_SW_max": res["max_drift_2F_SW"],
        "Drift_1F_NE_max": res["max_drift_1F_NE"],
        "Drift_2F_NE_max": res["max_drift_2F_NE"],
        "Drift_1F_SW_time": res["drift_1F_SW_time"],
        "Drift_2F_SW_time": res["drift_2F_SW_time"],
        "Drift_1F_NE_time": res["drift_1F_NE_time"],
        "Drift_2F_NE_time": res["drift_2F_NE_time"],
        "MeanDrift_1F":  res["mean_drift_1F_value"],
        "MeanDrift_2F":  res["mean_drift_2F_value"]
    })

summary_df = pd.DataFrame(summary_data)

# Lagre til Excel
excel_path = os.path.join(results[0]["save_folder"], "Drift_Summary.xlsx")
summary_df.to_excel(excel_path, index=False)
print(f"✅ Drift-data lagret til Excel: {excel_path}")


# Plot samlet stair-plot
combined_stair_plot(results)  # ved peak i 1F
combined_stair_plot_max_values(results)  # globale maksdrift

