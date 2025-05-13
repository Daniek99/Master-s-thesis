# -*- coding: utf-8 -*-
"""
This code creates a batch plot of displacement vs time for all active dampers for each test. 
Batch: stacked Disp[1] vs time (t=10→35 s) for all Test02–Test26
No annotations, no accel background, keeps your normalization + threshold logic.
"""

import os
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# === SETTINGS ===
data_folder  = r"C:\Users\danie\Documents\Master\Numerisk analyse\Tester\Alletester"    #Locally saved folder containing all test files
SAVE_PLOTS   = True       # True → write PNGs; False → just show
THRESHOLD    = 0.4        # minimum displacement threshold for activation
t_min, t_max = 10, 35     # seconds window, 0-50 is the total range. 

test_intensity = {
    "Test02": 0.04, "Test03": 0.09, "Test04": 0.09, "Test05": 0.09, "Test06": 0.18,
    "Test07": 0.18, "Test08": 0.18, "Test09": 0.27, "Test10": 0.27, "Test11": 0.36,
    "Test12": 0.36, "Test13": 0.36, "Test14": 0.09, "Test15": 0.18, "Test16": 0.18,
    "Test17": 0.18, "Test18": 0.27, "Test19": 0.27, "Test20": 0.27, "Test21": 0.36,
    "Test22": 0.45, "Test23": 0.18, "Test24": 0.27, "Test25": 0.36, "Test26": 0.45
}
# =========================================================================

# find all files named like TestXX
files = sorted(
    f for f in os.listdir(data_folder)
    if re.search(r"Test\d\d", f) and f.lower().endswith(".xlsx")
)

for fn in files:
    test = re.search(r"(Test\d+)", fn).group(1)
    path = os.path.join(data_folder, fn)
    print(f"\n→ {test}: {fn}")

    # --- load data ---
    df = pd.read_excel(path)
    if "Time (s)" not in df.columns:
        print("   ⚠️ Missing 'Time (s)' → skip")
        continue
    time = df["Time (s)"]

    # --- Disp columns --- finding columns with the relevant displacement sensors
    disp1_cols = [c for c in df.columns if c.startswith("Disp[1]")]
    disp2_cols = [c for c in df.columns if c.startswith("Disp[2]")]
    if not disp1_cols:
        print("   ⚠️ No Disp[1] columns → skip")
        continue

    # --- normalize Disp[2] for t=0 and subtract from Disp[1] in timestep
    df2 = {c: df[c] - df[c].iloc[0] for c in disp2_cols}
    for c1 in disp1_cols:
        suf = c1.split("Disp[1]")[-1]
        c2  = f"Disp[2]{suf}"
        if c2 in df2:
            df[c1] = df[c1] - df2[c2]
        else:
            print(f"   ⚠️ No matching {c2} for {c1}")

    # --- normalize Disp[1] to zero and threshold ---
    df_adj = pd.DataFrame()
    valid  = []
    for c in disp1_cols:
        norm = df[c] - df[c].iloc[0]
        if norm.abs().max() >= THRESHOLD:
            df_adj[c] = norm
            valid.append(c)
        else:
            print(f"   skipped {c}: never exceeds ±{THRESHOLD} mm")

    if not valid:
        print("   ⚠️ No valid dampers → skip")
        continue

    # --- trim to 10≤t≤35 ---
    mask    = (time >= t_min) & (time <= t_max)
    t_trim  = time[mask]
    df_trim = df_adj.loc[mask, valid]

    # --- plot stacked subplots ---
    n = len(valid)
    fig, axes = plt.subplots(n, 1, figsize=(4, 1.2*n), sharex=True)
    if n == 1:
        axes = [axes]

    g    = test_intensity.get(test, None)
    supt = f"{test}  – L'Aquila {g:.2f} g" if g else test
    fig.suptitle(supt, fontsize=14, fontweight="bold")

    for ax, col in zip(axes, valid):
        ax.plot(t_trim, df_trim[col], color="C0", lw=1)
        ax.set_ylim(-25, 25)
        ax.grid(which="both", linestyle=":", linewidth=0.5)

        # remove default y‐axis ticks & labels
        ax.set_yticks([])

        # rotated damper name just outside left:
        ax.text(
            x=-0.05, y=0.5, s=col,
            transform=ax.transAxes,
            fontsize=12, rotation=75,
            va='center', ha='right'
        )

    # force x‐limits exactly
    for ax in axes:
        ax.set_xlim(t_min, t_max)

    # xlabel only on bottom
    axes[-1].set_xlabel("Time (s)", fontsize=12)
    axes[-1].set_xticks(np.arange(t_min, t_max+1, 5))
    axes[-1].tick_params(axis="x", labelsize=10)

    # bump bottom margin so ticklabels aren’t clipped
    fig.subplots_adjust(bottom=0.20)

    # save or show
    if SAVE_PLOTS:
        save_path = os.path.join(data_folder, f"{test}_stacked.png")
        plt.savefig(
            save_path,
            dpi=300,
            bbox_inches='tight',
            pad_inches=0.1
        )
        print(f"   ✓ saved {save_path}")
    plt.show()
    plt.close(fig)
