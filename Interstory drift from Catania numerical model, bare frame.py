"""

This code inputs the numerical data from Catania, used in simulations to estimate interstory drift and TAF
for a bare concrete frame of identical dimensions as in the experiment. 
"""

import pandas as pd
import numpy as np
import re

FILE = "Kopi av Displacement of Bare frame.xlsx"
STOREY_HEIGHT = 2000.0  # mm

# ------------------------------------------------------------------
# 1)  Read raw sheet  (no headers) ---------------------------------
# ------------------------------------------------------------------
raw = pd.read_excel(FILE, header=None)

# Header rows 3 & 4 identify the node and coordinate
hdr3 = raw.iloc[3]     # e.g. "Node 103"
hdr4 = raw.iloc[4]     # e.g. "X"

def col_of(node, coord='X'):
    match = np.where((hdr3 == node) & (hdr4 == coord))[0]
    if len(match):
        return int(match[0])
    raise ValueError(f"{node} {coord} column not found")

col_time = 1
col_103x = col_of("Node 103", "X")
col_107x = col_of("Node 107", "X")

# ------------------------------------------------------------------
# 2)  Build numeric DataFrame --------------------------------------
# ------------------------------------------------------------------
df = raw[[col_time, col_103x, col_107x]].copy()
df.columns = ["time", "n103_x", "n107_x"]
df = df.apply(pd.to_numeric, errors="coerce").dropna(subset=["time"])

# ------------------------------------------------------------------
# 3)  Locate block boundaries  (time drops back) -------------------
# ------------------------------------------------------------------
time_jump = df["time"].diff()           # forward difference
reset_idx = df.index[time_jump < -0.5].tolist()   # any drop ≥0.5 s
reset_idx = [df.index[0]] + reset_idx + [df.index[-1]+1]  # sentinel

records = []
for i in range(len(reset_idx)-1):
    start, end = reset_idx[i], reset_idx[i+1]
    block = df.loc[start:end-1].reset_index(drop=True)
    if block.empty:
        continue

    # baseline = first value in the block
    base103 = block.at[0, "n103_x"]
    base107 = block.at[0, "n107_x"]

    max103 = (block["n103_x"] - base103).abs().max()
    max107 = (block["n107_x"] - base107).abs().max()

    drift103 = max103  / STOREY_HEIGHT * 100   # → %
    drift107 = max107  / STOREY_HEIGHT * 100

    # best guess PGA label = text just above the block
    header_row = raw.loc[:start-1, 0].last_valid_index()
    hdr_txt = str(raw.at[header_row, 0]) if header_row is not None else ''
    m = re.search(r"PGA\s*=\s*([0-9.]+)", hdr_txt)
    pga = m.group(1) if m else f"Block {i+1}"

    records.append(dict(
        Step=i+1,
        PGA=pga,
        Max103_mm=round(max103, 3),
        Drift103_pct=round(drift103, 3),
        Max107_mm=round(max107, 3),
        Drift107_pct=round(drift107, 3)
    ))

result = pd.DataFrame(records)
pd.set_option("display.float_format", "{:.3f}".format)

print("\nMaximum first-storey inter-storey drift per PGA block\n")
print(result.to_string(index=False))
