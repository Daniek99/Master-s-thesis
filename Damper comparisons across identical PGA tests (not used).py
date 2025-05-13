# -*- coding: utf-8 -*-
"""
This script generates overlay displacement curves per damper for every shake‑table test at the same
PGA level within a config.

--------------------------------------------------------------------------
Normalization logic:

1. `Disp2_norm = Disp[2] − Disp[2][0]`   (only if the matching column exists)
2. `corrected  = Disp[1] − Disp2_norm`    → removes rigid‑frame motion
3. `rel      = corrected − corrected[0]`  → every curve starts at 0 mm
"""

import re
from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# =============================== SETTINGS ===================================
DATA_FOLDER = Path(r"C:\Users\danie\Documents\Master\Numerisk analyse\Tester\Config1Disp[1]")
SELECT_PGA_VALUES = [0.36]  # change as needed
THRESHOLD = 0.4            # mm – filter out flat/noisy traces
LINE_ALPHA       = 0.4 
SAVE_PLOTS = False       # True ⇒ write PNGs
RUN_INDIVIDUAL = False     # set True if you still want the per‑test plots

# Mapping Test label → PGA (g)
TEST_INTENSITY_LOOKUP: Dict[str, float] = {
    "Test02": 0.04, "Test03": 0.09, "Test04": 0.09, "Test05": 0.09,
    "Test06": 0.18, "Test07": 0.18, "Test08": 0.18, "Test09": 0.27,
    "Test10": 0.27, "Test11": 0.36, "Test12": 0.36, "Test13": 0.36,
    "Test14": 0.09, "Test15": 0.18, "Test16": 0.18, "Test17": 0.18,
    "Test18": 0.27, "Test19": 0.27, "Test20": 0.27, "Test21": 0.36,
    "Test22": 0.45, "Test23": 0.18, "Test24": 0.27, "Test25": 0.36,
    "Test26": 0.45, "Test27": 0.18, "Test28": 0.18,
}

OVERLAY_FOLDER = DATA_FOLDER / "OverlayPlots"
OVERLAY_FOLDER.mkdir(exist_ok=True)

# =============================================================================
# ---------------------------  Helper functions  ------------------------------
# =============================================================================

def process_file(file_path: Path, thresh: float = THRESHOLD):
    df = pd.read_excel(file_path, sheet_name=0)

    if "Time (s)" not in df.columns:
        raise ValueError("Missing 'Time (s)' column in " + file_path.name)

    disp1_cols = [c for c in df.columns if c.startswith("Disp[1]")]
    disp2_cols = [c for c in df.columns if c.startswith("Disp[2]")]
    if not disp1_cols:
        raise ValueError("No 'Disp[1]' columns found in " + file_path.name)

    df_adj = pd.DataFrame(index=df.index)
    valid_cols: List[str] = []

    for col1 in disp1_cols:
        suffix = col1.split("Disp[1]")[-1]
        col2 = f"Disp[2]{suffix}"

        # --- Step 1: normalise Disp[2] to its own t=0 (if available) ---
        if col2 in disp2_cols:
            disp2_norm = df[col2] - df[col2].iloc[0]
            corrected = df[col1] - disp2_norm   # Step 2: subtract
        else:
            corrected = df[col1].copy()

        # --- Step 3: normalise corrected signal to its own t=0 ---
        rel = corrected - corrected.iloc[0]

        # Keep only if it moves beyond ±THRESHOLD
        if (rel.max() >= thresh) or (rel.min() <= -thresh):
            df_adj[col1] = rel
            valid_cols.append(col1)

    return {
        "time": df["Time (s)"],
        "df_adj": df_adj,
        "valid_cols": valid_cols,
    }

# =============================================================================
# -------------------------------  Plotting  ----------------------------------
# =============================================================================

def overlay_by_damper(results: Dict[str, dict], pga_values):
    damper_names = sorted({c for d in results.values() for c in d["valid_cols"]},
                          key=lambda c: (c.endswith("2F"), c))

    colour_cycle = plt.rcParams["axes.prop_cycle"].by_key()["color"]
    test_to_colour = {t: colour_cycle[i % len(colour_cycle)]
                      for i, t in enumerate(sorted(results))}

    pga_str = ", ".join(f"{p:.2f} g" for p in sorted(pga_values))

    for damper in damper_names:
        plt.figure(figsize=(12, 4))
        has_data = False

        for test_label, data in sorted(results.items()):
            if damper not in data["valid_cols"]:
                continue
            has_data = True
            plt.plot(data["time"], data["df_adj"][damper],
                     label=test_label, color=test_to_colour[test_label], alpha=LINE_ALPHA), 

        if not has_data:
            plt.close(); continue

        plt.title(f"{damper} – displacement overlay – {pga_str}")
        plt.xlabel("Time (s)")
        plt.ylabel("Displacement (mm)")
        plt.grid(True, which="both", ls="--", lw=0.4)
        plt.legend(loc="upper left", ncol=4, fontsize=8)
        plt.tight_layout()

        if SAVE_PLOTS:
            out_dir = OVERLAY_FOLDER / pga_str.replace(" ", "")
            out_dir.mkdir(exist_ok=True)
            plt.savefig(out_dir / f"{damper}_overlay.png", dpi=300)
        plt.show()

# =============================================================================
# --------------------------------  Main  ------------------------------------
# =============================================================================

def main():
    wanted_pgas = set(np.round(SELECT_PGA_VALUES, 2))
    results: Dict[str, dict] = {}

    for fpath in DATA_FOLDER.glob("*.xlsx"):
        m = re.search(r"(Test\d+)", fpath.name)
        if not m:
            continue
        test_label = m.group(1)
        pga = TEST_INTENSITY_LOOKUP.get(test_label)
        if pga is None or np.round(pga, 2) not in wanted_pgas:
            continue
        try:
            results[test_label] = process_file(fpath)
        except Exception as exc:
            print(f"⚠️  Skipping {fpath.name}: {exc}")

    if not results:
        print("No files matched the requested PGA level(s).")
        return

    overlay_by_damper(results, wanted_pgas)

    if RUN_INDIVIDUAL:
        print("Running individual per‑test plots (not shown here)…")
    


if __name__ == "__main__":
    main()
