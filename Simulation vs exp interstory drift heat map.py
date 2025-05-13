
#Generates heat map comparing values of experimental interstory drift for each configuration to simulated values

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm

# ────────────────────────────────────────────────────────────────────
# 0)  global font settings – make everything larger
# ────────────────────────────────────────────────────────────────────
plt.rcParams.update({
    "font.size": 18,        # base size for text
    "axes.titlesize": 20,
    "axes.labelsize": 18,
    "xtick.labelsize": 18,
    "ytick.labelsize": 18,
})

# ────────────────────────────────────────────────────────────────────
# 1)  SIMULATED BASELINES 
# ────────────────────────────────────────────────────────────────────
sim_df_cf1 = pd.DataFrame({
    "PGA":   [0.09, 0.18, 0.27, 0.36],
    "North": [0.11, 0.61, 2.13, 10.61],
    "South": [0.10, 0.55, 2.13,  9.99],
}).set_index("PGA")

sim_df_cf2 = pd.DataFrame({
    "PGA":   [0.09, 0.18, 0.27, 0.36],
    "North": [0.08, 0.54, 2.07,  8.54],
    "South": [0.12, 0.62, 1.87,  8.04],
}).set_index("PGA")

# ────────────────────────────────────────────────────────────────────
# 2)  EXPERIMENTAL DRIFTS  (Config 1 & 2, no 0.45 g)
# ────────────────────────────────────────────────────────────────────
exp_rows = [
    #  PGA ,Cfg, Test,  North , South
    (0.09,1,"T03",0.19,0.15),(0.09,1,"T04",0.23,0.14),
    (0.18,1,"T06",0.35,0.47),(0.18,1,"T07",0.49,0.45),(0.18,1,"T08",0.55,0.56),
    (0.27,1,"T09",0.81,0.68),(0.27,1,"T10",0.97,0.69),
    (0.36,1,"T11",1.32,0.90),(0.36,1,"T12",1.58,1.10),(0.36,1,"T13",1.77,1.25),

    (0.09,2,"T14",0.40,0.31),
    (0.18,2,"T15",0.78,0.52),(0.18,2,"T16",0.89,0.56),(0.18,2,"T17",0.94,0.74),
    (0.27,2,"T18",1.33,0.79),(0.27,2,"T19",1.47,0.92),(0.27,2,"T20",1.58,0.97),
    (0.36,2,"T21",2.06,1.30),
]
exp_df = pd.DataFrame(exp_rows,
                      columns=["PGA","Config","Test","North","South"])

# -------------------------------------------------------------------
# Helper: ALWAYS-safe TwoSlopeNorm    Helper function to bypass twoslopenorm error
# -------------------------------------------------------------------
def safe_norm(dev_df, clip=100):
    """
    Return a TwoSlopeNorm centred at 0 that *never* violates the rule
    vmin < vcenter < vmax, even if the matrix is constant or full of NaNs.

    Parameters
    ----------
    dev_df : pandas.DataFrame  -- signed deviation (%)
    clip   : float             -- absolute maximum for colour scale
    """
    # ignore NaNs when looking for extents, for an earlier version of the code where certain driftvalues were "nan"
    try:
        vmin = np.nanmin(dev_df.values)
        vmax = np.nanmax(dev_df.values)
    except ValueError:          # dev_df was entirely NaN
        vmin = vmax = 0.0

    span = max(abs(vmin), abs(vmax))

    # case A: every entry is NaN  → span == 0 and NaN min/max handled
    # case B: all zeros           → span == 0
    # case C: all positive (no negatives)
    # case D: all negative (no positives)
    # case E: mixed signs (normal)

    if span == 0 or np.isnan(span):            # A or B
        return TwoSlopeNorm(vmin=-1.0, vcenter=0.0, vmax=1.0)

    span = min(span, clip)

    if vmin >= 0:                              # C  (shift tiny bit below 0)
        vmin_plot = -0.01 * span or -1e-3
        vmax_plot =  span
    elif vmax <= 0:                            # D  (shift tiny bit above 0)
        vmin_plot = -span
        vmax_plot =  0.01 * span or 1e-3
    else:                                      # E  (normal)
        vmin_plot = -span
        vmax_plot =  span

    # final sanity check
    if not (vmin_plot < 0 < vmax_plot):
        vmin_plot, vmax_plot = -1.0, 1.0

    return TwoSlopeNorm(vmin=vmin_plot, vcenter=0.0, vmax=vmax_plot)

# ────────────────────────────────────────────────────────────────────
# 4)  Build long “Sim / C1 / C2” table for one side
# ────────────────────────────────────────────────────────────────────
def long_table(side):
    recs = []
    for _, r in exp_df.iterrows():
        cfg, pga, test = r.Config, r.PGA, r.Test
        label = f"{pga:.2f}g {test}"
        sim_val = (sim_df_cf1 if cfg == 1 else sim_df_cf2).loc[pga, side]
        rec = dict(Row=label, Sim=sim_val, C1=np.nan, C2=np.nan)
        rec[f"C{cfg}"] = r[side]
        recs.append(rec)
    vals = (pd.DataFrame(recs)
              .set_index("Row")[["Sim","C1","C2"]])
    dev  = (vals.sub(vals["Sim"], axis=0)
                 .div(vals["Sim"], axis=0) * 100)
    dev["Sim"] = 0.0
    return vals, dev

north_vals, north_dev = long_table("North")
south_vals, south_dev = long_table("South")

# ────────────────────────────────────────────────────────────────────
# 5)  Plot helper
# ────────────────────────────────────────────────────────────────────
def heat(ax, vals, dev, title, annot_size=16):
    im = ax.imshow(dev.clip(-100,100), cmap="bwr", norm=safe_norm(dev), aspect="auto")
    ax.set_xticks(range(len(vals.columns)))
    ax.set_xticklabels(vals.columns, fontsize=16, weight='bold')
    ax.set_yticks(range(len(vals.index)))
    ax.set_yticklabels(vals.index, fontsize=16)
    ax.set_xlabel("Configuration", weight='bold')
    ax.set_title(title, fontsize=16, weight='bold', pad=10)

    # annotate every filled cell
    for i in range(vals.shape[0]):
        for j in range(vals.shape[1]):
            v = vals.iat[i, j]
            if np.isnan(v): continue
            bg = im.cmap(im.norm(dev.iat[i, j]))
            lum = 0.299*bg[0] + 0.587*bg[1] + 0.114*bg[2]
            ax.text(j, i, f"{v:.2f}%", ha="center", va="center",
                    fontsize=annot_size, fontweight='bold',
                    color=("black" if lum > 0.6 else "white"))
    return im

# ────────────────────────────────────────────────────────────────────
# 6)  Draw figure with colour-bar on the far right
# ────────────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(14, 8))

# 1×3 grid: left map, colorbar, right map
# width_ratios: make the center col tiny, left & right equal
gs = fig.add_gridspec(
    1, 3,
    width_ratios=[1, 0.05, 1],
    wspace=0.4   # more horizontal gap between heatmaps
)

axN = fig.add_subplot(gs[0, 0])
axC = fig.add_subplot(gs[0, 1])
axS = fig.add_subplot(gs[0, 2])

# Draw the two heatmaps
imN = heat(axN, north_vals, north_dev, "North frame")
imS = heat(axS, south_vals, south_dev, "South frame")

# Shared Y label
axN.set_ylabel("PGA  &  Test ID", weight='bold')

# 1) SHRINK the colorbar to 85% of the axis height
# 2) NUDGE it slightly left within its axes by adjusting its aspect ratio
cbar = fig.colorbar(
    imS, cax=axC,
    shrink=0.85,      # 85% of full height
)
# shift the colorbar ticks & label slightly left:
cbar.ax.yaxis.set_ticks_position('left')
cbar.ax.yaxis.set_label_position('left')
cbar.ax.tick_params(pad=2)  # move tick labels a bit closer
cbar.set_label(
    "Signed deviation (%)  (clipped at ±100)",
    fontsize=16, weight='bold', labelpad=5
)

# 1) Two‐line suptitle moved a bit lower (y=0.95 instead of 0.99)
fig.suptitle(
    "Simulated vs experimental interstory drifts (%)\n"
    "Deviation from simulated values indicated by color",
    fontsize=20, weight="bold",
    y=0.95,           # lower it so there's room underneath
    linespacing=1.2
)

# 2) Give each subplot title more pad 
for ax in (axN, axS):
    ax.set_title(ax.get_title(), pad=30)  

# 3) Tell Matplotlib to reserve only ~80% of the figure height for the axes,
#    leaving 20% free up top for the supertitle + padding
fig.subplots_adjust(
    left=0.10,   
    top=0.80,
    right=0.95,
    wspace=0)

plt.show()