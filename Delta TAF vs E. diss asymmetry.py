# -*- coding: utf-8 -*-
"""
Created on Mon May  5 15:55:28 2025

This code assesses the correlation between Delta TAF (Experimental - Simulated)
against Damper energy dissipation asymmetry (Most dissipating facade - least dissipating facade (both in-plane))
Whether this increases torsion compared to the numerical simulations will be investigated using statistical
methods. 

@author: danie
"""

import pandas as pd, numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import pearsonr, spearmanr
sns.set_context("talk")

# ─────────────────────────────────────────────────────────────
# 1. Re-create the dataset
# ─────────────────────────────────────────────────────────────
rows = [
# Cfg Test  TAF  SimTAF  DeltaE_abs  DeltaE_pct
 (1,  6, 1.08, 1.05,   0.166,  33),
 (1,  7, 1.18, 1.05,   0.610,  44),
 (1,  8, 1.01, 1.05,   1.100,  55),

 (2, 15, 1.203, 1.10,  3.567,  99),
 (2, 16, 1.231, 1.10,  4.388, 100),         #Simulated values from Catania
 (2, 17, 1.115, 1.10,  5.025, 100),

 (1,  9, 1.093, 1.00,  2.140,  35),
 (1, 10, 1.169, 1.00,  2.591,  23),

 (2, 18, 1.253, 1.05,  8.110,  93),
 (2, 19, 1.237, 1.05,  9.704,  92),
 (2, 20, 1.236, 1.05, 10.672,  92),

 (1, 11, 1.204, 1.03,  3.917,  18),
 (1, 12, 1.177, 1.03,  4.575,  17),
 (1, 13, 1.192, 1.03,  3.657,  11),

 (2, 21, 1.227, 1.03, 17.524,  87),
 (2, 22, 1.227, np.nan, 20.071, 83),   # SimTAF missing → will be dropped
]
cols = ["Config","Test","TAF","SimTAF","DeltaE_abs","DeltaE_pct"]
df   = pd.DataFrame(rows, columns=cols)

# ─────────────────────────────────────────────────────────────
# 2. Derived quantities
# ─────────────────────────────────────────────────────────────
df["DeltaE_pct"] = df["DeltaE_pct"] / 100      # convert to fraction
df["DeltaTAF"]   = df["TAF"] - df["SimTAF"]    # NaN for Test 22

df_valid = df.dropna(subset=["DeltaTAF"])      # drop rows with NaN SimTAF

# ─────────────────────────────────────────────────────────────
# 3. Correlation statistics
# ─────────────────────────────────────────────────────────────
def corr_report(x, y, label):
    r_p,  p_p  = pearsonr(x, y)
    r_s,  p_s  = spearmanr(x, y)
    print(f"\n{label}")
    print(f"  Pearson  r = {r_p:+.3f}   p = {p_p:.3f}")
    print(f"  Spearman ρ = {r_s:+.3f}   p = {p_s:.3f}")

corr_report(df_valid["DeltaE_abs"],
            df_valid["DeltaTAF"],
            "ΔTAF  vs  ΔE_abs (kJ)")

corr_report(df_valid["DeltaE_pct"],
            df_valid["DeltaTAF"],
            "ΔTAF  vs  ΔE_pct (fraction)")

# ── 4.  Two figures: ΔTAF vs ΔE_abs and ΔE_pct (Energy asymmetry in percentage) (Cfg-specific markers) ──────
cfg_marker = {1: "o", 2: "s"}    # circle for Cfg 1, square for Cfg 2
cfg_label  = {1: "Cfg 1", 2: "Cfg 2"}

def scatter_by_cfg(ax, x, y, xlabel, title, xlim=None):
    # points, split by configuration
    for cfg in [1, 2]:
        pts = df_valid[df_valid["Config"] == cfg]
        if pts.empty:
            continue
        ax.scatter(x.loc[pts.index], y.loc[pts.index],
                   marker=cfg_marker[cfg], s=75, alpha=.85,
                   edgecolors="k" if cfg == 2 else None,
                   label=cfg_label[cfg])

    # pooled OLS fit
    m, c = np.polyfit(x, y, 1)
    xs = np.linspace(x.min(), x.max(), 100)
    ax.plot(xs, m * xs + c, color="black", lw=2.5, label="OLS fit")

    if xlim:
        ax.set_xlim(xlim)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("ΔTAF  (exp – sim)")
    ax.set_title(title, pad=10)
    ax.grid(alpha=.4)
    ax.legend(frameon=True, fontsize=10)

# 4A  absolute asymmetry (kJ)
fig1, ax1 = plt.subplots(figsize=(7,5))
scatter_by_cfg(ax1,
               df_valid["DeltaE_abs"],
               df_valid["DeltaTAF"],
               "Energy-dissipation asymmetry  ΔE  [kJ]",
               "ΔTAF vs ΔE_abs")

# 4B  percentage asymmetry (0–100 %)
fig2, ax2 = plt.subplots(figsize=(7,5))
pct = df_valid["DeltaE_pct"] * 100
scatter_by_cfg(ax2,
               pct,
               df_valid["DeltaTAF"],
               "Energy-dissipation asymmetry  ΔE  [% of total]",
               "ΔTAF vs ΔE_pct",
               xlim=(0, 100))

plt.tight_layout()
plt.show()
