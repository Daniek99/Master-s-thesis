# energy_dissipation_plot.py
"""
Visualiserer energi‑ og frekvensdata fra shaketable‑tester.

* **Grå søyle**   = total dissipert energi (Base‑shear)
* **Oransje søyle** = AFC‑dissipert energi (subset av totalen)
* **Punktmarkør**   = initial modal frekvens (markør / farge ≈ Config)
* **Farget bakgrunn** = PGA‑område (0.04 g → 0.45 g) med tekst øverst

Bruk `load_dataframe(sort_by="AFC_kJ")` _(standard)_ eller
`sort_by="BaseShear_kJ"` for å sortere på total energi.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import Iterable, Tuple, Optional, Dict

# ---------------------------------------------------------------------------
# 1  Rådata
# ---------------------------------------------------------------------------
RAW_DATA = [
    # Config, PGA_g, Test, BaseShear_kJ, AFC_kJ, Freq_Hz, Drift1F_mm, Drift2F_mm
    [1, 0.04, "Test02",  0.4,  0.0, 3.02, 0.252429641, 0.18354932],
    [1, 0.09, "Test03",  0.8,  0.0, 2.89, 0.344778922, 0.230903188],
    [1, 0.09, "Test04",  1.4,  0.0, 2.92, 0.485684447, 0.32992916],
    [1, 0.09, "Test05",  1.7,  0.0, 2.90, 0.501650577, 0.328967544],
    [2, 0.09, "Test14",  2.9,  0.6, 2.52, 0.705614094, 0.376661798],
    [1, 0.18, "Test06",  3.0,  0.5, 2.89, 0.693240788, 0.485677046],
    [1, 0.18, "Test07",  5.1,  1.4, 2.87, 0.815787188, 0.52576787],
    [1, 0.18, "Test08",  6.0,  2.0, 2.84, 0.952406917, 0.617766464],
    [2, 0.18, "Test15",  8.7,  3.6, 2.45, 1.412046932, 0.637872809],
    [2, 0.18, "Test16", 10.3,  4.4, 2.39, 1.542708015, 0.634039424],
    [2, 0.18, "Test17", 11.4,  5.0, 2.34, 1.563631874, 0.604437673],
    [3, 0.18, "Test23",  9.7,  4.2, 2.05, 1.870069295, 0.573182555],
    [1, 0.27, "Test09", 11.3,  6.1, 2.82, 1.217636606, 0.708955886],
    [1, 0.27, "Test10", 15.7, 11.5, 2.69, 1.551747265, 0.773938546],
    [2, 0.27, "Test18", 18.5,  8.7, 2.28, 2.234710206, 0.810855938],
    [2, 0.27, "Test19", 22.2, 10.6, 2.28, 2.362225824, 0.814614835],
    [2, 0.27, "Test20", 24.5, 11.6, 2.28, 2.583528175, 0.853381109],
    [3, 0.27, "Test24", 21.3,  9.9, 2.05, 2.771883566, 0.831390851],
    [1, 0.36, "Test11", 27.1, 22.1, 2.56, 2.414591085, 1.066265856],
    [1, 0.36, "Test12", 31.7, 27.2, 2.48, 2.789953906, 1.072756379],
    [1, 0.36, "Test13", 36.7, 32.8, 2.39, 3.291774267, 1.124017312],
    [2, 0.36, "Test21", 42.0, 20.2, 2.28, 3.215229147, 1.076677738],
    [3, 0.36, "Test25", 44.6, 16.3, 2.02, 3.58910893 , 1.037698393],
    [2, 0.45, "Test22", 51.1, 24.2, 2.15, 4.117414328, 1.244380888],
    [3, 0.45, "Test26", 64.8, 22.7, 1.98, 4.381482398, 1.21513786],
]

COLUMNS = ["Config", "PGA_g", "Test", "BaseShear_kJ", "AFC_kJ", "Freq_Hz"]
CFG_MARKERS = {1: "o", 2: "s", 3: "v"}
CFG_COLORS  = {1: "#0072b2", 2: "#d55e00", 3: "#cc79a7"}
PGA_COLORS  = {
    0.04: "#e6f2ff", 0.09: "#e8f9e5", 0.18: "#fff7e6",
    0.27: "#fde9e9", 0.36: "#ede5f5", 0.45: "#f3e6ff",
}

# ---------------------------------------------------------------------------
# 2  Databehandling
# ---------------------------------------------------------------------------

def load_dataframe(
    raw: Iterable[Iterable] = RAW_DATA,
    *,
    sort_by: str = "AFC_kJ",  # «AFC_kJ» eller «BaseShear_kJ»
    ascending: bool = True,
) -> pd.DataFrame:
    if sort_by not in {"AFC_kJ", "BaseShear_kJ"}:
        raise ValueError("sort_by må være 'AFC_kJ' eller 'BaseShear_kJ'")
    df = pd.DataFrame(raw, columns=COLUMNS)
    df["TestNo"] = df["Test"].str.extract(r"(\d+)").astype(int)
    return df.sort_values([sort_by, "TestNo"], ascending=ascending).reset_index(drop=True)

# ---------------------------------------------------------------------------
# 3  Plotting
# ---------------------------------------------------------------------------

def _add_pga_background(ax: plt.Axes, pga: pd.Series) -> None:
    """Legg halvtransparente vertikale striper og PGA‑tekst."""
    current = pga.iloc[0]
    start   = 0
    for i in range(1, len(pga) + 1):
        if i == len(pga) or pga.iloc[i] != current:
            end = i - 1
            ax.axvspan(start - 0.5, end + 0.5, color=PGA_COLORS.get(current, "#f0f0f0"), alpha=0.35, zorder=0)
            mid = (start + end) / 2
            ax.text(mid, ax.get_ylim()[1] * 1.02, f"{current:.2f} g", ha="center", va="bottom", fontsize=8)
            if i < len(pga):
                current = pga.iloc[i]
                start   = i


def plot_energy_vs_freq(
    df: pd.DataFrame,
    *,
    figsize: Tuple[int, int] = (14, 4),
    ylim_energy: Optional[Tuple[float, float]] = None,
    ylim_freq:   Optional[Tuple[float, float]] = None,
) -> plt.Figure:
    idx = np.arange(len(df))
    fig, ax1 = plt.subplots(figsize=figsize)

    # Energi‑søyler først (for å få korrekt y‑topp før bakgrunn‑tekst)
    ax1.bar(idx, df["BaseShear_kJ"], color="lightgray", alpha=0.6, label="Base‑shear energy")
    ax1.bar(idx, df["AFC_kJ"], width=0.6, color="#ffa500", label="AFC dissipated energy")
    for i, val in enumerate(df["AFC_kJ"]):
        ax1.text(i, val + 0.5, f"{val:.1f}", ha="center", va="bottom", fontsize=7)

    # Bakgrunnsstriper etter at y‑grense finnes
    _add_pga_background(ax1, df["PGA_g"])

    ax1.set_ylabel("Energy dissipated [kJ]")
    ax1.set_xticks(idx)
    ax1.set_xticklabels(df["Test"], rotation=45, ha="right")
    ax1.set_xlabel("Test (sorted)")

    # Frekvens‑akse
    ax2 = ax1.twinx()
    for cfg in df["Config"].unique():
        mask = df["Config"] == cfg
        ax2.plot(idx[mask], df.loc[mask, "Freq_Hz"], linestyle="", marker=CFG_MARKERS[cfg],
                 markersize=6, color=CFG_COLORS[cfg], label=f"Freq (Config {cfg})")
    for i, val in enumerate(df["Freq_Hz"]):
        ax2.text(i, val + 0.02, f"{val:.2f}", ha="center", va="bottom", fontsize=6)
    ax2.set_ylabel("Initial modal frequency [Hz]")

    # Aksegrenser
    if ylim_energy:
        ax1.set_ylim(*ylim_energy)
    if ylim_freq:
        ax2.set_ylim(*ylim_freq)
    else:
        ax1.set_ylim(bottom=-0.5)

    # Legend
    handles1, labels1 = ax1.get_legend_handles_labels()
    handles2, labels2 = ax2.get_legend_handles_labels()
    handles, labels   = handles1 + handles2, labels1 + labels2
    ncol = max(2, len(labels) // 2)
    ax1.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.5, 1.15), ncol=ncol, frameon=False)

    plt.title("Energy Dissipation vs Initial Frequency")
    plt.tight_layout()
    return fig

# ---------------------------------------------------------------------------
# 4  Demo‑kjøring
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    df_default = load_dataframe()
    plot_energy_vs_freq(df_default)
    plt.show()
