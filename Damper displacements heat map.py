# -*- coding: utf-8 -*-
"""
Heatmap of displacement range (MaxDisp_mm – MinDisp_mm) per Damper vs Test,
with PGA band shading in the background indicating test intensity. 
"""

import re
from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.cm import get_cmap
from matplotlib.patches import Rectangle

# === USER SETTINGS ===
SUMMARY_FILE = Path(
    r"C:\Users\danie\Documents\Master\Numerisk analyse\Tester\Alletester\displacement_summary.xlsx"
)

# === 1. Load & combine sheets ===
xls = pd.ExcelFile(SUMMARY_FILE)
df_list = []
for sheet in xls.sheet_names:
    tmp = xls.parse(sheet)
    tmp["PGA_g"] = float(sheet.replace("g", ""))
    df_list.append(tmp)
df = pd.concat(df_list, ignore_index=True)

# === 2. Compute range & pivot ===
df["Range_mm"] = df["MaxDisp_mm"] - df["MinDisp_mm"]
pivot = df.pivot_table(
    index="Damper",
    columns="Test",
    values="Range_mm",
    aggfunc="mean"
)
# sort tests numerically
ordered_tests = sorted(pivot.columns, key=lambda t: int(re.sub(r"\D", "", t)))
pivot = pivot.reindex(columns=ordered_tests)

# === 3. Determine PGA spans ===
test_to_pga = df.drop_duplicates(subset=["Test"])[["Test","PGA_g"]].set_index("Test")["PGA_g"]
ordered_pgas = [test_to_pga[t] for t in ordered_tests]

groups: Dict[float, List[int]] = {}
current = ordered_pgas[0]
start = 0
for i, p in enumerate(ordered_pgas + [None]):
    if p != current:
        groups.setdefault(current, []).append((start, i-1))
        start = i
        current = p

# PGA levels in sorted order
levels = sorted({0.09, 0.18, 0.27, 0.36, 0.45})

# grab exactly 5 maximally‐distinct colours
palette = sns.color_palette("Set1", n_colors=len(levels))

# map PGA→colour
color_map = dict(zip(levels, palette))

# === 4. Plot ===
n_rows, n_cols = pivot.shape
plt.figure(figsize=(12, 8))
sns.set(style="white")
ax = plt.gca()

# 4a. draw PGA‐band rectangles aligned to cell edges:
for pga, spans in groups.items():
    if pga is None: continue
    for (st, en) in spans:
        rect = Rectangle(
            (st, -0.5),         # (x, y) lower‐left corner
            width=en-st+1,      # number of columns in group
            height=n_rows,      # full number of rows
            facecolor=color_map[pga],
            alpha=0.1,
            edgecolor="none",
            zorder=0
        )
        ax.add_patch(rect)

# 4b. overlay heatmap
sns.heatmap(
    pivot,
    annot=True, fmt=".1f",
    cmap="Reds",
    cbar_kws={"label": "Displacement range (mm)"},
    linewidths=0.5,
    linecolor="gray",
    ax=ax,
    xticklabels=False
)

# 5. X‐ticks (centered, 90°)
n_rows, n_cols = pivot.shape
ax.set_xlim(0, n_cols)
xt = np.arange(n_cols) + 0.5
ax.set_xticks(xt)
ax.set_xticklabels(ordered_tests, rotation=90, ha="center", va="center")

# 6. Labels & title
ax.set_xlabel("Test")
ax.set_ylabel("Damper")
ax.set_title("Displacement Range per Damper and Test\n(shaded by PGA)")


from matplotlib.patches import Patch
handles = [Patch(facecolor=color_map[p], alpha=0.5, label=f"{p:.2f} g")
           for p in levels]
ax.legend(
    handles       = handles,
    title         = "PGA Levels",
    loc           = "upper center",
    bbox_to_anchor= (0.5, 1.02),             
    ncol          = len(handles),          
    frameon       = False,
    fontsize      = 8
)


plt.tight_layout()
plt.show()
