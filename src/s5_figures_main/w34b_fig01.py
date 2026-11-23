# -*- coding: utf-8 -*-
"""W34b: fig01 redraw - lowercase panels, scale bar, Okabe palette."""
import os
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D

ROOT = r"D:\2026-SP"; INT = os.path.join(ROOT, "Outputs", "intermediate")
OUT = os.path.join(ROOT, "Outputs", "figures", "main")
plt.rcParams.update({"font.family": "sans-serif", "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
                     "font.size": 7.5, "axes.labelsize": 8, "axes.titlesize": 8.5,
                     "xtick.labelsize": 6.8, "ytick.labelsize": 6.8, "legend.fontsize": 6.6,
                     "axes.linewidth": 0.6, "axes.spines.top": False, "axes.spines.right": False,
                     "figure.dpi": 300, "savefig.dpi": 600, "pdf.fonttype": 42})
OK = {"blue": "#0072B2", "red": "#D55E00", "purple": "#CC79A7", "grey": "#999999"}
MM = 1/25.4

df = pd.read_csv(os.path.join(INT, "zenodo_yield_2021_grid.csv"))
mA = df["wheat_yield_tha"].notna().values
mD4 = (df["n_px"] >= 4).values

fig = plt.figure(figsize=(183*MM, 138*MM))
gs = fig.add_gridspec(2, 2, width_ratios=[1.3, 1], hspace=0.45, wspace=0.3,
                      left=0.08, right=0.96, top=0.94, bottom=0.09)

axA = fig.add_subplot(gs[:, 0])
sc = axA.scatter(df.lon, df.lat, c=df.elevation_m, cmap="viridis", s=30, edgecolors="none", zorder=2)
axA.scatter(df.lon[mA], df.lat[mA], s=95, facecolors="none", edgecolors=OK["red"], linewidths=1.3, zorder=3,
            label="Target A: process-model baseline (43)")
axA.scatter(df.lon[mD4], df.lat[mD4], marker="^", s=42, facecolors="white", edgecolors=OK["purple"],
            linewidths=1.1, zorder=4, label="Target D: satellite retrieval (22)")
cb = fig.colorbar(sc, ax=axA, pad=0.015, fraction=0.04); cb.set_label("Elevation (m)", fontsize=7)
# scale bar: 5 km in degrees at lat 40.1
km5_lon = 5 / (111.32 * np.cos(np.radians(40.1)))
x0, y0 = df.lon.min() + 0.02, df.lat.min() + 0.015
axA.plot([x0, x0 + km5_lon], [y0, y0], color="black", lw=1.6, solid_capstyle="butt")
axA.plot([x0, x0], [y0 - 0.004, y0 + 0.004], color="black", lw=1.2)
axA.plot([x0 + km5_lon, x0 + km5_lon], [y0 - 0.004, y0 + 0.004], color="black", lw=1.2)
axA.text(x0 + km5_lon/2, y0 + 0.006, "5 km", ha="center", fontsize=6.5)
axA.set_xlabel("Longitude (E)"); axA.set_ylabel("Latitude (N)")
axA.set_title("(a) 234-grid environmental matrix (0.0417 deg ~ 3.6 x 4.6 km)", loc="left", fontweight="bold")
handles, _ = axA.get_legend_handles_labels()
handles.append(Line2D([], [], marker="o", ls="none", color="#440154", markerfacecolor="#440154", ms=6,
                      label="grid colour = elevation (PC1 axis, r = -0.94)"))
axA.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=2, frameon=False)
axA.set_aspect(1/np.cos(np.radians(40.1)))

axB = fig.add_subplot(gs[0, 1])
data = [df.loc[mA, "wheat_yield_tha"], df.wheat_yield_pred_tha, df.yield_blended_tha,
        df.loc[mD4, "zenodo_yield_tha"]]
labels = ["A (43)", "B (234)", "C (234)", "D (22)"]
cols = [OK["red"], "#56B4E9", OK["blue"], OK["purple"]]
bp = axB.boxplot(data, tick_labels=labels, widths=0.55, patch_artist=True, showfliers=False,
                 medianprops=dict(color="black", lw=1.1))
for patch, c in zip(bp["boxes"], cols):
    patch.set_facecolor(c); patch.set_alpha(0.55); patch.set_edgecolor(c)
for i, v in enumerate(data, 1):
    axB.scatter(np.random.default_rng(7).normal(i, 0.045, len(v)), v, s=5, color=cols[i-1], alpha=0.6,
                edgecolors="none", zorder=3)
axB.axhline(5.241, color=OK["grey"], ls="--", lw=0.9)
axB.text(0.55, 5.30, "Beijing statistical mean 5.24 t/ha", fontsize=6.2, color=OK["grey"])
axB.set_ylabel("Yield (t/ha)")
axB.set_title("(b) Four model-derived yield targets", loc="left", fontweight="bold")

axC = fig.add_subplot(gs[1, 1])
axC.set_xlim(0, 12); axC.set_ylim(0, 10); axC.axis("off")
def box(x, y, w, h, text, fc, ec, fs=6.8):
    axC.add_patch(mpatches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.12",
                  facecolor=fc, edgecolor=ec, linewidth=1.0))
    axC.text(x + w/2, y + h/2, text, ha="center", va="center", fontsize=fs)
def arrow(x1, y1, x2, y2):
    axC.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle="->", color=OK["grey"], lw=1.1))
box(0.1, 7.3, 3.4, 2.2, "Xiao et al. 2024\n(Nat. Food) process\nmodel, baseline 1-km", "#fdf0ee", OK["red"])
box(4.3, 7.3, 2.4, 2.2, "A (43)\n7.21 +/- 0.23\nt/ha", "#fdf0ee", OK["red"])
box(8.0, 7.3, 3.9, 2.2, "D (22)\nChinaWheatYield30m\nSentinel retrieval", "#f7eef5", OK["purple"])
box(5.0, 4.2, 2.8, 2.2, "B (234)\nRidge interpolation\n(train fit R2 = 0.99)", "#eaf3fb", "#56B4E9")
box(5.0, 1.1, 2.8, 2.2, "C (234)\nBayesian blend\n+ district prior 6.0", "#e9f6f0", "#009E73")
arrow(3.55, 8.4, 4.25, 8.4); arrow(6.75, 8.4, 7.95, 8.4)
arrow(6.4, 7.25, 6.4, 6.5); arrow(6.4, 4.15, 6.4, 3.4)
axC.text(9.95, 6.8, "independent source", ha="center", fontsize=6.4, color=OK["grey"], style="italic")
axC.text(6.85, 3.75, "district prior 6.0 t/ha", fontsize=6.4, color=OK["grey"], ha="left")
axC.text(0.1, 2.1, "No field-measured target\navailable (grid scale)", fontsize=6.4, color=OK["red"],
         ha="left", va="center", style="italic")
axC.set_title("(c) Target provenance flow", loc="left", fontweight="bold")

fig.savefig(os.path.join(OUT, "fig01_study_area.png"))
fig.savefig(os.path.join(OUT, "fig01_study_area.tiff"), pil_kwargs={"compression": "tiff_lzw"})
plt.close(fig)
print("fig01 redrawn")
