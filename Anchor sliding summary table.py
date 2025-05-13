# -*- coding: utf-8 -*-
"""
Created on Thu May  8 12:48:38 2025

@author: danie
"""

# -*- coding: utf-8 -*-
"""
Batch: maximum |Disp[2]| per anchor profile and per test
Produces a single summary table of anchor profile sliding sliding per damper per test
"""

import os
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# === USER SETTINGS ==========================================================
data_folder       = r"C:\Users\danie\Documents\Master\Numerisk analyse\Tester\Alletester"
THRESHOLD_PLOT    = 0.30  # mm  – keep a column only if it ever exceeds this
PLOT_EACH_TEST    = False # True to keep the original stacked plots for sanity-check
SAVE_TABLE_CSV    = True  # writes "max_disp2_table.csv" next to the script
# ============================================================================

# ---------- containers for the summary table --------------------------------
max_disp = {}   # {test: {col: max|disp|}}

for file_name in sorted(f for f in os.listdir(data_folder) if f.endswith(".xlsx")):
    test = re.search(r"(Test\d+)", file_name)
    test = test.group(1) if test else file_name
    file_path = os.path.join(data_folder, file_name)
    print(f"→ {test}")

    try:
        df = pd.read_excel(file_path)
        time = df["Time (s)"]                         # required column
        disp_cols = [c for c in df.columns if c.startswith("Disp[2]")]
        disp_cols.sort(key=lambda c: (c.endswith("2F"), c))  # 1F rows first

        max_disp[test] = {}

        # (optional) plot for QC
        if PLOT_EACH_TEST and disp_cols:
            n = len(disp_cols)
            fig, axes = plt.subplots(n, 1, figsize=(10, 2.4*n), sharex=True)
            if n == 1: axes = [axes]

        for i, col in enumerate(disp_cols):
            disp = df[col] - df[col].iloc[0]          # normalise
            m = disp.abs().max()
            max_disp[test][col] = round(m, 3)

            if PLOT_EACH_TEST and m >= THRESHOLD_PLOT:
                ax = axes[i]
                ax.plot(time, disp, lw=0.8)
                ax.set_ylabel(col, rotation=0, labelpad=35)
                ax.set_ylim(-3, 3)
                ax.grid(True)

        if PLOT_EACH_TEST and disp_cols:
            axes[-1].set_xlabel("Time (s)")
            plt.tight_layout()
            plt.show()

    except Exception as e:
        print(f"  ⚠️  skipped – {e}")

# ---------- build a tidy DataFrame ------------------------------------------
table = pd.DataFrame.from_dict(max_disp, orient="index").fillna(0.0)

# Order tests numerically (Test02, Test03, …) and columns alphabetically
table = table.loc[sorted(table.index, key=lambda t: int(re.search(r"\d+", t).group()))]
table = table[sorted(table.columns)]


# ---------- optionally save to disk ----------------------------------------
if SAVE_TABLE_CSV:
    table.to_csv("max_disp2_table.csv")
    print("✓ Table written to max_disp2_table.csv")

