import pandas as pd, numpy as np, matplotlib.pyplot as plt

plt.rcParams.update({
    "font.size": 16,        # Øk font-størrelse på aksetitler, ticks osv.
    "axes.titlesize": 18,   # Tittel-størrelse
    "axes.labelsize": 16,   # Aksenes label-størrelse
    "legend.fontsize": 14,  # Legende-størrelse
    "xtick.labelsize": 16,  # X-ticks størrelse
    "ytick.labelsize": 16   # Y-ticks størrelse
})


# Recreate data
data = [
 (1,0.04,"Test02",0.4,0,3.02,0.252429641,0.18354932),
 (1,0.09,"Test03",0.8,0,2.89,0.344778922,0.230903188),
 (1,0.09,"Test04",1.4,0,2.92,0.485684447,0.32992916),
 (1,0.09,"Test05",1.7,0,2.90,0.501650577,0.328967544),
 (2,0.09,"Test14",2.9,0.6,2.52,0.705614094,0.376661798),
 (1,0.18,"Test06",3.0,0.5,2.89,0.693240788,0.485677046),
 (1,0.18,"Test07",5.1,1.4,2.87,0.815787188,0.52576787),
 (1,0.18,"Test08",6.0,2.0,2.84,0.952406917,0.617766464),
 (2,0.18,"Test15",8.7,3.6,2.45,1.412046932,0.637872809),
 (2,0.18,"Test16",10.3,4.4,2.39,1.542708015,0.634039424),
 (2,0.18,"Test17",11.4,5.0,2.34,1.563631874,0.604437673),
 (3,0.18,"Test23",9.7,4.2,2.05,1.870069295,0.573182555),
 (1,0.27,"Test09",11.3,6.1,2.82,1.217636606,0.708955886),
 (1,0.27,"Test10",15.7,11.5,2.69,1.551747265,0.773938546),
 (2,0.27,"Test18",18.5,8.7,2.28,2.234710206,0.810855938),
 (2,0.27,"Test19",22.2,10.6,2.28,2.362225824,0.814614835),
 (2,0.27,"Test20",24.5,11.6,2.28,2.583528175,0.853381109),
 (3,0.27,"Test24",21.3,9.9,2.05,2.771883566,0.831390851),
 (1,0.36,"Test11",27.1,22.1,2.56,2.414591085,1.066265856),
 (1,0.36,"Test12",31.7,27.2,2.48,2.789953906,1.072756379),
 (1,0.36,"Test13",36.7,32.8,2.39,3.291774267,1.124017312),
 (2,0.36,"Test21",42.0,20.2,2.28,3.215229147,1.076677738),
 (3,0.36,"Test25",44.6,16.3,2.02,3.58910893,1.037698393),
 (2,0.45,"Test22",51.1,24.2,2.15,4.117414328,1.244380888),
 (3,0.45,"Test26",64.8,22.7,1.98,4.381482398,1.21513786)
]
df = pd.DataFrame(data, columns=["Config","PGA","Test","Base_kJ","AFC_kJ","Freq","Drift1","Drift2"])

# Compute percentage
df["AFC_percent"] = df["AFC_kJ"] / (df["Base_kJ"]) * 100

# Plot
fig, ax = plt.subplots(figsize=(8,5))
markers = {1:'o', 2:'s', 3:'^'}
colors = {1:'#E15759', 2:'#4E79A7', 3:'#59A14F'}

for cfg in sorted(df["Config"].unique()):
    sub = df[df["Config"]==cfg].sort_values(by="Test")
    ax.plot(sub["Base_kJ"], sub["AFC_kJ"], marker=markers[cfg], color=colors[cfg], linewidth=2, label=f"Config {cfg}")

ax.set_xlabel("Total energy dissipated")
ax.set_ylabel("AFC energy dissipation")
ax.set_title("AFC energy dissipation vs. total energy dissipated")
ax.grid(True, alpha=0.3, linestyle='--')
ax.legend(title="Configurations")
plt.tight_layout()
plt.show()
