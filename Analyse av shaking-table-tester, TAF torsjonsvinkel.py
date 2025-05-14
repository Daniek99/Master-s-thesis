# -*- coding: utf-8 -*-
"""
Created on Fri May  9 20:27:18 2025

@author: Johan Linstad
"""

# -*- coding: utf-8 -*-
"""
Analyse av shaking-table-tester
  • TAF + torsjonsvinkel (θ)
  • Største signerte inter-storey-drift over tid (SW / NE)
Forfatter: ChatGPT (tilpasset for Johan L.)
Dato: 2025-05-09
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
from  scipy.signal import find_peaks


# ------------------------------------------------------------------
# 1  — Hjelpefunksjoner
# ------------------------------------------------------------------
def biggest_signed(values):
    """Returnerer tallet med størst absolut­tverdi *med* fortegn."""
    return max(values, key=abs, default=0.0)


def compute_taf_theta(Δsw1, Δne1, Δsw2, Δne2, H_mm, L_mm):
    """Beregn TAF og θ (grader) gitt fire signerte driftverdier i mm."""
    # TAF
    avg1 = (Δsw1 + Δne1) / 2
    avg2 = (Δsw2 + Δne2) / 2
    taf1 = max(Δsw1, Δne1, key=abs) / avg1 if avg1 else np.nan
    taf2 = max(Δsw2, Δne2, key=abs) / avg2 if avg2 else np.nan

    # θ (rad → deg)
    θ1_deg = np.degrees((Δsw1 - Δne1) / L_mm)
    θ2_deg = np.degrees((Δsw2 - Δne2) / L_mm)

    return taf1, taf2, θ1_deg, θ2_deg


def biggest_signed_vec(df, match):
    """Serie med største |verdi| (med fortegn) pr. rad for kolonner som matcher strengen *match*."""
    cols = [c for c in df.columns if match in c]
    if not cols:
        return pd.Series(0.0, index=df.index)
    return df[cols].apply(lambda r: r.loc[abs(r).idxmax()], axis=1)


# ------------------------------------------------------------------
# 2  — Analyse av én fil
# ------------------------------------------------------------------
import os, numpy as np, pandas as pd, matplotlib.pyplot as plt
from scipy.signal import find_peaks

# --------------- hjelp ----------------
def first_with(lst, key):
    """Finn første streng i lst som inneholder key."""
    return next((c for c in lst if key in c), None)

# --------------- hoved -----------------
def analyze_shaking_table_data(file_path,
                               H_mm=2000,
                               L_mm=4500,
                               time_window=(5, 30)):
    # ---- les ----------------------------------------------------------------
    df = pd.read_excel(file_path, sheet_name=0)
    test_id  = "Test " + file_path.split("Test")[1].split("_")[0]
    save_dir = os.path.join(os.path.dirname(file_path), "TAF_signed", test_id)
    os.makedirs(save_dir, exist_ok=True)
    
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


    # ---- velg kolonner -------------------------------------------------------
    ground = "PosA1T"
    disp_cols = [c for c in df.columns if c.startswith("Disp") and c.endswith("_X")]
    first_1f  = sorted([c for c in disp_cols if "_1F" in c])
    second_2f = sorted([c for c in disp_cols if "_2F" in c])

    # ---- null-shift & tidsvindu ---------------------------------------------
    df_disp = df[["Time (s)"] + disp_cols + [ground]].copy()
    df_disp.iloc[:, 1:] -= df_disp[df_disp["Time (s)"] <= 5].mean()[1:]
    mask = df_disp["Time (s)"].between(*time_window)
    df_disp = df_disp.loc[mask].reset_index(drop=True)
    
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
       
    

    # 1) DROP kolonner (enkelt)
    if test_number_raw in sensors_to_remove:
        df_disp = df_disp.drop(
            columns=[c for c in df_disp.columns
                     if any(excl in c for excl in sensors_to_remove[test_number_raw])],
            errors="ignore"
        )
            
        
    # ------- NY LINJE!  Oppdater disp-lister etter dropp ------------
    disp_cols   = [c for c in disp_cols   if c in df_disp.columns]
    first_1f    = [c for c in first_1f    if c in df_disp.columns]
    second_2f   = [c for c in second_2f   if c in df_disp.columns]
    # ---- relativ bevegelse mot bakkenivå ------------------------------------
    rel = df_disp[disp_cols].sub(df_disp[ground], axis=0)

    

    # Eventuelle sensorer som må snus
    for s in ["Disp12_NE_1F_X", "Disp16_NE_2F_X"]:
        if s in rel.columns:
            rel[s] = -rel[s]

    # ------------------- NYTT: drift- og rotasjonsserier ---------------------
    # plukk én SW- og én NE-sensor per etasje (tar bare den første som finnes):
    sw_1 = first_with(first_1f, "SW");  ne_1 = first_with(first_1f, "NE")
    sw_2 = first_with(second_2f, "SW"); ne_2 = first_with(second_2f, "NE")

    if None in (sw_1, ne_1, sw_2, ne_2):
        raise ValueError("Finner ikke nødvendige SW/NE-sensorer!")

    # inter-storey drift som signerte serier:
    drift1_SW = rel[sw_1]                               # ground ↔ 1F
    drift1_NE = rel[ne_1]
    drift2_SW = rel[sw_2] - rel[sw_1]                   # 1F ↔ 2F
    drift2_NE = rel[ne_2] - rel[ne_1]

    # torsjonsvinkel (grader) = (Δ_SW – Δ_NE) / L
    theta_1_deg = np.degrees((drift1_SW - drift1_NE) / L_mm)
    theta_2_deg = np.degrees((drift2_SW - drift2_NE) / L_mm)

    time = df_disp["Time (s)"]

    # ---------- plot drift for hjørnene --------------------------------------
    plt.figure(figsize=(10, 6))
    plt.plot(time, drift1_SW, label="Δ1F SW")
    plt.plot(time, drift1_NE, label="Δ1F NE")
    plt.plot(time, drift2_SW, "--", label="Δ2F SW")
    plt.plot(time, drift2_NE, "--", label="Δ2F NE")
    plt.axhline(0, color="grey", lw=0.6)
    plt.xlabel("Time [s]"); plt.ylabel("Inter-storey drift [mm]")
    plt.title(f"{test_number} - Drift over time – SW/NE (1F & 2F)")
    plt.legend(); plt.grid(True); plt.tight_layout()
    plt.savefig(os.path.join(save_dir, "DriftCorners_timeseries.png"), dpi=150)
    plt.show()

    # ---------- plot rotasjon -------------------------------------------------
    plt.figure(figsize=(10, 6))
    plt.plot(time, theta_1_deg, label="θ 1F")
    plt.plot(time, theta_2_deg, label="θ 2F")
    plt.axhline(0, color="grey", lw=0.6)
    plt.xlabel("Time [s]"); plt.ylabel("Rotation θ [deg]")
    plt.title(f"{test_number} - Rotation over time")
    plt.legend(); plt.grid(True); plt.tight_layout()
    plt.savefig(os.path.join(save_dir, "Rotation_timeseries.png"), dpi=150)
    plt.show()
    # -------------- resten av analysen (TAF, topper, …) ----------------------
    # her kaller du bare den gamle logikken din,
    # eller flytt inn resten av koden som stod lengre ned.
    # -----------------------------------------------------------

    print("✓ Ferdig:", test_id)
    return {
        "drift1_SW": drift1_SW, "drift1_NE": drift1_NE,
        "drift2_SW": drift2_SW, "drift2_NE": drift2_NE,
        "theta_1_deg": theta_1_deg, "theta_2_deg": theta_2_deg,
        "time": time
    }



# ------------------------------------------------------------------
# 3  — Kjør et eksempel
# ------------------------------------------------------------------
if __name__ == "__main__":
    test_file = r"C:\Users\Johan Linstad\Documents\Master\transfer_230466_files_963a7b941\ACQ_20240911_1604_Test19_T_CORR.xlsx"
    analyze_shaking_table_data(test_file)


# file_paths = [
#     "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240909_1308_Test00_T_CORR.xlsx",
#     "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240909_1321_Test01_T_CORR.xlsx",
#     "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240910_1547_Test02_T_CORR.xlsx",
#     "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240910_1619_Test03_T_CORR.xlsx",
#     "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240910_1623_Test04_T_CORR.xlsx",
#     "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240910_1627_Test05_T_CORR.xlsx",
#     "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240910_1645_Test06_T_CORR.xlsx",
    
#     "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240910_1649_Test07_T_CORR.xlsx",
#     "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240910_1652_Test08_T_CORR.xlsx",
#     "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240910_1719_Test09_T_CORR.xlsx",

    
#     "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240910_1723_Test10_T_CORR.xlsx",
#     "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240910_1803_Test11_T_CORR.xlsx",
#     "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240910_1814_Test12_T_CORR.xlsx",

#     "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240910_1822_Test13_T_CORR.xlsx",
#     "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1513_Test14_T_CORR.xlsx",
#     "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1530_Test15_T_CORR.xlsx",
#     "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1536_Test16_T_CORR.xlsx",

#     "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1543_Test17_T_CORR.xlsx",
#     "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1600_Test18_T_CORR.xlsx",

#     "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1604_Test19_T_CORR.xlsx",
#     "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1611_Test20_T_CORR.xlsx",

#     "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1644_Test21_T_CORR.xlsx",
#     "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1718_Test22_T_CORR.xlsx",
#     "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1838_Test23_T_CORR.xlsx",
#     "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1853_Test24_T_CORR.xlsx",
#     "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1915_Test25_T_CORR.xlsx",
#     "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240911_1941_Test26_T_CORR.xlsx",
#     "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240912_1157_Test27_T_CORR.xlsx", 
#     "C:\\Users\\Johan Linstad\\Documents\\Master\\transfer_230466_files_963a7b941\\ACQ_20240913_1443_Test28_T_CORR.xlsx"
#     ]