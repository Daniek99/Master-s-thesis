


import pandas as pd
import matplotlib.pyplot as plt

# Load the Excel file
file_path = "Data catania.xlsx"
xls = pd.ExcelFile(file_path)

# Parse and structure data
df_raw = xls.parse(xls.sheet_names[0], skiprows=4)
df_raw.columns = [
    'Step', 'Time', 'Node103_X', 'Node103_Z', 'Node107_X', 'Node107_Z',
    'Node203_X', 'Node203_Z', 'Node207_X', 'Node207_Z'
] + [f'Other_{i}' for i in range(len(df_raw.columns) - 10)]

df = df_raw[['Step', 'Time', 'Node103_X', 'Node107_X', 'Node203_X', 'Node207_X']].copy()
df['Step'] = df['Step'].fillna(method='ffill')

# Convert numeric values
for col in df.columns[1:]:
    df[col] = pd.to_numeric(df[col], errors='coerce')

height = 2000  # mm
steps = df['Step'].dropna().unique()

# Plot for each step
for step in steps:
    df_step = df[df['Step'] == step].copy()
    time = df_step['Time']

    # NW corner (Node 103 and 203)
    drift_NW_1F = df_step['Node103_X'] / height
    drift_NW_2F = (df_step['Node203_X'] - df_step['Node103_X']) / height

    max_NW_1F = drift_NW_1F.abs().max() * 100
    time_NW_1F = time[drift_NW_1F.abs().idxmax()]
    max_NW_2F = drift_NW_2F.abs().max() * 100
    time_NW_2F = time[drift_NW_2F.abs().idxmax()]

    # SE corner (Node 107 and 207)
    drift_SE_1F = df_step['Node107_X'] / height
    drift_SE_2F = (df_step['Node207_X'] - df_step['Node107_X']) / height

    max_SE_1F = drift_SE_1F.abs().max() * 100
    time_SE_1F = time[drift_SE_1F.abs().idxmax()]
    max_SE_2F = drift_SE_2F.abs().max() * 100
    time_SE_2F = time[drift_SE_2F.abs().idxmax()]

    # Plot
    fig, ax = plt.subplots(figsize=(6, 6))

    # NW corner - stepped line
    ax.plot([max_NW_1F, max_NW_1F], [0, 2], color='blue')
    ax.plot([max_NW_1F, max_NW_2F], [2, 2], color='blue', label='Drift x-direction - corner NW')
    ax.plot([max_NW_2F, max_NW_2F], [2, 4], color='blue')
    ax.text(max_NW_1F, 2.05, f"{max_NW_1F:.4f}%", color='blue')
    ax.text(max_NW_2F, 4.05, f"{max_NW_2F:.4f}%", color='blue')

    # SE corner - stepped line
    ax.plot([max_SE_1F, max_SE_1F], [0, 2], color='orange')
    ax.plot([max_SE_1F, max_SE_2F], [2, 2], color='orange', label='Drift x-direction - corner SE')
    ax.plot([max_SE_2F, max_SE_2F], [2, 4], color='orange')
    ax.text(max_SE_1F, 2.2, f"{max_SE_1F:.4f}%", color='orange')
    ax.text(max_SE_2F, 4.2, f"{max_SE_2F:.4f}%", color='orange')

    ax.set_yticks([0, 2, 4])
    ax.set_yticklabels(["0 m (Ground)", "2 m (1st Floor)", "4 m (2nd Floor)"])
    ax.set_xlabel("Interstory Drift % (Δ/H)")
    ax.set_ylabel("Height [m]")
    ax.set_xlim(0, max(max_NW_1F, max_NW_2F, max_SE_1F, max_SE_2F) * 1.4)
    ax.set_title(f"{step} - Driftprofile (X-dir)\nNW peak: {time_NW_2F:.2f}s, SE peak: {time_SE_2F:.2f}s")
    ax.legend()
    ax.grid(True)
    plt.tight_layout()
    plt.show()
