# -*- coding: utf-8 -*-
"""W34c: fig10-13 redraw patch (ledger-faithful)."""
import os, json, warnings
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = r"D:\2026-SP"; INT = os.path.join(ROOT, "Outputs", "intermediate")
OUT = os.path.join(ROOT, "Outputs", "figures", "main")
plt.rcParams.update({
    "font.family": "sans-serif", "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
    "font.size": 7.5, "axes.labelsize": 8, "axes.titlesize": 8.5,
    "xtick.labelsize": 6.8, "ytick.labelsize": 6.8, "legend.fontsize": 6.6,
    "axes.linewidth": 0.6, "axes.spines.top": False, "axes.spines.right": False,
    "figure.dpi": 300, "savefig.dpi": 600, "pdf.fonttype": 42})
OK = {"blue": "#0072B2", "orange": "#E69F00", "green": "#009E73", "red": "#D55E00", "grey": "#999999"}
MM = 1/25.4

led = pd.read_csv(os.path.join(INT, "experiments_ledger_v3.csv"))
sp = pd.read_csv(os.path.join(INT, "spatial_cv_ledger.csv"))
ex = pd.read_csv(os.path.join(INT, "extrapolation_ledger.csv"))
F = pd.read_csv(os.path.join(INT, "fine250_v5_features.csv"))
pr = pd.read_csv(os.path.join(INT, "all_predictions_v3.csv"))

def save(fig, name):
    fig.savefig(os.path.join(OUT, name + ".png"))
    fig.savefig(os.path.join(OUT, name + ".tiff"), pil_kwargs={"compression": "tiff_lzw"})
    plt.close(fig); print("redrawn:", name)

# sanity: prediction row order matches feature table
assert len(pr) == len(F), "row mismatch"
c = np.corrcoef(pr.E0.values, F.yield_2021_tha.values)[0, 1]
print("order-check corr(E0_pred, yield):", round(c, 3))

# ---- fig10: random vs latitude blocks (ledger-faithful) ----
fig, ax = plt.subplots(figsize=(120*MM, 66*MM))
pairs = [("E0", "E0_base58", "S0_base58", "E0 baseline\n(58 vars)"),
         ("E5", "E5_topk25", "S5_topk25", "E5 top-25\n(18 effective)"),
         ("E7", "E7_topk25_ridge", None, "E7 +Ridge mix\n(no block run)"),
         ("E8", "E8_resid_idw", "S8_resid_idw", "E8 hybrid\n(residual IDW)")]
rand = [float(led[led.exp == le].r2_pooled.iloc[0]) for _, le, _, _ in pairs]
latv = [float(sp[sp.exp == se].r2_pooled.iloc[0]) if se else np.nan for _, _, se, _ in pairs]
x = np.arange(4); w = 0.38
ax.bar(x - w/2, rand, w, color=OK["blue"], label="Random 5-fold")
ax.bar(x + w/2, [0 if np.isnan(v) else v for v in latv], w, color=OK["orange"], label="Latitude blocks (4)")
for i, v in enumerate(latv):
    if np.isnan(v):
        ax.text(x[i] + w/2, 0.02, "not\nrun", ha="center", fontsize=6, color=OK["grey"], rotation=90)
ax.axhline(0, color=OK["grey"], lw=0.6)
ax.set_xticks(x); ax.set_xticklabels([p[3] for p in pairs], fontsize=6.4)
ax.set_ylabel("Pooled R2"); ax.legend(frameon=False)
fig.tight_layout(); save(fig, "fig10_experiment_comparison")

# ---- fig11: E0 vs E8 under three blocking designs ----
fig, ax = plt.subplots(figsize=(89*MM, 62*MM))
blocks = ["Latitude 4", "LOBO 8", "Env-space"]
e0v = [float(sp[sp.exp == "S0_base58"].r2_pooled.iloc[0]),
       float(ex[(ex.scheme == "LOBO_kmeans8_geo") & (ex.exp == "E0")].r2_pooled.iloc[0]),
       float(ex[(ex.scheme == "envspace_featk4") & (ex.exp == "E0")].r2_pooled.iloc[0])]
e8v = [float(sp[sp.exp == "S8_resid_idw"].r2_pooled.iloc[0]),
       float(ex[(ex.scheme == "LOBO_kmeans8_geo") & (ex.exp == "E8")].r2_pooled.iloc[0]),
       float(ex[(ex.scheme == "envspace_featk4") & (ex.exp == "E8")].r2_pooled.iloc[0])]
x = np.arange(3)
ax.bar(x - 0.19, e0v, 0.38, color=OK["blue"], label="E0 environmental")
ax.bar(x + 0.19, e8v, 0.38, color=OK["red"], label="E8 hybrid")
ax.axhline(0, color=OK["grey"], lw=0.6)
ax.set_xticks(x); ax.set_xticklabels(blocks)
ax.set_ylabel("Pooled R2 under blocking"); ax.legend(frameon=False)
fig.tight_layout(); save(fig, "fig11_block_sensitivity")

# ---- fig12: obs-pred scatter ----
obs = pr["E0"].values
fig, axes = plt.subplots(1, 2, figsize=(120*MM, 62*MM))
for ax, e, le, ttl in zip(axes, ["E0", "E8"], ["E0_base58", "E8_resid_idw"],
                          ["(a) E0 environmental baseline", "(b) E8 hybrid (residual IDW)"]):
    p = pr[e + "_p"].values
    ax.set_title(ttl, loc="left", fontweight="bold", fontsize=8)
    ax.scatter(obs, p, s=7, alpha=0.5, color=OK["blue"] if e == "E0" else OK["red"], edgecolors="none")
    lims = [min(obs.min(), p.min()), max(obs.max(), p.max())]
    ax.plot(lims, lims, "--", color=OK["grey"], lw=0.9)
    r2 = float(led[led.exp == le].r2_pooled.iloc[0]); rm = float(led[led.exp == le].rmse.iloc[0])
    ax.text(0.05, 0.92, f"R2 = {r2:.3f}\nRMSE = {rm:.3f} t/ha\nn = {len(obs)}",
            transform=ax.transAxes, va="top", fontsize=6.5)
    ax.set_xlabel("Observed yield (t/ha)"); ax.set_ylabel("Predicted yield (t/ha)")
fig.tight_layout(); save(fig, "fig12_obs_pred_scatter")

# ---- fig13: extrapolation spectrum (four ledger points) ----
fig, ax = plt.subplots(figsize=(120*MM, 62*MM))
stages = ["Random\n5-fold", "Latitude\nblocks", "LOBO\n8 blocks", "Env-space\nK-means 4"]
e0 = [float(led[led.exp == "E0_base58"].r2_pooled.iloc[0]), e0v[0], e0v[1], e0v[2]]
e8 = [float(led[led.exp == "E8_resid_idw"].r2_pooled.iloc[0]), e8v[0], e8v[1], e8v[2]]
ax.plot(range(4), e0, "o-", ms=4, lw=1.1, color=OK["blue"], label="E0 environmental")
ax.plot(range(4), e8, "s-", ms=4, lw=1.1, color=OK["red"], label="E8 hybrid")
for i, (a, b) in enumerate(zip(e0, e8)):
    ax.text(i, a + 0.05, f"{a:.2f}", ha="center", fontsize=6, color=OK["blue"])
    ax.text(i, b + 0.05, f"{b:.2f}", ha="center", fontsize=6, color=OK["red"])
ax.axhline(0, color=OK["grey"], lw=0.6)
ax.set_xticks(range(4)); ax.set_xticklabels(stages, fontsize=6.6)
ax.set_ylabel("Pooled R2"); ax.set_xlabel("Validation scheme (decreasing spatial connectivity)")
ax.legend(frameon=False)
fig.tight_layout(); save(fig, "fig13_extrapolation_spectrum")
print("W34c done")
