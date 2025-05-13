# -*- coding: utf-8 -*-
"""
Batch analysis script: computes hysteresis loops, base shear from accelerations, and total energy for all tests.
Saves detailed plots, summary Excel, and combined Energy/PGA bar chart.
"""
import os
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- Plotting Function for plotting area of each hysteresis loop ---
def plot_loops_separately(disp, force, loop_indices, loop_areas, total_energy, test_number="Test", save_path=None):
    fig, ax = plt.subplots(figsize=(10, 8))
    cmap = plt.get_cmap('Blues')   #Color code of area fill
    colors = cmap(np.linspace(0.3, 1, len(loop_indices)))

    x_min, x_max = np.min(disp), np.max(disp)
    y_min, y_max = np.min(force), np.max(force)

    for idx, (start_idx, end_idx) in enumerate(loop_indices):
        d_loop = disp[start_idx:end_idx+1]
        f_loop = force[start_idx:end_idx+1]
        ax.plot(d_loop, f_loop, color=colors[idx], lw=2)
        ax.fill_between(d_loop, f_loop, color=colors[idx], alpha=0.3)

    ax.set_title(f"{test_number} - Energy Dissipation", fontsize=24)
    ax.set_xlabel("Mean displacement, 2F X-direction (mm)", fontsize=22)
    ax.set_ylabel("Base Shear (kN)", fontsize=22)
    ax.tick_params(axis='both', which='major', labelsize=20)
    ax.grid(True)
    ax.set_xlim(-50, 50)
    ax.set_ylim(-165, 165)

    ax.text(0.4, 0.95,
            f"Total $E_d$ = {total_energy/1000:.1f} kJ",
            transform=ax.transAxes,
            fontsize=24,
            verticalalignment='top',
            bbox=dict(boxstyle="round,pad=0.4", facecolor="white", edgecolor="black"))

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path)
        plt.show()
        # plt.close(fig)
    else:
        plt.show()

# --- Loop Energy Calculator. Computes the area of half of each loop and adds all together. Turned out to be the most convenient method. ---
def compute_dissipated_energy_and_loops(disp, force):
    zero_crossings = np.where(np.diff(np.sign(force)))[0]
    loop_indices = []
    loop_areas = []

    for i in range(0, len(zero_crossings) - 1, 2):
        start = zero_crossings[i]
        end = zero_crossings[i + 2] if (i + 2) < len(zero_crossings) else zero_crossings[i + 1]
        area = abs(np.trapz(force[start:end + 1], disp[start:end + 1]))
        loop_indices.append((start, end))
        loop_areas.append(area)

    total_energy = sum(loop_areas)
    return loop_indices, loop_areas, total_energy

# --- Per-file processing, computes base shear from acceleration sensors and defined masses, uses displacement sensor data from excel files ---
def force_acc(file_path, results_dir):
    base_name = os.path.basename(file_path)
    if 'Test' not in base_name:
        print(f"Skipping non-test file: {base_name}")
        return None

    xls = pd.ExcelFile(file_path)
    df = pd.read_excel(xls, sheet_name=xls.sheet_names[0])
    t0, t1 = 5, 35

    disp_cols = [c for c in df.columns if c.startswith('Disp')]
    sensors_to_remove = {
        '04': ['Disp06','Disp07'], '11': ['Disp06','Disp07'], '15': ['Disp06','Disp07'],
        '16': ['Disp06','Disp07'], '18': ['Disp06','Disp07'], '20': ['Disp06','Disp07'],
        '21': ['Disp04','Disp05'], '22': ['Disp06','Disp07'], '25': ['Disp09','Disp08'],
        '26': ['Disp09','Disp08'], '27': ['Disp14','Disp18']
    }
    raw = base_name.split('Test')[1].split('_')[0]
    if raw in sensors_to_remove:
        disp_cols = [c for c in disp_cols if c not in sensors_to_remove[raw]]

    gf_x, gf_y = 'PosA1T', 'PosA2L'
    cols = ['Time (s)'] + disp_cols
    if gf_x in df.columns: cols.append(gf_x)
    if gf_y in df.columns: cols.append(gf_y)
    df_disp = df[cols].copy()

    baseline = df_disp[df_disp['Time (s)'] <= t0].mean(numeric_only=True)
    df_disp.loc[:, disp_cols] -= baseline[disp_cols]

    for inv in ['Disp12_NE_1F_X','Disp16_NE_2F_X','Disp13_NE_1F_Y','Disp15_SW_1F_Y']:
        if inv in df_disp.columns:
            df_disp[inv] = -df_disp[inv]

    ff_x = [c for c in disp_cols if '_1F' in c and c.endswith('X')]
    sf_x = [c for c in disp_cols if '_2F' in c and c.endswith('X')]
    if gf_x in df_disp.columns:
        for c in ff_x + sf_x:
            df_disp[c] -= df_disp[gf_x]

    df_disp = df_disp[(df_disp['Time (s)'] >= t0) & (df_disp['Time (s)'] <= t1)].reset_index(drop=True)
    disp = df_disp[sf_x].mean(axis=1).values

    acc_cols = [c for c in df.columns if c.startswith('Acc') and df[c].abs().max() <= 3000]
    acc1_x = [c for c in acc_cols if '_1F' in c and c.endswith('X')]
    acc2_x = [c for c in acc_cols if '_2F' in c and c.endswith('X')]
    for c in acc1_x + acc2_x:
        if 'SW' in c:
            df[c] = -df[c]

    a1 = df[acc1_x].mean(axis=1).values * 0.01
    a2 = df[acc2_x].mean(axis=1).values * 0.01
    g_x = df['accT'].values * 0.01 if 'accT' in df.columns else np.zeros_like(a1)

    m_base = 0.65 * 1000
    m1_cm, m2_cm = 6.4 * 1000, 5.8 * 1000
    m_red, m_yel = 1.2 * 1000, 0.6 * 1000    #Floor masses pluss additional steel masses 
    m1 = m1_cm + 4*m_red + 2*m_yel
    m2 = m2_cm + 3*m_red + 3*m_yel
    m1_NE = m1_cm/2 + 2*m_red + 2*m_yel
    m1_SW = m1_cm/2 + 2*m_red
    m2_NE = m2_cm/2 + 1*m_red + 2*m_yel
    m2_SW = m2_cm/2 + 2*m_red + 1*m_yel

    def pick_mean(cols, default):
        return df[cols].mean(axis=1).values*0.01 if cols else default

    a1_NE = pick_mean([c for c in acc1_x if 'NE' in c], a1)
    a1_SW = pick_mean([c for c in acc1_x if 'SW' in c], a1)
    a2_NE = pick_mean([c for c in acc2_x if 'NE' in c], a2)
    a2_SW = pick_mean([c for c in acc2_x if 'SW' in c], a2)

    V_base = (m_base * g_x + m1_NE*a1_NE + m1_SW*a1_SW + m2_NE*a2_NE + m2_SW*a2_SW)
    mask = (df['Time (s)'] >= t0) & (df['Time (s)'] <= t1)
    force = V_base[mask] / 1000.0

    loop_indices, loop_areas, Ed = compute_dissipated_energy_and_loops(disp, force)
    test_id = 'Test' + raw
    plot_loops_separately(disp, force, loop_indices, loop_areas, Ed,
                          test_number=test_id,
                          save_path=os.path.join(results_dir, f"{test_id}_loops.png"))
    return Ed

# PGA lookup
PGA_MAP = {
    'Test02': 0.04, 'Test03': 0.09, 'Test04': 0.09, 'Test05': 0.09, 'Test06': 0.18,
    'Test07': 0.18, 'Test08': 0.18, 'Test09': 0.27, 'Test10': 0.27, 'Test11': 0.36,
    'Test12': 0.36, 'Test13': 0.36, 'Test14': 0.09, 'Test15': 0.18, 'Test16': 0.18,
    'Test17': 0.18, 'Test18': 0.27, 'Test19': 0.27, 'Test20': 0.27, 'Test21': 0.36,
    'Test22': 0.45, 'Test23': 0.18, 'Test24': 0.27, 'Test25': 0.36, 'Test26': 0.45,
    'Test27': 0.18, 'Test28': 0.18
}

# --- Batch runner ---
def main():
    base_dir = r"C:\Users\danie\Documents\Master\Numerisk analyse\Tester\Alletester"
    results_dir = os.path.join(base_dir, 'AnalysisResults')
    os.makedirs(results_dir, exist_ok=True)

    summary = []
    for file_path in glob.glob(os.path.join(base_dir, '*.xlsx')):
        Ed = force_acc(file_path, results_dir)
        if Ed is not None:
            ekj = Ed / 1000.0
            test_id = 'Test' + os.path.basename(file_path).split('Test')[1].split('_')[0]
            pga = PGA_MAP.get(test_id, np.nan)
            summary.append({'Test': test_id, 'Energy_kJ': ekj, 'PGA': pga})

    df_sum = pd.DataFrame(summary)
    df_sum['Num'] = df_sum['Test'].str.extract(r'Test(\d+)').astype(int)
    df_sum.sort_values('Num', inplace=True)
    df_sum.drop(columns=['Num'], inplace=True)

    excel_file = os.path.join(results_dir, 'Summary_Energy.xlsx')
    df_sum.to_excel(excel_file, index=False)
    print(f"Summary saved to: {excel_file}")

    # fig, ax1 = plt.subplots(figsize=(12, 6))
    # x = np.arange(len(df_sum))
    # ax1.set_xticks(x)
    # ax1.set_xticklabels(df_sum['Test'], rotation=90)
    # bars1 = ax1.bar(x, df_sum['Energy_kJ'], color='skyblue', label='Energy (kJ)')
    # for i, bar in enumerate(bars1):
    #     ax1.text(bar.get_x() + bar.get_width() / 2, -df_sum['Energy_kJ'].max() * 0.05,
    #              df_sum['Test'].iloc[i], ha='center', va='top', rotation=90, fontsize=8)
    # ax1.set_ylabel('Energy (kJ)')
    # for bar in bars1:
    #     yval = bar.get_height()
    #     ax1.text(bar.get_x() + bar.get_width()/2, yval + 0.5, f"{yval:.1f}",
    #              ha='center', va='bottom', fontsize=8)

    # ax2 = ax1.twinx()
    # bars2 = ax2.bar(x, df_sum['PGA'], width=0.4, color='salmon', align='center', label='PGA (g)', alpha=0.5)
    # ax2.set_ylim(4.5, 0)
    # ax2.set_ylabel('PGA (g)')
    # for bar in bars2:
    #     yval = bar.get_height()
    #     ax2.text(bar.get_x() + bar.get_width()/2, yval - 0.02, f"{yval:.2f}",
    #              ha='center', va='top', color='black', fontsize=8)

    # pos = ax1.get_position()
    # band_height = pos.height * 0.2
    # ax2.set_position([pos.x0, pos.y0 + pos.height - band_height, pos.width, band_height])
    # ax2.set_frame_on(False)
    # ax2.set_xticks([])

    # fig.subplots_adjust(bottom=0.20)
    # plt.title('Dissipated Energy and PGA per Test')
    # chart_file = os.path.join(results_dir, 'Energy_PGA.png')
    # plt.savefig(chart_file, bbox_inches='tight')
    # print(f"Chart saved to: {chart_file}")
    
    
    #UNCOMMENT ^ TO plot bar chart of total energy dissipated per test

if __name__ == '__main__':
    main()
