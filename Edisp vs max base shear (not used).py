import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import linregress

# Data from the provided table (excluding Test11)
data = {
    'Test': ['Test02', 'Test03', 'Test04', 'Test05', 'Test06', 'Test07', 'Test08', 'Test09', 'Test10',
             'Test12', 'Test13', 'Test14', 'Test15', 'Test16', 'Test17', 'Test18', 'Test19', 'Test20',
             'Test21', 'Test22', 'Test23', 'Test24', 'Test25', 'Test26'],
    'Energy_kJ': [0.41, 0.75, 1.43, 1.74, 3.02, 5.07, 6.03, 11.30, 15.67, 31.75, 36.66, 2.92, 8.71,
                  10.30, 11.37, 18.46, 22.21, 24.47, 42.04, 51.08, 9.74, 21.34, 44.60, 64.83],
    'MaxShear_kN': [15.77, 22.46, 32.44, 35.02, 47.19, 61.89, 70.46, 84.91, 89.84, 104.33, 117.01,
                    36.97, 46.36, 53.60, 58.03, 77.26, 87.33, 93.16, 124.95, 144.49, 50.99, 78.99,
                    116.24, 142.82],
    'PGA': [0.04, 0.09, 0.09, 0.09, 0.18, 0.18, 0.18, 0.27, 0.27, 0.36, 0.36, 0.09, 0.18, 0.18,
            0.18, 0.27, 0.27, 0.27, 0.36, 0.45, 0.18, 0.27, 0.36, 0.45]
}

# Create DataFrame
df = pd.DataFrame(data)

# Group by PGA
pga_groups = df.groupby('PGA')

# Create figure with subplots (2 rows, 3 columns to accommodate all PGA levels)
fig, axes = plt.subplots(2, 3, figsize=(15, 10), sharex=True, sharey=True)
axes = axes.flatten()  # Flatten for easier iteration

# Define PGA levels to plot
pga_levels = sorted(df['PGA'].unique())

# Plot for each PGA level
for i, pga in enumerate(pga_levels):
    if i >= len(axes):  # Skip if more PGA levels than subplots
        break
    ax = axes[i]
    group = pga_groups.get_group(pga)

    # Scatter plot
    ax.scatter(group['Energy_kJ'], group['MaxShear_kN'], color='blue', label='Tests')

    # Add test labels
    for j, test in enumerate(group['Test']):
        ax.text(group['Energy_kJ'].iloc[j] + 0.5, group['MaxShear_kN'].iloc[j], test, fontsize=14)

    # Linear regression
    if len(group) > 1:  # Need at least 2 points for regression
        slope, intercept, r_value, p_value, std_err = linregress(group['Energy_kJ'], group['MaxShear_kN'])
        line = slope * group['Energy_kJ'] + intercept
        ax.plot(group['Energy_kJ'], line, color='red', label=f'Fit: y = {slope:.2f}x + {intercept:.2f}')

    # Customize subplot
    ax.set_title(f'PGA = {pga}g')
    ax.grid(True)
    ax.legend()

# Set common labels
fig.text(0.5, 0.04, 'Energy (kJ)', ha='center', fontsize=18)
fig.text(0.04, 0.5, 'Max Shear (kN)', va='center', rotation='vertical', fontsize=18)

# Adjust layout
plt.suptitle('Energy dissipation vs. Max Shear by PGA Level', fontsize=18)
plt.tight_layout(rect=[0.05, 0.05, 1, 0.95])

# Save plot
# plt.savefig('energy_maxshear_intra_pga.png', bbox_inches='tight')
# plt.close()
plt.show()