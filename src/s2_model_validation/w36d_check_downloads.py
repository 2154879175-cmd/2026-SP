# -*- coding: utf-8 -*-
"""W36d: validator for user-downloaded datasets (figshare China crop-area TIFs +
CMA yield tables). Runs anytime; reports what arrived and what's still needed."""
import os, glob, json, warnings
import numpy as np
warnings.filterwarnings("ignore")

ROOT = r"D:\2026-SP"
FIG_DL = os.path.join(ROOT, "Data", "CropArea_figshare", "download")
CMA_DL = os.path.join(ROOT, "Data", "CMA_agromet", "download")
report = {"figshare": {"found": [], "missing": []}, "cma": {"found": [], "note": ""}}

# ---- figshare: China_[year].tif files ----
WANT_YEARS = list(range(2016, 2023))          # panel/RS overlap years (minimum)
OPT_YEARS = [y for y in range(1980, 2023) if y not in WANT_YEARS]
tif_all = sorted(glob.glob(os.path.join(FIG_DL, "**", "*.tif"), recursive=True) +
                 glob.glob(os.path.join(FIG_DL, "**", "*.tif.gz"), recursive=True))
print(f"[figshare] TIF files found: {len(tif_all)}")
for fp in tif_all:
    base = os.path.basename(fp)
    report["figshare"]["found"].append(base)
try:
    import rasterio
    have_years = []
    for fp in tif_all:
        base = os.path.basename(fp)
        yr = "".join(ch for ch in base if ch.isdigit())[:4]
        have_years.append(yr)
        with rasterio.open(fp) as s:
            bands = s.count
            desc = s.descriptions
            print(f"  {base}: {s.width}x{s.height}, {bands} bands, epsg={s.crs}, "
                  f"band names={list(desc)[:16]}")
        if s.width > 4000 or s.height > 2000:
            print("    [warn] unexpected global raster size")
    missing = [y for y in WANT_YEARS if str(y) not in have_years]
    print("  coverage vs needed years 2016-2022:", "OK" if not missing else f"missing {missing}")
    report["figshare"]["missing"] = missing
except ImportError:
    print("  (rasterio check skipped)")
except Exception as e:
    print("  [warn] tif inspection:", type(e).__name__)

for y in WANT_YEARS:
    if not any(str(y) in f for f in tif_all):
        report["figshare"]["missing"].append(y)

# ---- CMA: scan download dir ----
cma_files = sorted(glob.glob(os.path.join(CMA_DL, "**", "*.*"), recursive=True))
print(f"[CMA] files found: {len(cma_files)}")
if cma_files:
    print("  run: python src/s2_model_validation/w36_cma_ingest.py  (station discovery)")
    for f in cma_files[:20]:
        report["cma"]["found"].append(os.path.basename(f))
else:
    print("  empty - download from data.cma.cn (search 农业气象观测年报 / 作物产量)")

out = os.path.join(ROOT, "Outputs", "intermediate", "w36d_download_status.json")
json.dump(report, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("status ->", out)
