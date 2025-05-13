"""
This code aims to compare the three configurations in their capacity of limiting interstory drift.
Seeing as reduction in stiffness, expressed as frequency degradation is a major contributing factor
of increased interstory drift over the course of multiple tests, this negatively affects the recorded
experimental interstory drift values for Config 2 and 3 especially, compared to Config 1.
Therefore, frequency values are upscaled using linear models from earlier codes to 
correspondingly decrease drift values of later tests to better compare the three configurations. 
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D


# --------------------------------------------------
# R² values from “Linear-fit statistics …” table
# (picture 2 — one value per PGA-band & frame)
# --------------------------------------------------
r2_table = {                
    (0.18, 'SW'): 0.66,
    (0.18, 'NE'): 0.91,
    (0.27, 'SW'): 0.81,
    (0.27, 'NE'): 0.91,
    (0.36, 'SW'): 0.61,
    (0.36, 'NE'): 0.78,
    # 0.09 g wasn’t in the table; no bar will be drawn for it
}

# --------------------------------------------------
# 1)  Raw per-test data  ----------------------------
#     (NOTE: Frq = None for 07, 16, 19 – to be interpolated)
# --------------------------------------------------
tests = [
    # PGA  Config Test Dir Drift  Frq
    (0.09, 1, 3,  'SW', 0.15, 2.93),
    (0.09, 1, 3,  'NE', 0.19, 2.93),
    (0.09, 1, 4,  'SW', 0.14, 2.92),   # middle of batch → None
    (0.09, 1, 4,  'NE', 0.23, 2.92),
    (0.09, 1, 5,  'SW', 0.20, 2.90),
    (0.09, 1, 5,  'NE', 0.27, 2.90),

    (0.09, 2, 14, 'SW', 0.31, 2.31),
    (0.09, 2, 14, 'NE', 0.40, 2.31),

    (0.18, 1, 6,  'SW', 0.47, 2.89),   # before
    (0.18, 1, 6,  'NE', 0.35, 2.89),
    (0.18, 1, 7,  'SW', 0.45, 2.87),   # middle → None
    (0.18, 1, 7,  'NE', 0.49, 2.87),
    (0.18, 1, 8,  'SW', 0.56, 2.84),   # after
    (0.18, 1, 8,  'NE', 0.55, 2.84),

    (0.18, 2, 15, 'SW', 0.52, 2.45),   # before
    (0.18, 2, 15, 'NE', 0.78, 2.45),
    (0.18, 2, 16, 'SW', 0.56, 2.39),   # middle → None
    (0.18, 2, 16, 'NE', 0.89, 2.39),
    (0.18, 2, 17, 'SW', 0.74, 2.34),   # after
    (0.18, 2, 17, 'NE', 0.94, 2.34),

    (0.18, 3, 23, 'SW', 0.73, 2.06),   # single (before) – kept as is
    (0.18, 3, 23, 'NE', 0.98, 2.06),

    (0.27, 1,  9, 'SW', 0.68, 2.82),
    (0.27, 1,  9, 'NE', 0.81, 2.82),
    (0.27, 1, 10, 'SW', 0.69, 2.69),
    (0.27, 1, 10, 'NE', 0.97, 2.69),

    (0.27, 2, 18, 'SW', 0.79, 2.28),   # before
    (0.27, 2, 18, 'NE', 1.33, 2.28),
    (0.27, 2, 19, 'SW', 0.92, 2.28),   # middle → None
    (0.27, 2, 19, 'NE', 1.47, 2.28),
    (0.27, 2, 20, 'SW', 0.97, 2.28),   
    (0.27, 2, 20, 'NE', 1.58, 2.28),

    (0.27, 3, 24, 'SW', 0.99, 2.05),   
    (0.27, 3, 24, 'NE', 1.57, 2.05),
]

df = pd.DataFrame(
    tests,
    columns=['PGA', 'Config', 'Test', 'Dir', 'Drift', 'Frq']
)

# --------------------------------------------------
# 2)  Interpolate missing frequencies --------------
#     • Sort so rows are ordered inside each batch     #Frequency values are already interpolated in newest version
#     • Interpolate within (PGA, Config) so SW & NE
#       both get the same new value
# --------------------------------------------------
# 1️⃣  interpolate 
df['Frq'] = (
    df.groupby(['PGA', 'Config'])['Frq']
      .transform(lambda s: s.interpolate(method='linear',
                                         limit_direction='both'))
)

# 2️⃣  enforce ONE value per Test
df['Frq'] = (
    df.groupby(['PGA', 'Config', 'Test'])['Frq']
      .transform('mean')       # mean == identical because the two rows match
)


# optional sanity-check table
# print(df[['PGA','Config','Test','Dir','Frq']].to_string(index=False))

# --------------------------------------------------
# 3)
#     β₁ slopes, baseline freq, drift adjustment,
#     reduction calc, plotting, etc.
# --------------------------------------------------

# β₁ slopes ---------------------------------------------------------  
beta = { (0.18,'SW'):-0.294, (0.18,'NE'):-0.733,
         (0.27,'SW'):-0.428, (0.27,'NE'):-1.064 }  #From ID vs frq regression script

cfg1 = df[df['Config'] == 1]
baseline_freq = (cfg1.groupby(['PGA', 'Dir'])['Frq']
                    .max()
                    .dropna()
                    .to_dict())

def adjust(row):
    if row['Config'] == 1:
        return row['Drift']
    key = (row['PGA'], row['Dir'])
    slope, target = beta.get(key), baseline_freq.get(key)
    if slope is None or target is None or pd.isna(row['Frq']):
        return row['Drift']
    return row['Drift'] + slope * (target - row['Frq'])

df['Drift_adj'] = df.apply(adjust, axis=1)

# reduction ---------------------------------------------------------
bare_ref = { (0.09,'SW'):0.50, (0.09,'NE'):0.67,
             (0.18,'SW'):1.58, (0.18,'NE'):1.87,
             (0.27,'SW'):7.63, (0.27,'NE'):8.61 }

pct_reduction = lambda v,p,d: (bare_ref[(p,d)]-v)/bare_ref[(p,d)]*100
df['Reduction_orig_%'] = df.apply(
    lambda r: pct_reduction(r['Drift'], r['PGA'], r['Dir']), axis=1)
df['Reduction_adj_%'] = df.apply(
    lambda r: pct_reduction(r['Drift_adj'], r['PGA'], r['Dir']), axis=1)

# keep only 0.09-0.27 g for the plot
df_plot = df[df['PGA'].isin([0.09,0.18,0.27])].copy()



# --------------------------------------------------
# 4)  Combined plot  (same style as before) --------
# --------------------------------------------------
marker_shapes = {1:'o', 2:'s', 3:'^'}
pga_colors   = {0.09:'tab:blue', 0.18:'tab:green', 0.27:'tab:red'}

fig, ax = plt.subplots(figsize=(9, 8))

df_plot = df_plot.sort_values(['PGA','Config','Test','Dir']).reset_index(drop=True)

for y, row in df_plot.iterrows():
    ax.plot([row['Reduction_orig_%'], row['Reduction_adj_%']], [y, y],
            color='grey', alpha=0.35, linewidth=1)
    ax.scatter(row['Reduction_orig_%'], y,
               marker=marker_shapes[row['Config']], s=80,
               alpha=0.3, color=pga_colors[row['PGA']])
    ax.scatter(row['Reduction_adj_%'], y,
               marker=marker_shapes[row['Config']], s=110,
               edgecolor='black', linewidth=0.6,
               color=pga_colors[row['PGA']])
    ax.text(row['Reduction_adj_%'] + 1.2, y,
            f"C{row['Config']}-T{row['Test']}-{row['Dir']}",
            va='center', fontsize=8)
    


ax.set_title("Reduction in interstory drift \n Upgraded vs bare frame (0.09–0.27 g)")
ax.set_xlabel("Reduction (%)  –  corrected for stiffness degradation")
ax.set_yticks([])
ax.set_xlim(0, 100)
ax.grid(axis='x', linestyle='--', alpha=0.25)



config_handles = [plt.Line2D([],[],marker=m,linestyle='None',
                             label=f"Config {c}",markersize=9,
                             markeredgecolor='black',color='w')
                  for c,m in marker_shapes.items()]
pga_handles = [plt.Line2D([],[],marker='o',linestyle='None',
                          label=f"{pga:.2f} g",markersize=9,
                          color=c) for pga,c in pga_colors.items()]

# create two proxy artists for the “before” vs “after” style
orig_handle = Line2D(
    [], [], 
    color='grey', marker='o', linestyle='None',
    markersize=8, markerfacecolor='grey', alpha=0.3,
    label='Original reduction'
)
adj_handle = Line2D(
    [], [], 
    color='grey', marker='o', linestyle='None',
    markersize=8, markerfacecolor='grey', markeredgecolor='black',
    label='Adjusted reduction'
)

# 1) only config
config_legend = ax.legend(
    handles=config_handles,
    title="Configuration",
    fontsize=12,
    title_fontsize=12,
    loc="upper left",
    bbox_to_anchor=(0.02, 0.95),
    frameon=False
)
ax.add_artist(config_legend)

# 2) only PGA
pga_legend = ax.legend(
    handles=pga_handles,
    fontsize=12,
    title_fontsize=12,
    title="PGA",
    loc="upper left",
    bbox_to_anchor=(0.20, 0.95),
    frameon=False
)
ax.add_artist(pga_legend)

# 3) only orig vs. adj
oa_legend = ax.legend(
    handles=[orig_handle, adj_handle],
    title="Reduction type",
    fontsize=12,
    title_fontsize=12,
    loc="center left",
    bbox_to_anchor=(0.02, 0.65),
    frameon=False
)
ax.add_artist(oa_legend)


# tighten up so none overlap
plt.tight_layout(pad=2.0)
plt.show()
