# -*- coding: utf-8 -*-
"""
Created on Mon May  5 16:43:56 2025

This code finds the correlation coefficients between interstory drift and frequency (stiffness) by OLS regression.
These will also be used in later scripts. 


@author: danie
"""

import pandas as pd, numpy as np
import matplotlib.pyplot as plt, seaborn as sns, statsmodels.api as sm
sns.set_context("talk")
from math import sqrt

# ─────────────────────────────────────────────────────────────────────────────
# 1.  DATA TABLE  (Test 22 removed, Config-3 added)
# ─────────────────────────────────────────────────────────────────────────────
rows = [
 # Cfg  Test  Frq   SW   NE   E_diss  PGA[g]
 (1,  6, 2.89, 0.47, 0.35,  0.5,  0.18),
 (1,  7,  2.87,0.45,0.49, 1.4,  0.18),
 (1,  8, 2.84, 0.56, 0.55,  2.0,  0.18),

 (2, 15, 2.45, 0.52, 0.78,  3.6,  0.18),
 (2, 16, 2.39,0.56,0.89, 4.4,  0.18),
 (2, 17, 2.34, 0.74, 0.94,  5.0,  0.18),

 (3, 23, 2.06, 0.73, 0.98,  4.2,  0.18),

 (1,  9, 2.82, 0.68, 0.81,  6.1,  0.27),
 (1, 10, 2.69, 0.69, 0.97, 11.5,  0.27),

 (2, 18, 2.28, 0.79, 1.33,  8.7,  0.27),
 (2, 19, 2.28,0.92,1.47, 10.6,  0.27),
 (2, 20, 2.28, 0.97, 1.58, 11.6,  0.27),

 (3, 24, 2.05, 0.99, 1.57,  9.9,  0.27),

 (1, 11, 2.56, 0.90, 1.32, 22.1,  0.36),
 (1, 12, 2.48,1.10,1.58, 27.2,  0.36),
 (1, 13, 2.39, 1.25, 1.77, 32.8,  0.36),

 (2, 21, 2.28, 1.30, 2.06, 20.2,  0.36),

 (3, 25, 2.02, 1.29, 2.07, 16.3,  0.36),
]
df = pd.DataFrame(rows, columns=["Config","Test","Frq","SW","NE","E_diss","PGA"])

# ─────────────────────────────────────────────────────────────────────────────
# 2.  Interpolate missing frequencies *within each configuration*
# ─────────────────────────────────────────────────────────────────────────────
df.sort_values("Test", inplace=True)
df["Frq"] = (
    df.groupby("Config")["Frq"]
      .transform(lambda s: s.interpolate())
)

# derived helper columns
df["Drift_mean"] = df[["SW","NE"]].mean(axis=1)

# ─────────────────────────────────────────────────────────────────────────────
# 3.  Plotting: separate figure for SW and NE, one line per PGA
# ─────────────────────────────────────────────────────────────────────────────
pga_palette = {0.18: "tab:blue", 0.27: "tab:orange", 0.36: "tab:green"}
cfg_marker  = {1: "o", 2: "s", 3: "^"}            # circle / square / triangle

def plot_direction_swapped(col, title, pad_frac=0.2):
    fig, ax = plt.subplots(figsize=(8,6))
    shown_cfg = set()
    for pga in sorted(df["PGA"].unique()):
        sub = df[df["PGA"] == pga]

        # scatter per configuration: x=drift, y=frequency
        for cfg in sorted(df["Config"].unique()):
            pts = sub[sub["Config"] == cfg]
            if pts.empty: continue
            label_cfg = f"Cfg {cfg}" if cfg not in shown_cfg else None
            shown_cfg.add(cfg)
            ax.scatter(
                pts[col],      # now on x
                pts["Frq"],    # now on y
                marker=cfg_marker[cfg],
                color=pga_palette[pga],
                edgecolors="k" if cfg!=1 else None,
                alpha=0.85,
                label=label_cfg
            )

        # regression line for this PGA (configs pooled): Frq ~ drift
        if len(sub) < 2:
            continue
        # fit Frq = m * drift + c
        m, c = np.polyfit(sub[col], sub["Frq"], 1)

        # determine the first/last drift for this PGA
        x_min, x_max = sub[col].min(), sub[col].max()
        pad = (x_max - x_min) * pad_frac

        # build a tiny extra‐long xs array
        xs = np.linspace(x_min - pad, x_max + pad, 100)
        ys = m*xs + c

        ax.plot(xs, ys,
                color=pga_palette[pga],
                lw=3,
                label=f"{pga:g} g fit")
        
    ax.set_xlabel(f"{col} drift")
    ax.set_ylabel("First-mode frequency [Hz]")
    ax.set_title(title, pad=12)
    ax.grid(alpha=.4)
    ax.legend(ncol=2, fontsize=10, frameon=True)
    plt.tight_layout()
    plt.show()

# call it just like before:
plot_direction_swapped("SW", "SW drift vs Frequency  • grouped by PGA")
plot_direction_swapped("NE", "NE drift vs Frequency  • grouped by PGA")

# ─────────────────────────────────────────────────────────────────────────────
# 4.  Stats per PGA band
#     • baseline :  drift (SW / NE) ~ 1 + Frq
#     • extended :  drift (SW / NE) ~ 1 + Frq + E_diss
# ─────────────────────────────────────────────────────────────────────────────

def add_const(x):
    return sm.add_constant(x)

print("\n── OLS per PGA band: baseline vs baseline + E_diss ──")
for pga in sorted(df["PGA"].unique()):
    sub = df[df["PGA"] == pga]

    # Skip bands with too few usable rows
    if len(sub) < 3:
        continue

    print(f"\nPGA {pga:g} g  —  N = {len(sub)}")

    for frame in ["SW", "NE"]:
        if frame not in sub.columns or sub[frame].notna().sum() < 3:
            continue

        y = sub[frame]

        # baseline: drift ~ Frq
        mdl_base = sm.OLS(y, add_const(sub["Frq"])).fit()

        # extended: drift ~ Frq + E_diss
        mdl_ext = sm.OLS(y, add_const(sub[["Frq", "E_diss"]])).fit()

        delta_r2 = mdl_ext.rsquared - mdl_base.rsquared
        print(f"  {frame}:  R²(base)={mdl_base.rsquared:.2f}  →  "
              f"R²(+E_diss)={mdl_ext.rsquared:.2f}  (Δ={delta_r2:+.2f}),  "
              f"slope_E={mdl_ext.params['E_diss']:+.3f}  "
              f"(p={mdl_ext.pvalues['E_diss']:.3f})")
