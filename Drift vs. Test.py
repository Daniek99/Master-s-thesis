# -*- coding: utf-8 -*-
"""
Created on Thu May  8 10:12:46 2025

@author: Johan Linstad
"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import re
plt.rcParams.update({
    "font.size": 16,        # Øk font-størrelse på aksetitler, ticks osv.
    "axes.titlesize": 18,   # Tittel-størrelse
    "axes.labelsize": 16,   # Aksenes label-størrelse
    "legend.fontsize": 14,  # Legende-størrelse
    "xtick.labelsize": 16,  # X-ticks størrelse
    "ytick.labelsize": 16   # Y-ticks størrelse
})

# ------------------------------------------------------------
# 0.  Klargjør DataFrame  (samme tall som sist)
# ------------------------------------------------------------
rows = [
    ("Test 00 (0.04 g)", 0.10,0.15,0.07,0.11,0.10,0.15,0.07,0.04),
    ("Test 01 (0.04 g)", 0.12,0.15,0.08,0.12,0.11,0.15,0.07,0.02),
    ("Test 02 (0.04 g)", 0.10,0.15,0.09,0.11,0.10,0.15,0.05,0.02),
    ("Test 03 (0.09 g)", 0.15,0.19,0.12,0.14,0.05,0.19,0.03,0.13),
    ("Test 04 (0.09 g)", 0.14,0.23,0.12,0.16,0.14,0.23,0.10,0.02),
    ("Test 05 (0.09 g)", 0.20,0.27,0.13,0.18,0.18,0.27,0.12,0.04),
    ("Test 06 (0.18 g)", 0.47,0.35,0.46,0.23,0.47,0.01,0.46,0.00),
    ("Test 07 (0.18 g)", 0.45,0.49,0.23,0.31,0.42,0.49,0.23,0.04),
    ("Test 08 (0.18 g)", 0.56,0.55,0.45,0.35,0.56,0.55,0.21,0.03),
    ("Test 09 (0.27 g)", 0.68,0.81,0.33,0.47,0.66,0.81,0.26,0.10),
    ("Test 10 (0.27 g)", 0.69,0.97,0.38,0.47,0.69,0.97,0.33,0.13),
    ("Test 11 (0.36 g)", 0.90,1.32,0.35,0.60,0.87,1.32,0.31,0.39),
    ("Test 12 (0.36 g)", 1.10,1.58,0.57,0.69,1.09,1.58,0.45,0.52),
    ("Test 13 (0.36 g)", 1.25,1.77,0.56,0.74,1.22,1.77,0.50,0.51),
    ("Test 14 (0.09 g)", 0.31,0.40,0.28,0.21,0.27,0.40,0.13,0.01),
    ("Test 15 (0.18 g)", 0.52,0.78,0.25,0.31,0.48,0.78,0.18,0.12),
    ("Test 16 (0.18 g)", 0.56,0.89,0.25,0.31,0.54,0.89,0.21,0.11),
    ("Test 17 (0.18 g)", 0.74,0.94,0.25,0.31,0.70,0.94,0.23,0.27),
    ("Test 18 (0.27 g)", 0.79,1.33,0.32,0.46,0.79,1.33,0.32,0.27),
    ("Test 19 (0.27 g)", 0.92,1.47,0.54,0.48,0.90,1.47,0.54,0.29),
    ("Test 20 (0.27 g)", 0.97,1.58,0.39,0.50,0.97,1.58,0.38,0.29),
    ("Test 21 (0.36 g)", 1.30,2.06,0.60,0.70,1.30,2.06,0.54,0.06),
    ("Test 22 (0.45 g)", 1.49,2.28,0.65,0.83,1.44,2.28,0.64,0.42),
    ("Test 23 (0.18 g)", 0.73,0.98,0.29,0.27,0.70,0.98,0.22,0.05),
    ("Test 24 (0.27 g)", 0.99,1.57,0.58,0.53,0.90,1.57,0.58,0.38),
    ("Test 25 (0.36 g)", 1.29,2.07,0.62,0.70,1.22,2.07,0.60,0.05),
    ("Test 26 (0.45 g)", 1.61,2.50,0.71,0.85,1.57,2.50,0.63,0.02),
    ("Test 27 (0.18 g)", 0.88,1.20,0.80,0.72,0.85,1.20,0.19,0.45),
    ("Test 28 (0.18 g)", 0.85,1.15,0.72,0.47,0.81,1.15,0.24,0.47)
]

cols = ["Test",
        "Max_1F_SW", "Max_1F_NE", "Max_2F_SW", "Max_2F_NE",
        "Same_1F_SW", "Same_1F_NE", "Same_2F_SW", "Same_2F_NE"]

df = pd.DataFrame(rows, columns=cols)

# legg til en numeric PGA-kolonne hentet fra parentesen
# riktig:
df["PGA_g"] = (
    df["Test"]
    .str.extract(r"\((0\.\d+) g\)", expand=False)   # <- NB!
    .astype(float)
)


# fargekart for bakgrunn
pga_colors = {
    0.04: "#c7d8ff",   # klarere blå
    0.09: "#c6f4bd",   # sterkere grønn
    0.18: "#ffe5a3",   # dypere gul-oransje
    0.27: "#ffc0c0",   # mer mettet rosa-rød
    0.36: "#d0c4ff",   # tydeligere lilla
    0.45: "#ffb3ff",   # NY – varm magenta-rosa
}


# ------------------------------------------------------------
# 1. Plot
# ------------------------------------------------------------
plt.figure(figsize=(14, 6))

# --- bakgrunnsstriper ---
pgas = list(df["PGA_g"]) + [None]   # liste + stoppmarkør
cur = pgas[0]
start = 0
for i, p in enumerate(pgas, start=0):
    if p != cur:                               # ny intensitet ⇒ avslutt stripe
        plt.axvspan(start-0.5, i-0.5,
                    color=pga_colors[cur], alpha=0.35, zorder=0)
        mid = (start + i - 1) / 2
        plt.text(mid, plt.gca().get_ylim()[1] * 2.5,
                 f"{cur:.2f} g", ha="center", va="bottom", fontsize=12)
        cur, start = p, i                      # start neste stripe

# -- drift-kurver (velg det du vil vise) --
series = [
    ("Max_1F_SW",  "o-", "Max 1F SW"),
    ("Max_1F_NE",  "s-", "Max 1F NE"),
    ("Max_2F_SW",  "v-", "Max 2F SW"),
    ("Max_2F_NE",  "^-", "Max 2F NE")
]

for col, style, label in series:
    plt.plot(df["Test"], df[col], style, label=label)



# ↙︎ HER er de nye linjene
plt.xlim(-0.5, len(df) - 0.5)   # ingen hvite kanter
plt.margins(x=0)                    # slå av implicit padding

# formatering
plt.xticks(rotation=65, ha="right")
plt.ylabel("Drift Δ/H [%]")
plt.title("Drift vs. Test")
plt.grid(True, linestyle="--", alpha=0.4)
plt.legend(frameon=False, 
           loc="upper left",           # forankringspunkt i legend-boksen
           bbox_to_anchor=(0.02, 0.80))
plt.subplots_adjust(left=0.01, right=0.99, top=0.90, bottom=0.20)
plt.tight_layout()
plt.show()


# ------------------------------------------------------------
# 2. Plot
# ------------------------------------------------------------
plt.figure(figsize=(14, 6))

# --- bakgrunnsstriper ---
pgas = list(df["PGA_g"]) + [None]   # liste + stoppmarkør
cur = pgas[0]
start = 0
for i, p in enumerate(pgas, start=0):
    if p != cur:                               # ny intensitet ⇒ avslutt stripe
        plt.axvspan(start-0.5, i-0.5,
                    color=pga_colors[cur], alpha=0.35, zorder=0)
        mid = (start + i - 1) / 2
        plt.text(mid, plt.gca().get_ylim()[1] * 2,
                 f"{cur:.2f} g", ha="center", va="bottom", fontsize=8)
        cur, start = p, i                      # start neste stripe

# -- drift-kurver (velg det du vil vise) --

series = [
    ("Same_1F_SW",  "o-", "Same 1F SW"),
    ("Same_1F_NE",  "s-", "Same 1F NE"),
    ("Same_2F_SW",  "v-", "Same 2F SW"),
    ("Same_2F_NE",  "^-", "Same 2F NE")
]

for col, style, label in series:
    plt.plot(df["Test"], df[col], style, label=label)

# formatering
plt.xticks(rotation=65, ha="right")
plt.ylabel("Drift Δ/H [%]")
plt.title("Drift vs. Test")
plt.grid(True, linestyle="--", alpha=0.4)
plt.legend(frameon=False)
plt.tight_layout()
plt.show()
