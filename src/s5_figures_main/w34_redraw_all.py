# -*- coding: utf-8 -*-
"""W34: unified-style redraw of 11 flagged figures (audit-driven).
Style contract (fig style v2): Arial; Okabe-Ito palette; bold lowercase panel
letters (a)(b)(c); semantic colours stable across figures (XGB=blue,
LightGBM=orange, RF=green; targets A=red B=sky C=blue D=purple; E=blue M=red
EM=green); no Chinese; 600 dpi PNG + LZW TIFF per figure."""
import os, json, warnings
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = r"D:\2026-SP"
INT = os.path.join(ROOT, "Outputs", "intermediate")
OUT = os.path.join(ROOT, "Outputs", "figures", "main")
plt.rcParams.update({
    "font.family": "sans-serif", "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
    "font.size": 7.5, "axes.labelsize": 8, "axes.titlesize": 8.5,
    "xtick.labelsize": 6.8, "ytick.labelsize": 6.8, "legend.fontsize": 6.6,
    "axes.linewidth": 0.6, "xtick.major.width": 0.5, "ytick.major.width": 0.5,
    "axes.spines.top": False, "axes.spines.right": False,
    "figure.dpi": 300, "savefig.dpi": 600, "pdf.fonttype": 42,
})
OK = {"blue": "#0072B2", "orange": "#E69F00", "green": "#009E73", "red": "#D55E00",
      "purple": "#CC79A7", "sky": "#56B4E9", "yellow": "#F0E442", "grey": "#999999"}
MC = {"XGBoost": OK["blue"], "LightGBM": OK["orange"], "RF": OK["green"]}
TC = {"A": OK["red"], "B": OK["sky"], "C": OK["blue"], "D": OK["purple"]}
MM = 1/25.4

def panel(ax, letter, dx=-0.02):
    ax.set_title(f"({letter})", loc="left", fontweight="bold", fontsize=8.5, pad=4)

def save(fig, name):
    fig.savefig(os.path.join(OUT, name + ".png"))
    fig.savefig(os.path.join(OUT, name + ".tiff"), pil_kwargs={"compression": "tiff_lzw"})
    plt.close(fig)
    print("redrawn:", name)

# ============ fig02 feature audit (4 clean panels) ============
fig, axes = plt.subplots(2, 2, figsize=(183*MM, 130*MM))
vif = pd.read_csv(os.path.join(INT, "vif_results.csv")).sort_values("VIF", ascending=False).head(20).iloc[::-1]
ax = axes[0, 0]; panel(ax, "a")
ax.barh(vif.Variable, vif.VIF, color=OK["blue"], height=0.65)
ax.axvline(10, color=OK["red"], ls="--", lw=0.8)
ax.text(10.3, 0.2, "VIF=10", color=OK["red"], fontsize=6)
ax.set_xlabel("Variance inflation factor"); ax.set_title("(a)", loc="left", fontweight="bold", fontsize=8.5)
bor = pd.read_csv(os.path.join(INT, "boruta_results.csv"))
ax = axes[0, 1]; panel(ax, "b")
cnt = bor.Class.value_counts().reindex(["Confirmed", "Tentative", "Rejected"]).fillna(0)
ax.bar(cnt.index, cnt.values, color=[OK["green"], OK["yellow"], OK["grey"]], width=0.55)
for i, v in enumerate(cnt.values):
    ax.text(i, v + 0.3, str(int(v)), ha="center", fontsize=7)
ax.set_ylabel("Variables"); ax.set_title("(b)", loc="left", fontweight="bold", fontsize=8.5)
ax = axes[1, 0]; panel(ax, "c")
for cls, col in [("Confirmed", OK["green"]), ("Rejected", OK["grey"])]:
    s = bor[bor.Class == cls].Hit_Rate
    ax.hist(s, bins=12, alpha=0.65, color=col, label=cls)
ax.set_xlabel("Boruta hit rate (50 iterations)"); ax.set_ylabel("Variables"); ax.legend(frameon=False)
ax.set_title("(c)", loc="left", fontweight="bold", fontsize=8.5)
E = pd.read_csv(os.path.join(INT, "data_with_yield_ensemble_full.csv"))
drop = {"lon","lat","wheat_yield_tha","wheat_yield_pred_tha","yield_uncertainty_tha","yield_source","yield_blended_tha","yield_source_blend"}
fv = [c for c in E.columns if c not in drop and E[c].dtype in ("float64","int64")][:24]
corr = E[fv].corr(method="spearman").values
ax = axes[1, 1]; panel(ax, "d")
im = ax.imshow(corr, cmap="RdBu_r", vmin=-1, vmax=1)
ax.set_xticks(range(0, 24, 4)); ax.set_xticklabels([fv[i] for i in range(0, 24, 4)], rotation=45, ha="right")
ax.set_yticks(range(0, 24, 4)); ax.set_yticklabels([fv[i] for i in range(0, 24, 4)])
fig.colorbar(im, ax=ax, fraction=0.045, label="Spearman r")
ax.set_title("(d)", loc="left", fontweight="bold", fontsize=8.5)
fig.tight_layout()
save(fig, "fig02_feature_audit_dashboard")

# ============ fig04 CV scheme comparison (canonical v2) ============
d = pd.read_csv(os.path.join(INT, "review_response_diag_seeds_v2.csv"))
fig, axes = plt.subplots(1, 3, figsize=(183*MM, 62*MM))
schemes = ["random", "checker_2d", "lat_block"]; slab = ["Random", "Checkerboard", "Latitude blocks"]
for k, (ax, stat, title) in enumerate(zip(axes, ["pooled_mean", "fold_mean_mean"],
        ["(a) Pooled out-of-fold R2", "(b) Fold-mean R2"])):
    panel(ax, "ab"[k]); ax.set_title(f"({'ab'[k]}) {'Pooled out-of-fold' if k==0 else 'Fold-mean'} R2", loc="left", fontweight="bold")
    x = np.arange(len(schemes)); w = 0.36
    for i, m in enumerate(["XGBoost", "RF"]):
        sub = d[(d.Model == ("XGBoost" if m == "XGBoost" else "RF"))]
        vals = [float(sub[sub.Scheme == s][stat].iloc[0]) for s in schemes]
        errs = [float(sub[sub.Scheme == s][stat.replace("mean","std")].iloc[0]) if stat.replace("mean","std") in sub else 0 for s in schemes]
        ax.bar(x + (-w/2 if i == 0 else w/2), vals, w, yerr=errs, capsize=2,
               color=MC[m], label=m, error_kw=dict(lw=0.7))
    ax.axhline(0, color=OK["grey"], lw=0.6)
    ax.set_xticks(x); ax.set_xticklabels(slab); ax.set_ylabel("R2"); ax.legend(frameon=False)
gap = []
ax = axes[2]
panel(ax, "c"); ax.set_title("(c) Optimism gap (random - scheme)", loc="left", fontweight="bold")
for i, m in enumerate(["XGBoost", "RF"]):
    sub = d[d.Model == ("XGBoost" if m == "XGBoost" else "RF")]
    r = float(sub[sub.Scheme == "random"].pooled_mean.iloc[0])
    g = [r - float(sub[sub.Scheme == s].pooled_mean.iloc[0]) for s in schemes[1:]]
    ax.bar([0, 1], g, 0.5, color=MC[m], label=m)
ax.set_xticks([0, 1]); ax.set_xticklabels(slab[1:]); ax.set_ylabel("Delta R2"); ax.legend(frameon=False)
fig.tight_layout()
save(fig, "fig04_cv_scheme_comparison")

# ============ fig05 target-source sensitivity ============
ys = pd.read_csv(os.path.join(INT, "yield_source_sensitivity.csv"))
zen = pd.read_csv(os.path.join(INT, "zenodo_cv_results.csv"))
fig, axes = plt.subplots(1, 2, figsize=(183*MM, 66*MM), gridspec_kw={"width_ratios": [1.6, 1]})
ax = axes[0]; panel(ax, "a"); ax.set_title("(a) Same models, four targets (pooled R2)", loc="left", fontweight="bold")
rows = []
for _, r in ys.iterrows():
    t = r.Target.split("_")[0]
    rows.append((t, r.Model, r.R2))
dz = zen[zen.Scheme == "checker_4"]
for _, r in dz.iterrows():
    rows.append(("D", r.Model, r.R2_mean))
cats = ["A", "B", "C", "D"]; x = np.arange(4); w = 0.26
for i, m in enumerate(["XGBoost", "LightGBM", "RF"]):
    vals = [next((v for t, mm, v in rows if t == c and mm == m), np.nan) for c in cats]
    ax.bar(x + (i-1)*w, vals, w, color=MC[m], label=m)
ax.axhline(0, color=OK["grey"], lw=0.6)
ax.set_xticks(x); ax.set_xticklabels([f"Target {c}" for c in cats]); ax.set_ylabel("Pooled R2")
ax.legend(frameon=False, ncol=3, loc="upper left")
ax.annotate("circular\nvalidation", xy=(1.0, 0.97), xytext=(0.55, 0.85), fontsize=6.5, color=OK["red"],
            arrowprops=dict(arrowstyle="->", color=OK["red"], lw=0.7))
ax = axes[1]; panel(ax, "b"); ax.set_title("(b) The circular upper bound", loc="left", fontweight="bold")
bars = [("B: env. models\nCV R2", 0.98), ("B: LOO-IDW of\nits own sources", 0.27), ("B: LOO-IDW\nupper range", 0.20)]
ax.bar(range(3), [b[1] for b in bars], color=[OK["red"], OK["grey"], OK["grey"]], width=0.55)
ax.set_xticks(range(3)); ax.set_xticklabels([b[0] for b in bars], fontsize=6.2)
ax.set_ylabel("R2"); ax.set_ylim(0, 1.1)
for i, b in enumerate(bars):
    ax.text(i, b[1] + 0.02, f"{b[1]:.2f}", ha="center", fontsize=6.5)
fig.tight_layout()
save(fig, "fig05_source_sensitivity")

# ============ fig06 independent validation (D target) ============
fig, axes = plt.subplots(1, 2, figsize=(183*MM, 62*MM))
ax = axes[0]; panel(ax, "a"); ax.set_title("(a) Fold-mean R2 by scheme (n=22)", loc="left", fontweight="bold")
x = np.arange(3); w = 0.26
for i, m in enumerate(["XGBoost", "LightGBM", "RF"]):
    v = [float(zen[(zen.Scheme == s) & (zen.Model == m)].R2_mean.iloc[0]) for s in ["checker_4", "random"]]
    e = [float(zen[(zen.Scheme == s) & (zen.Model == m)].R2_std.iloc[0]) for s in ["checker_4", "random"]]
    ax.bar(x[:2] + (i-1)*w, v, w, yerr=e, capsize=2, color=MC[m], label=m, error_kw=dict(lw=0.7))
ax.axhline(0, color=OK["grey"], lw=0.6)
ax.set_xticks([0, 1]); ax.set_xticklabels(["Checkerboard", "Random"]); ax.set_ylabel("Fold-mean R2 (5-fold)")
ax.legend(frameon=False, ncol=3)
ax = axes[1]; panel(ax, "b"); ax.set_title("(b) Pooled R2: the small-sample trap", loc="left", fontweight="bold")
for i, m in enumerate(["XGBoost", "LightGBM", "RF"]):
    v = [float(zen[(zen.Scheme == s) & (zen.Model == m)].R2_pooled.iloc[0]) for s in ["checker_4", "random"]]
    ax.bar(x[:2] + (i-1)*w, v, w, color=MC[m])
ax.set_xticks([0, 1]); ax.set_xticklabels(["Checkerboard", "Random"]); ax.set_ylabel("Pooled R2")
ax.text(0.5, 0.05, "pooled ~0.99 under random CV is the cluster-\nstructure artefact (22 grids, 4-5 per fold)",
        transform=ax.transAxes, ha="center", fontsize=6, color=OK["grey"], style="italic")
fig.tight_layout()
save(fig, "fig06_independent_validation")

# ============ fig07 QRF uncertainty ============
q = pd.read_csv(os.path.join(INT, "qrf_uncertainty.csv")).sort_values("y_true_blend").reset_index(drop=True)
fig, axes = plt.subplots(1, 3, figsize=(183*MM, 60*MM))
ax = axes[0]; panel(ax, "a"); ax.set_title("(a) Prediction intervals vs observation", loc="left", fontweight="bold")
xs = np.arange(len(q))
ax.fill_between(xs, q.q10, q.q90, color=OK["blue"], alpha=0.28, label="90% interval")
ax.plot(xs, q.q50, color=OK["blue"], lw=0.8, label="Q50")
ax.plot(xs, q.y_true_blend, ".", color=OK["red"], ms=2.2, label="observed", rasterized=True)
ax.set_xlabel("Grids sorted by observed yield"); ax.set_ylabel("Yield (t/ha)"); ax.legend(frameon=False, ncol=3)
ax = axes[1]; panel(ax, "b"); ax.set_title("(b) Calibration", loc="left", fontweight="bold")
ax.scatter(q.y_true_blend, q.q50, s=5, color=OK["blue"], alpha=0.6, edgecolors="none")
lims = [q.y_true_blend.min(), max(q.y_true_blend.max(), q.q50.max())]
ax.plot(lims, lims, "--", color=OK["grey"], lw=0.8)
ax.set_xlabel("Observed yield (t/ha)"); ax.set_ylabel("Q50 prediction (t/ha)")
conf = pd.read_csv(os.path.join(INT, "review_response_conformal.csv"))
ax.text(0.05, 0.92, "\n".join(f"raw: PICP {conf[conf.variant=='raw'].PICP_90.iloc[0]:.3f}" for _ in [1]) +
        f"\nconformal: PICP {conf[conf.variant=='conformal'].PICP_90.iloc[0]:.3f}",
        transform=ax.transAxes, va="top", fontsize=6.2)
ax = axes[2]; panel(ax, "c"); ax.set_title("(c) Interval width distribution", loc="left", fontweight="bold")
ax.hist(q.width_90, bins=18, color=OK["blue"], alpha=0.8)
ax.axvline(q.y_true_blend.std(), color=OK["red"], ls="--", lw=0.9)
ax.text(q.y_true_blend.std()+0.02, ax.get_ylim()[1]*0.9, "target SD", color=OK["red"], fontsize=6.2)
ax.set_xlabel("Q90-Q10 width (t/ha)"); ax.set_ylabel("Grids")
fig.tight_layout()
save(fig, "fig07_qrf_uncertainty")

# ============ fig08 variogram + spectrum + dose (both domains, EN) ============
vari = json.load(open(os.path.join(INT, "review_response_variogram.json")))
spec = pd.read_csv(os.path.join(INT, "w14_q2_spectrum.csv"))
dose_p = pd.read_csv(os.path.join(INT, "w14_dose_response.csv"))
dose_n = pd.read_csv(os.path.join(INT, "w22_r6_national_dose.csv"))
fig, axes = plt.subplots(1, 3, figsize=(183*MM, 58*MM))
ax = axes[0]; panel(ax, "a"); ax.set_title("(a) Empirical variograms", loc="left", fontweight="bold")
yv = pd.DataFrame(vari["yield_variogram"]); rv = pd.DataFrame(vari["resid_variogram"])
ax.plot(yv.lag_km, yv.gamma, "o-", ms=2.6, lw=0.9, color=OK["blue"], label="yield")
ax.plot(rv.lag_km, rv.gamma, "s-", ms=2.6, lw=0.9, color=OK["orange"], label="CV residuals")
ax.axvline(4.62, color=OK["red"], ls="--", lw=0.9)
ax.text(4.9, ax.get_ylim()[1]*0.85, "range\n4.62 km", color=OK["red"], fontsize=6.2)
ax.set_xlabel("Lag h (km)"); ax.set_ylabel("Semi-variance (normalised)"); ax.legend(frameon=False)
ax = axes[1]; panel(ax, "b"); ax.set_title("(b) Five-scheme spectrum (XGB)", loc="left", fontweight="bold")
lab = {"random": "Random", "checker_1x": "Checker", "lat4": "Lat blocks", "lobo8": "LOBO", "env_kmeans4": "Env-space"}
ax.bar(range(len(spec)), spec.pooled_mean, color=[OK["blue"], OK["sky"], OK["orange"], OK["purple"], OK["red"]], width=0.6)
ax.axhline(0, color=OK["grey"], lw=0.6)
ax.set_xticks(range(len(spec))); ax.set_xticklabels([lab[s] for s in spec.scheme], rotation=20, ha="right")
ax.set_ylabel("Pooled R2 (target C)")
ax = axes[2]; panel(ax, "c"); ax.set_title("(c) Dose-response, two domains", loc="left", fontweight="bold")
p = dose_p[dose_p.model == "XGB"]; n = dose_n[dose_n.scheme != "random"]
ax.plot([0]+list(p.block_ratio_x_range), [0.4002]+list(p.pooled_mean), "o-", ms=3.2, lw=1.0, color=OK["blue"], label="Pinggu (5.6 ranges wide)")
nvals = [float(dose_n[dose_n.scheme=="random"].pooled_mean.iloc[0])] + [float(v) for v in n.pooled_mean]
ax.plot([0]+list(n.ratio_x_range), nvals, "s-", ms=3.2, lw=1.0, color=OK["red"], label="NCP (~2 own ranges)")
ax.axhline(0, color=OK["grey"], lw=0.6)
ax.set_xlabel("Checkerboard block size / variogram range"); ax.set_ylabel("Pooled R2")
ax.legend(frameon=False, fontsize=6.2)
fig.tight_layout()
save(fig, "fig08_variogram_block_defense")

# ============ fig09 learning curve (recomputed, EN) ============
F = pd.read_csv(os.path.join(INT, "fine250_v5_features.csv"))
ycol = "yield_2021_tha"
idc = ["cell_r", "cell_c", "lon", "lat", ycol, "n_px"]
Xf = F[[c for c in F.columns if c not in idc and F[c].dtype in ("float64", "int64")]].fillna(0)
yv = F[ycol].values
from sklearn.model_selection import KFold
from sklearn.metrics import r2_score
from xgboost import XGBRegressor
NEW = dict(n_estimators=428, max_depth=5, learning_rate=0.168, subsample=0.594,
           colsample_bytree=0.821, min_child_weight=6, reg_alpha=3.57, reg_lambda=2.69,
           random_state=42, n_jobs=4, verbosity=0)
sizes = [60, 100, 140, 180, 220, 260, 300]
tr_s, te_s = [], []
rng = np.random.default_rng(7)
for s in sizes:
    tr_r, te_r = [], []
    for rep in range(3):
        idx = rng.choice(len(yv), s, replace=False)
        Xs, ys = Xf.values[idx], yv[idx]
        for tr, te in KFold(5, shuffle=True, random_state=rep).split(Xs):
            m = XGBRegressor(**NEW).fit(Xs[tr], ys[tr])
            tr_r.append(r2_score(ys[tr], m.predict(Xs[tr])))
            te_r.append(r2_score(ys[te], m.predict(Xs[te])))
    tr_s.append(np.mean(tr_r)); te_s.append(np.mean(te_r))
pd.DataFrame({"train_size": sizes, "train_r2": tr_s, "val_r2": te_s}).to_csv(
    os.path.join(INT, "w34_fig09_learning_curve.csv"), index=False, encoding="utf-8-sig")
fig, ax = plt.subplots(figsize=(89*MM, 62*MM))
ax.plot(sizes, tr_s, "o-", ms=3.4, lw=1.1, color=OK["orange"], label="Training R2")
ax.plot(sizes, te_s, "s-", ms=3.4, lw=1.1, color=OK["blue"], label="Validation R2 (5-fold)")
ax.axhline(0.769, color=OK["green"], ls="--", lw=0.9)
ax.text(62, 0.78, "hybrid E8 pooled R2 (0.769)", color=OK["green"], fontsize=6.2)
ax.set_xlabel("Training-set size (grids)"); ax.set_ylabel("R2"); ax.legend(frameon=False, loc="center right")
fig.tight_layout()
save(fig, "fig09_learning_curve")

print("W34 batch1 complete")
