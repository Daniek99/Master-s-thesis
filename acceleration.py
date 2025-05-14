# -*- coding: utf-8 -*-
"""
Created on Mon Mar 31 14:48:15 2025

@author: Johan Linstad
"""
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm
from matplotlib.collections import LineCollection



def beregn_massesenter(df):
    """
    Beregner massesenteret i x- og z-retning for en etasje.
    Parametere:
        df (pd.DataFrame): DataFrame med kolonner ['mass', 'x', 'z']
    Returnerer:
        tuple: (x_cm, z_cm)
    """
    total_mass = df["mass"].sum()
    x_cm = (df["mass"] * df["x"]).sum() / total_mass
    z_cm = (df["mass"] * df["z"]).sum() / total_mass
    return x_cm, z_cm

# Eksempel: massesenter for 1. og 2. etasje
massedata_1F = pd.DataFrame({
        "mass": [6.4, 1.2, 1.2, 0.6, 0.6, 1.2, 1.2],  # node 110 + 911,912,913,914,915,916
        "x":    [2.5, 0.503, 4.496, 0.503, 4.496, 0.503, 4.496],
        "z":    [-2.25, -0.553, -0.553, -1.7, -1.7, -3.947, -3.947]
    })
    
massedata_2F = pd.DataFrame({
        "mass": [5.8, 0.6, 1.2, 0.6, 1.2,  0.6, 1.2],  # node 210 + 921,922,923,924,925,926
        "x":    [2.5, 0.503, 2.003, 4.496, 0.503, 2.003, 4.496],
        "z":    [-2.25, -0.553, -0.553, -0.553, -2.806, -2.806, -2.806]
    })
    
x_cm_1F, z_cm_1F = beregn_massesenter(massedata_1F)
x_cm_2F, z_cm_2F = beregn_massesenter(massedata_2F)

print(f"\nCenter of mass 1. floor: x = {x_cm_1F:.3f} m, z = {z_cm_1F:.3f} m")
print(f"Center of mass 2. floor: x = {x_cm_2F:.3f} m, z = {z_cm_2F:.3f} m\n")


def force_acc(file_path):
    # Leser inn Excel-filen
    xls = pd.ExcelFile(file_path)
    df = pd.read_excel(xls, sheet_name=xls.sheet_names[0])
    
    tid_start = 10
    tid_slutt = 35
    
    # Filtrerer ut displacement-sensorer
    disp_columns = [col for col in df.columns if col.startswith("Disp")]
    
    
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

    
    # Lagre-mappe
    save_folder = os.path.join(os.path.dirname(file_path), "Test acc 09.05", test_number)
    os.makedirs(save_folder, exist_ok=True)
    
    
    #%%sensorer som skal fjernes
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
        disp_columns = [col for col in disp_columns if not any(excl in col for excl in sensors_to_exclude)]
    
    excluded_text = ""
    if test_number_raw in sensors_to_remove:
        sensors_to_exclude = sensors_to_remove[test_number_raw]
        excluded_text = f"The following sensors have been excluded for {test_number}:\n" + ", ".join(sensors_to_exclude)

    
    # Definerer bakkenivå-sensorer (Pakket i lister for å unngå feil)
    ground_floor_sensor_x = ["PosA1T"]  # X-retning
    ground_floor_sensor_y = ["PosA2L"]  # Y-retning
    
    print("Ground floor sensors:", ground_floor_sensor_x, ground_floor_sensor_y)
    
    # Lager en liste over kolonner som skal inkluderes
    selected_columns = ["Time (s)"] + disp_columns
    if ground_floor_sensor_x[0] in df.columns:
        selected_columns += ground_floor_sensor_x
    if ground_floor_sensor_y[0] in df.columns:
        selected_columns += ground_floor_sensor_y

    # Kopierer relevante kolonner inkludert tid
    df_disp = df[selected_columns].copy()

    # Trekker fra gjennomsnittet av de 5 første sekundene for å justere nullpunktet
    start_values = df_disp[df_disp["Time (s)"] <= 5].mean(numeric_only=True)
    df_disp.iloc[:, 1:] = df_disp.iloc[:, 1:] - start_values[1:]
    
    
    
    # Filtrerer på nytt for displacement-sensorer uten "Disp[" (for å ekskludere feilformaterte)
    disp_columns = [col for col in df_disp.columns if col.startswith("Disp") and not col.startswith("Disp[")]

    # Velger sensorer for interstory drift
    first_floor_sensors_x = [col for col in disp_columns if "_1F" in col and col.endswith("X")]
    first_floor_sensors_y = [col for col in disp_columns if "_1F" in col and col.endswith("Y")]
    second_floor_sensors_x = [col for col in disp_columns if "_2F" in col and col.endswith("X")]
    second_floor_sensors_y = [col for col in disp_columns if "_2F" in col and col.endswith("Y")]

    # Filtrer tidsområdet mellom 5 og 30 sekunder
    df_disp = df_disp[(df_disp["Time (s)"] >= tid_start) & (df_disp["Time (s)"] <= tid_slutt)].reset_index(drop=True)
    
    # Liste over sensorer som må inverteres
    inverted_sensors = ["Disp12_NE_1F_X", "Disp16_NE_2F_X", "Disp13_NE_1F_Y", "Disp15_SW_1F_Y"]
    for sensor in inverted_sensors:
        if sensor in df_disp.columns:
            df_disp[sensor] = -df_disp[sensor]  # Endrer fortegnet
    
    # Justerer displacement for bakkenivå hvis sensorene finnes
    if ground_floor_sensor_x[0] in df_disp.columns:
        for col in first_floor_sensors_x + second_floor_sensors_x:
            df_disp[col] = df_disp[col] - df_disp[ground_floor_sensor_x[0]]
    if ground_floor_sensor_y[0] in df_disp.columns:
        for col in first_floor_sensors_y + second_floor_sensors_y:
            df_disp[col] = df_disp[col] - df_disp[ground_floor_sensor_y[0]]
    
   

    
    time = df["Time (s)"].values
    #%%
    
    #acc_columns = [col for col in df.columns if col.startswith("Acc")]
    acc_columns = [
    col for col in df.columns
    if col.startswith("Acc") and "_X" in col and ("NE" in col or "SW" in col)
    ]
    print (acc_columns)
   # Først: inverter sensorene
    # Liste over sensorer som skal inverteres
    # inverted_acc_sensors = [
    #     "Acc01_ST_NE_X",
    #     "Acc09_1F_SW_X",
    #     "Acc10_1F_SW_Y",
    #     "Acc13_2F_SW_X",
    #     "Acc14_1F_SW_Y",
        
    #     # legg til flere hvis nødvendig
    # ]
    # for sensor in inverted_acc_sensors:
    #     if sensor in df.columns:
    #         df[sensor] = -df[sensor]
    
    # Så: filtrer vekk outliers og lag den endelige listen
    outlier_threshold = 3000
    acc_columns = [col for col in df.columns if col.startswith("Acc") and df[col].abs().max() <= outlier_threshold]
    
    

    

    
    # Definerer bakkenivå-sensorer
    ground_acc_x = "accT"  # X-retning
    ground_acc_y = "accL"  # Y-retning
    
    ground_acc_ne_x2 = "Acc01_ST_NE_X"  # X-retning
    ground_acc_se_x2 = "Acc04_ST_SE_X"  # X-retning
    ground_acc_ne_y2 = "Acc02_ST_NE_Y"
    
    

    print("acc_columns=", acc_columns)

    
    # Velger sensorer for acc in x direction
    Ground_acc = ["accT", "accL"]
    acc_1F_x_cols = [col for col in acc_columns if "_1F" in col and col.endswith("X")]
    acc_2F_x_cols = [col for col in acc_columns if "_2F" in col and col.endswith("X")]
    
    
    acc_1F_y_cols = [col for col in acc_columns if "_1F" in col and col.endswith("Y")]
    acc_2F_y_cols = [col for col in acc_columns if "_2F" in col and col.endswith("Y")]
    
    acc_1F_x_NE = [col for col in acc_columns if "_1F" in col and "NE" in col and col.endswith("X")]
    acc_2F_x_NE = [col for col in acc_columns if "_2F" in col and "NE" in col and col.endswith("X")]
    acc_1F_x_SW = [col for col in acc_columns if "_1F" in col and "SW" in col and col.endswith("X")]
    acc_2F_x_SW = [col for col in acc_columns if "_2F" in col and "SW" in col and col.endswith("X")]

    # Inverterer SW-aks i X-retning hvis de finnes
    for col in acc_1F_x_SW:
        if col in df.columns:
            df[col] = -df[col]

    for col in acc_2F_x_SW:
        if col in df.columns:
            df[col] = -df[col]

    # Hent gjennomsnittlig akselerasjon for hver etasje (konverter til numpy-array)
    acc_1F_x = df[acc_1F_x_cols].mean(axis=1).values
    acc_2F_x = df[acc_2F_x_cols].mean(axis=1).values

    df_acc = df[["Time (s)"] + acc_columns + Ground_acc].copy()
    
    # Plot akselerasjoner over tid
    plt.figure(figsize=(14, 6))
    for col in acc_columns:
        plt.plot(df_acc["Time (s)"], df_acc[col], label=col)
    
    plt.xlabel("Time (s)")
    plt.ylabel("Acceleration (cm/s²)")
    plt.title(f"{test_number} - Acceleration (Cleaned Sensors)")
    plt.legend(loc='upper right', fontsize=8, ncol=2)
    plt.grid(True)
    plt.tight_layout()
    
    plot_name = f"{test_number}_Acceleration_Cleaned.png"
    plt.savefig(os.path.join(save_folder, plot_name), bbox_inches="tight")
    plt.show()

    
    df_ground_x = df[["Time (s)"] + [ground_acc_x] + [ground_acc_ne_x2]]
    df_ground_y = df[["Time (s)"] + [ground_acc_y] + [ground_acc_ne_y2]]
    print("df_acc=", df_acc.columns)

    
    #%% Plott alle NE og SW akselerometre i X-retning (begge etasjer)
    plt.figure(figsize=(14, 6))
    plt.suptitle(f"Akselerometer – X-retning (NE og SW hjørner) – {test_number}", fontsize=15, fontweight="bold")

    # Plott NE (X-retning)
    for col in acc_1F_x_NE + acc_2F_x_NE:
        if col in df.columns:
            plt.plot(df["Time (s)"], df[col], label=col, linestyle='-')

    # Plott SW (X-retning)
    for col in acc_1F_x_SW + acc_2F_x_SW:
        if col in df.columns:
            plt.plot(df["Time (s)"], df[col], label=col, linestyle='--')

    plt.xlabel("Tid (s)")
    plt.ylabel("Akselerasjon (cm/s²)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(save_folder, f"{test_number}-acc_NE_SW_X.png"))
    plt.show()

    #%% Plott alle NE og SW akselerometre i X-retning (begge etasjer)
    plt.figure(figsize=(14, 6))
    plt.suptitle(f"Akselerometer – X-retning (NE og SW hjørner) – {test_number}", fontsize=15, fontweight="bold")

    
    # Plott SW (X-retning)
    for col in acc_1F_x_SW + acc_2F_x_SW:
        if col in df.columns:
            plt.plot(df["Time (s)"], df[col], label=col, linestyle='--')

    plt.xlabel("Tid (s)")
    plt.ylabel("Akselerasjon (cm/s²)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(save_folder, f"{test_number}-acc_NE_SW_X.png"))
    plt.show()



    #%%
    
    # Plotter displacement for alle sensorer delt opp etter etasje og retning
    fig, axes = plt.subplots(3, 2, figsize=(14, 10), sharex=True)

    #Tittel
    plt.suptitle(f"Shaking Table Test - {test_number}", fontsize=16, fontweight="bold")

    # Ground floor X (Sjekker om bakkenivåsensoren finnes før plotting)
    if ground_acc_x in df_acc.columns:
        axes[0, 0].plot(df_acc["Time (s)"], df_acc[ground_acc_x], label=ground_acc_x)

    axes[0, 0].set_title("Acceleration - Ground Floor (X)")
    axes[0, 0].set_ylabel("Acceleration (cm/s^2)")
    axes[0, 0].legend()
    axes[0, 0].grid(True)

    # Ground floor Y (Sjekker om bakkenivåsensoren finnes før plotting)
    if ground_acc_y in df_acc.columns:
        axes[0, 1].plot(df_acc["Time (s)"], df_acc[ground_acc_y], label=ground_acc_y)

    axes[0, 1].set_title("Acceleration - Ground Floor (Y)")
    axes[0, 1].set_ylabel("Acceleration (cm/s$^2$)")
    axes[0, 1].legend()
    axes[0, 1].grid(True)

    # Første etasje X
    for sensor in acc_1F_x_cols:
        axes[1, 0].plot(df_acc["Time (s)"], df_acc[sensor], label=sensor)
    axes[1, 0].set_title("Acceleration - First Floor (X)")
    axes[1, 0].set_ylabel("Acceleration (cm/s$^2$)")
    axes[1, 0].legend()
    axes[1, 0].grid(True)

    # Første etasje Y
    for sensor in acc_1F_y_cols:
        axes[1, 1].plot(df_acc["Time (s)"], df_acc[sensor], label=sensor)
    axes[1, 1].set_title("Acceleration - First Floor (Y)")
    axes[1, 1].set_ylabel("Acceleration (cm/s$^2$)")
    axes[1, 1].legend()
    axes[1, 1].grid(True)

    # Andre etasje X
    for sensor in acc_2F_x_cols:
        axes[2, 0].plot(df_acc["Time (s)"], df_acc[sensor], label=sensor)
    axes[2, 0].set_title("Acceleration - Second Floor (X)")
    axes[2, 0].set_xlabel("Time (s)")
    axes[2, 0].set_ylabel("Acceleration (mm)")
    axes[2, 0].legend()
    axes[2, 0].grid(True)

    # Andre etasje Y
    for sensor in acc_2F_y_cols:
        axes[2, 1].plot(df_acc["Time (s)"], df_acc[sensor], label=sensor)
    axes[2, 1].set_title("Acceleration - Second Floor (Y)")
    axes[2, 1].set_xlabel("Time (s)")
    axes[2, 1].set_ylabel("Acceleration (cm/s$^2$)")
    axes[2, 1].legend()
    axes[2, 1].grid(True)

    plt.tight_layout()
    

    #%% gorund floor sensors against each other
    # Lag ny figur med X og Y-retning oppå hverandre
    fig, axes = plt.subplots(2, 1, figsize=(14, 10), sharex=True)
    plt.suptitle(f"Shaking Table Test - {test_number}", fontsize=16, fontweight="bold")

    # === Plot X-retning ===
    axes[0].plot(df_ground_x["Time (s)"], df_ground_x[ground_acc_x], label=ground_acc_x)
    axes[0].plot(df_ground_x["Time (s)"], df_ground_x[ground_acc_ne_x2], label=ground_acc_ne_x2)
    axes[0].set_title("Acceleration - Ground Floor (X)")
    axes[0].set_ylabel("Acceleration (cm/s$^2$)")
    axes[0].legend()
    axes[0].grid(True)

    # === Plot Y-retning ===
    axes[1].plot(df_ground_y["Time (s)"], df_ground_y[ground_acc_y], label=ground_acc_y)
    axes[1].plot(df_ground_y["Time (s)"], df_ground_y[ground_acc_ne_y2], label=ground_acc_ne_y2)
    axes[1].set_title("Acceleration - Ground Floor (Y)")
    axes[1].set_ylabel("Acceleration (cm/s$^2$)")
    axes[1].set_xlabel("Time (s)")
    axes[1].legend()
    axes[1].grid(True)

    plt.tight_layout()
    plt.show()


    #%%
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 8), sharex=True)
    plt.suptitle(f"Shaking Table Test - {test_number}", fontsize=16, fontweight="bold")

    # 1F – NE
    for sensor in acc_1F_x_NE:
        axes[0, 0].plot(df["Time (s)"], df[sensor], label=sensor)
        axes[0, 0].set_title("1F – NE (X-direction)")
        axes[0, 0].set_ylabel("Acceleration (cm/s$^2$)")
        axes[0, 0].legend()
        axes[0, 0].grid(True)

    # 1F – SW
    for sensor in acc_1F_x_SW:
        axes[0, 1].plot(df["Time (s)"], df[sensor], label=sensor)
        axes[0, 1].set_title("1F – SW (X-direction)")
        axes[0, 1].set_ylabel("Acceleration (cm/s$^2$)")
        axes[0, 1].legend()
        axes[0, 1].grid(True)

    # 2F – NE
    for sensor in acc_2F_x_NE:
        axes[1, 0].plot(df["Time (s)"], df[sensor], label=sensor)
        axes[1, 0].set_title("2F – NE (X-direction)")
        axes[1, 0].set_ylabel("Acceleration (cm/s$^2$)")
        axes[1, 0].set_xlabel("Time (s)")
        axes[1, 0].legend()
        axes[1, 0].grid(True)

    # 2F – SW
    for sensor in acc_2F_x_SW:
        axes[1, 1].plot(df["Time (s)"], df[sensor], label=sensor)
        axes[1, 1].set_title("2F – SW (X-direction)")
        axes[1, 1].set_ylabel("Acceleration (cm/s$^2$)")
        axes[1, 1].set_xlabel("Time (s)")
        axes[1, 1].legend()
        axes[1, 1].grid(True)

    plt.tight_layout()
    plt.show()

    #%%
    
    m_yellow = 0.6 #tonn
    m_red = 1.2 #tonn
    
    #Masse first floor
    m1_cm = 6.4 #tonn
    m1_add = 4*m_red + 2*m_yellow
    
    #mass second floor 
    m2_cm = 5.8 #tonn    
    m2_add = 3*m_red + 3*m_yellow

    m1 = m1_cm + m1_add #total masse 
    m2 = m2_cm + m2_add #total masse 

    m_base = 0.65 #tonn 9 columns (1m)

    m1_NE = m1_cm/2 + 2*m_red + 2*m_yellow  # 1F_NE
    m1_SW = m1_cm/2 + 2*m_red + 0*m_yellow  # 1F_SW
    m2_NE = m2_cm/2 + 1*m_red + 2*m_yellow  # 2F_NE
    m2_SW = m2_cm/2 + 2*m_red + 1*m_yellow  # 2F_Sw

    

    # print ("m1:", m1, "m2:",m2, "m1_NE+m1_SW",m1_NE+m1_SW, "m2_NE+m2_SW",m2_NE+m2_SW)

    acc_1F_x_mean = df[acc_1F_x_cols].mean(axis=1).values  # Gjennomsnitt per rad (dvs. over tid)
    acc_2F_x_mean = df[acc_2F_x_cols].mean(axis=1).values


    # Lage akselerasjonsmatrise og masse-matrise
    a_matrix = np.vstack([acc_1F_x_mean, acc_2F_x_mean])  # (2, N)
    M = np.diag([m1, m2])  # (2, 2)

    # # Beregn krefter: F = M * a
    # F_matrix = M @ a_matrix  # (2, N)

    # # Visualiser kraft over tid
    # plt.figure(figsize=(12, 5))
    # plt.plot(time, F_matrix[0], label="Forces in 1st floor (Transverse)")
    # plt.plot(time, F_matrix[1], label="Kraft i 2. etasje (Transverse)")
    # plt.xlabel("Time (s)")
    # plt.ylabel("Force (N)")
    # plt.title("Forces in Transverse direction (X-retning)")
    # plt.grid(True)
    # plt.legend()
    # plt.tight_layout()
    # plt.show()
    
    
    
    #%%
    # Hent akselerasjon for hvert hjørne (X-retning)
    acc_1F_NE = df[acc_1F_x_NE[0]].values * 0.01 #konverterer fra cm/s^2 til m/s^2
    acc_1F_SW = df[acc_1F_x_SW[0]].values * 0.01
    acc_2F_NE = df[acc_2F_x_NE[0]].values * 0.01
    acc_2F_SW = df[acc_2F_x_SW[0]].values * 0.01
    acc_1F_x_mean1 = acc_1F_x_mean * 0.01
    acc_2F_x_mean1 = acc_2F_x_mean * 0.01
    
    ground_acc_x_array = df["accT"].values * 0.01  # konverter fra cm/s² til m/s²
    ground_acc_y_array = df["accL"].values * 0.01

    # Beregn base shear i X-retning (samme for Y om du bytter kolonner)
    V_base = m_base * ground_acc_x_array + m1 * acc_1F_x_mean1 + m2 * acc_2F_x_mean1  # N

    # Plot base shear
    plt.figure(figsize=(12, 5))
    plt.plot(time, V_base, label="Base Shear (X-retning)")
    plt.xlabel("Time (s)")
    plt.ylabel("Base Shear (kN)")
    plt.title("Total base shear from two floors (X-direction) based on mean value")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plot_name = f"{test_number}-baseshear_frommean.png"
    plt.savefig(os.path.join(save_folder, plot_name))
    plt.show()
    plt.close()

    acc_1F_y_mean = df[acc_1F_y_cols].mean(axis=1).values
    acc_2F_y_mean = df[acc_2F_y_cols].mean(axis=1).values
    acc_1F_y_mean1 = acc_1F_y_mean * 0.01
    acc_2F_y_mean1 = acc_2F_y_mean * 0.01


    #Beregn base shear i X-retning (samme for Y om du bytter kolonner)
    V_base1 = m_base * ground_acc_y_array + m1 * acc_1F_y_mean1 + m2 * acc_2F_y_mean1  # N

    # Plot base shear
    plt.figure(figsize=(12, 5))
    plt.plot(time, V_base1, label="Base Shear (Y-retning)")
    plt.xlabel("Time (s)")
    plt.ylabel("Base Shear (kN)")
    plt.title("Total base shear fra 2 etasjer (Y-retning) based on mean value")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()
    

    V_b_det = m_base * ground_acc_x_array + m1_NE*acc_1F_NE + acc_1F_SW*m1_SW + acc_2F_NE*m2_NE + acc_2F_SW*m2_SW
  
    

    # Plot base shear
    plt.figure(figsize=(12, 5))
    plt.plot(time, V_b_det, label="Base Shear (X-retning)")
    plt.xlabel("Time (s)")
    plt.ylabel("Base Shear (kN)")
    plt.title("total base shear (X-retning)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plot_name = f"{test_number}-baseshear.png"
    plt.savefig(os.path.join(save_folder, plot_name))
    plt.show()
    plt.close()


    # Beregn krefter: F = m * a (N, men her fortsatt i cm/s² så egentlig da N*100)
    F_1F_NE = m1_NE * acc_1F_NE
    F_1F_SW = m1_SW * acc_1F_SW
    F_2F_NE = m2_NE * acc_2F_NE
    F_2F_SW = m2_SW * acc_2F_SW

    # Plot
    plt.figure(figsize=(14, 6))
    plt.plot(time, F_1F_NE, label="1F NE")
    plt.plot(time, F_1F_SW, label="1F SW")
    plt.plot(time, F_2F_NE, label="2F NE")
    plt.plot(time, F_2F_SW, label="2F SW")
    plt.title("Forces in X-direction – per corner (F = m·a)")
    plt.xlabel("Tid (s)")
    plt.ylabel("Kraft (kN)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plot_name = f"{test_number}-force_vs_ID1.png"
    plt.savefig(os.path.join(save_folder, plot_name))
    plt.show()
    plt.close()

    #%%

    # --- Beregn krefter: F = m * a ---
    F_1F_NE = m1_NE * acc_1F_NE
    F_1F_SW = m1_SW * acc_1F_SW
    F_2F_NE = m2_NE * acc_2F_NE
    F_2F_SW = m2_SW * acc_2F_SW

    # --- Plotting per hjørne ---
    fig, axes = plt.subplots(2, 2, figsize=(14, 8), sharex=True)
    plt.suptitle(f"{test_number} - Forces in X-direction – per corner (F = m·a)", fontsize=16, fontweight="bold")

    axes[0, 0].plot(time, F_1F_NE, label="1F NE", color='tab:blue')
    axes[0, 0].set_title("1. Floor – NE")
    axes[0, 0].set_ylabel("Force (kN)")
    axes[0, 0].grid(True)

    axes[0, 1].plot(time, F_1F_SW, label="1F SW", color='tab:orange')
    axes[0, 1].set_title("1. Floor – SW")
    axes[0, 1].grid(True)

    axes[1, 0].plot(time, F_2F_NE, label="2F NE", color='tab:green')
    axes[1, 0].set_title("2. Floor – NE")
    axes[1, 0].set_xlabel("Time (s)")
    axes[1, 0].set_ylabel("Force (kN)")
    axes[1, 0].grid(True)

    axes[1, 1].plot(time, F_2F_SW, label="2F SW", color='tab:red')
    axes[1, 1].set_title("2. Floor – SW")
    axes[1, 1].set_xlabel("Time (s)")
    axes[1, 1].grid(True)

    # Legg til legend i hvert subplot
    for ax in axes.flat:
        ax.legend()

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])  # Juster plass til suptitle
    plot_name = f"{test_number}-force.png"
    plt.savefig(os.path.join(save_folder, plot_name))
    plt.show()
    plt.close()

    #%%inter story drift
    # Beregner interstory drift mellom bakkenivå og 1. etasje
    # Velger sensorer for interstory drift
    # Filtrerer på nytt for displacement-sensorer uten "Disp[" (for å ekskludere feilformaterte)
    disp_columns_x = [col for col in df_disp.columns if col.startswith("Disp") and not col.startswith("Disp[") and col.endswith("X")]
    
    ground_floor_sensors = ["PosA1T"]
    first_floor_sensors = [col for col in disp_columns_x if "_1F" in col]
    second_floor_sensors = [col for col in disp_columns_x if "_2F" in col]
    
    ground_floor_sensors.sort()
    first_floor_sensors.sort()
    second_floor_sensors.sort()
    
    df_disp_interstory_1F = df_disp[["Time (s)"]].copy()
    for sensor in first_floor_sensors:
        if sensor.endswith("_X"):
            drift_col = f"Drift_{sensor}_Ground_X"
            df_disp_interstory_1F[drift_col] = -df_disp[sensor] 
        elif sensor.endswith("_Y"):
            drift_col = f"Drift_{sensor}_Ground_Y"
            df_disp_interstory_1F[drift_col] = -df_disp[sensor] 
    
    
    print("First floor sensor=",first_floor_sensors)
    print("second floor sensor=",second_floor_sensors)

    # Beregner interstory drift mellom 1. etasje og 2. etasje
    df_disp_interstory_2F = df_disp[["Time (s)"]].copy()
    for i in range(len(second_floor_sensors)):
        second_sensor = second_floor_sensors[i]
        first_sensor = first_floor_sensors[i % len(first_floor_sensors)]  # Matche med tilsvarende sensor på 1. etasje
        drift_col = f"Drift_{second_sensor}_{first_sensor}"
        df_disp_interstory_2F[drift_col] = df_disp[second_sensor] - df_disp[first_sensor]
        
    print("First floor SW:", [s for s in first_floor_sensors if "SW" in s])
    print("Second floor SW:", [s for s in second_floor_sensors if "SW" in s])

    print("First floor NE:", [s for s in first_floor_sensors if "NE" in s])
    print("Second floor NE:", [s for s in second_floor_sensors if "NE" in s])
    
    

    print("interstory drift 1st" , df_disp_interstory_1F.columns)
    print("interstory drift 2st" , df_disp_interstory_2F.columns)


    # Finn kolonner for SW og NE i drift-dataene
    drift_1F_SW_cols = [col for col in df_disp_interstory_1F.columns if "SW" in col]
    drift_1F_NE_cols = [col for col in df_disp_interstory_1F.columns if "NE" in col]

    drift_2F_SW_cols = [col for col in df_disp_interstory_2F.columns if "SW" in col]
    drift_2F_NE_cols = [col for col in df_disp_interstory_2F.columns if "NE" in col]
    
    
    print("drift_1F_SW_cols", drift_1F_SW_cols)    
    print("drift_1F_NE_cols", drift_1F_NE_cols)

    print("drift_2F_SW_cols", drift_2F_SW_cols)    
    print("drift_2F_NE_cols", drift_2F_NE_cols)
    
    # Finn tidsfilter mellom 5 og 30 sek
    mask_time = (df["Time (s)"] >= tid_start) & (df["Time (s)"] <= tid_slutt)

    # Bruk samme filter på kraftdataene
    F_1F_NE = F_1F_NE[mask_time]
    F_1F_SW = F_1F_SW[mask_time]
    F_2F_NE = F_2F_NE[mask_time]
    F_2F_SW = F_2F_SW[mask_time]

    # Oppdater også time hvis du bruker det i plottene
    time_filtered = time[mask_time]

    
    # Hent maks driftverdier og normaliser til Δ/H
    max_drift_1F_SW = df_disp_interstory_1F[drift_1F_SW_cols].abs().max().max() 
    max_drift_1F_NE = df_disp_interstory_1F[drift_1F_NE_cols].abs().max().max() 
    
    max_drift_2F_SW = df_disp_interstory_2F[drift_2F_SW_cols].abs().max().max() 
    max_drift_2F_NE = df_disp_interstory_2F[drift_2F_NE_cols].abs().max().max() 
    
    # === Hent driftverdier for hver hjørne (X-retning) ===
    drift_1F_NE = df_disp_interstory_1F[drift_1F_NE_cols[0]].values
    drift_1F_SW = df_disp_interstory_1F[drift_1F_SW_cols[0]].values
    drift_2F_NE = df_disp_interstory_2F[drift_2F_NE_cols[0]].values
    drift_2F_SW = df_disp_interstory_2F[drift_2F_SW_cols[0]].values
    
    # Konverter displacement fra mm til meter for riktig sammenligning (valgfritt)
    drift_1F_NE = drift_1F_NE 
    drift_1F_SW = drift_1F_SW 
    drift_2F_NE = -drift_2F_NE 
    drift_2F_SW = -drift_2F_SW 

    # === Plot F vs Δx per hjørne – som linjer med tid ===
    fig, axes = plt.subplots(2, 2, figsize=(12, 10), sharex=False, sharey=False)
    plt.suptitle(f"{test_number} - Force vs. Interstory Drift – per Corner (X-direction)", fontsize=16, fontweight="bold")

    # Felles linjesegment-generator
    def make_segment(x, y):
        points = np.array([x, y]).T.reshape(-1, 1, 2)
        return np.concatenate([points[:-1], points[1:]], axis=1)

    # Felles plotting-funksjon
    def add_colored_line(ax, x, y, label):
        segments = make_segment(x, y)
        norm = plt.Normalize(time_filtered.min(), time_filtered.max())
        lc = LineCollection(segments, cmap='viridis', norm=norm)
        lc.set_array(time_filtered[:-1])
        lc.set_linewidth(2)
        line = ax.add_collection(lc)
        return line

    # Limits
    xlim = (-40, 40)
    ylim = (-40, 40)

    # 1F NE
    line0 = add_colored_line(axes[0, 0], drift_1F_NE, F_1F_NE, "1F NE")
    axes[0, 0].set_title("1F NE")
    axes[0, 0].set_xlim(xlim)
    axes[0, 0].set_ylim(ylim)
    axes[0, 0].set_xlabel("Drift Δx (mm)")
    axes[0, 0].set_ylabel("Force F (kN)")
    axes[0, 0].grid(True)
    
    # 1F SW
    line1 = add_colored_line(axes[0, 1], drift_1F_SW, F_1F_SW, "1F SW")
    axes[0, 1].set_title("1F SW")
    axes[0, 1].set_xlim(xlim)
    axes[0, 1].set_ylim(ylim)
    axes[0, 1].set_xlabel("Drift Δx (mm)")
    axes[0, 1].grid(True)

    # 2F NE
    line2 = add_colored_line(axes[1, 0], drift_2F_NE, F_2F_NE, "2F NE")
    axes[1, 0].set_title("2F NE")
    axes[1, 0].set_xlim(xlim)
    axes[1, 0].set_ylim(ylim)
    axes[1, 0].set_xlabel("Drift Δx (mm)")
    axes[1, 0].set_ylabel("Force F (kN)")
    axes[1, 0].grid(True)

    # 2F SW
    line3 = add_colored_line(axes[1, 1], drift_2F_SW, F_2F_SW, "2F SW")
    axes[1, 1].set_title("2F SW")
    axes[1, 1].set_xlim(xlim)
    axes[1, 1].set_ylim(ylim)
    axes[1, 1].set_xlabel("Drift Δx (mm)")
    axes[1, 1].grid(True)

    # Legg til fargebar
    fig.subplots_adjust(right=0.88)
    cbar = fig.colorbar(line0, ax=axes.ravel().tolist(), shrink=0.95, pad=0.01)
    cbar.set_label("Time (s)")

    plt.tight_layout(rect=[0, 0.03, 0.75, 0.95])
    plt.savefig(os.path.join(save_folder, f"{test_number}-force_vs_ID_lines.png"))
    plt.show()
    plt.close()

    
    #%%
    # Hent riktige kolonner (etter fjerning og justering)
    
    disp_2F_x_cols = [col for col in df_disp.columns if col.startswith("Disp") and "_2F" in col and col.endswith("X")]

    print("disp_2F_x_cols", disp_2F_x_cols)

    # Beregn gjennomsnittlig displacement for 2F_X i X-retning
    df_disp["Mean_2F_X"] = df_disp[disp_2F_x_cols].mean(axis=1)

    # Plot
    plt.figure(figsize=(12, 5))
    
    plt.plot(df_disp["Time (s)"], df_disp["Mean_2F_X"], label="Gjennomsnittlig displacement 2F (X-retning)")
    plt.xlabel("Time (s)")
    plt.ylabel("Displacement (mm)")
    plt.title(f"{test_number} - Mean displacement in 2nd floor – X-direction")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

    # Finn tidsfilter mellom 5 og 30 sek
    V_b_det_filtered = V_b_det[mask_time]

    # Lag linjesegmenter for fargegradering
    points = np.array([df_disp["Mean_2F_X"].values, V_b_det_filtered]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)


    # Lag fargegradert linje
    norm = plt.Normalize(time_filtered.min(), time_filtered.max())
    lc = LineCollection(segments, cmap='viridis', norm=norm)
    lc.set_array(time_filtered[:-1])
    lc.set_linewidth(2)

    # Plott
    fig, ax = plt.subplots(figsize=(8, 6))
    line = ax.add_collection(lc)
    fig.colorbar(line, ax=ax, label='Time (s)')

    ax.set_xlim(df_disp["Mean_2F_X"].min(), df_disp["Mean_2F_X"].max())
    ax.set_ylim(V_b_det_filtered.min(), V_b_det_filtered.max())
    ax.set_xlabel("Mean displacement 2F (X) [mm]")
    ax.set_ylabel("Base Shear (kN)")
    ax.set_title(f"{test_number} - Base Shear vs Displacement (2F – X-direction) – ")
    ax.grid(True)
    ax.set_xlim(-50, 50)
    ax.set_ylim(-165, +165)
    plt.tight_layout()
    plot_name = f"{test_number}-base shear vs displacement.png"
    plt.savefig(os.path.join(save_folder, plot_name))

    plt.show()
    plt.close()   
    
    #%% Force - Delte_x
    
    
    F_1F_NE 
    F_1F_SW 
    F_2F_NE 
    F_2F_SW 
    
    return

#%%
def run_all_tests_from_paths(file_paths):
    if not file_paths:
        print("🚨 Ingen filbaner oppgitt.")
        return

    print(f"📂 Starter analyse av {len(file_paths)} testfiler...")

    for file_path in file_paths:
        print(f"🔍 Analyserer: {os.path.basename(file_path)}")
        force_acc(file_path)

    print("✅ Alle tester er analysert og plott lagret!")


# file_paths = [
#     "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240910_1547_Test02_T_CORR.xlsx",
#     "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240910_1627_Test05_T_CORR.xlsx",
#     "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240910_1649_Test07_T_CORR.xlsx",
#     "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240910_1723_Test10_T_CORR.xlsx",
#     "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240910_1822_Test13_T_CORR.xlsx"
#     ]
# johan1 = run_all_tests_from_paths(file_paths)


# file_paths = [
#     "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1513_Test14_T_CORR.xlsx",
#     "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1543_Test17_T_CORR.xlsx",
#     "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1604_Test19_T_CORR.xlsx",
#     "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1644_Test21_T_CORR.xlsx",
#     "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1718_Test22_T_CORR.xlsx"
#     ]
    
# johan = run_all_tests_from_paths(file_paths)
 
file_paths = [
    "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1838_Test23_T_CORR.xlsx",
    "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1853_Test24_T_CORR.xlsx",
    "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1915_Test25_T_CORR.xlsx",
    "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1941_Test26_T_CORR.xlsx",
    ]
    
johan = run_all_tests_from_paths(file_paths)
