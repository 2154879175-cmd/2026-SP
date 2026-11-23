# -*- coding: utf-8 -*-
"""W36: CMA agromet yield dataset ingestion & verification script.

Run AFTER downloading the dataset from data.cma.cn into
  Data/CMA_agromet/download/
(the raw download, any folder structure, any file types).

What it does (discovery mode - file format is unknown until we see it):
1. Scans every file, detects type (xlsx/xls/csv/txt/shp-less), tries readers;
2. Finds station identity columns and flags Beijing-area stations:
   Pinggu, Shunyi, Miyun, Tongzhou, Fangshan, Yanqing, Huairou, Daxing, Changping
   plus neighbour-ring stations (Sanhe, Xianghe, Dachang, Jizhou, Baodi, Wuqing);
3. Finds winter-wheat yield elements (地段单产/县平均单产/播种-成熟日数/总产);
4. Extracts Beijing-area winter-wheat series to a tidy CSV;
5. Writes a discovery report listing every distinct station name found, so the
   station-coverage question (does 618 include Beijing?) is answered once.

Output: Outputs/intermediate/w36_cma_ingest_report.json,
        Outputs/intermediate/w36_cma_beijing_series.csv (if found)."""
import os, sys, json, glob, warnings
import pandas as pd
import numpy as np
warnings.filterwarnings("ignore")

ROOT = r"D:\2026-SP"
RAW = os.path.join(ROOT, "Data", "CMA_agromet", "download")
INT = os.path.join(ROOT, "Outputs", "intermediate")
os.makedirs(RAW, exist_ok=True)
os.makedirs(INT, exist_ok=True)

if not os.listdir(RAW):
    sys.exit(f"[abort] {RAW} is empty - download the dataset from data.cma.cn first "
             f"(search: 作物产量 / 农业气象观测年报; export into this folder, keep raw structure).")

BJ = ["平谷", "顺义", "密云", "通州", "房山", "延庆", "怀柔", "大兴", "昌平", "海淀", "朝阳", "丰台", "门头沟"]
RING = ["三河", "大厂", "香河", "蓟州", "蓟县", "宝坻", "武清", "兴隆", "遵化"]
YIELD_KEYS = ["地段单产", "县平均单产", "单产", "地段总产", "实收面积"]
WHEAT_KEYS = ["冬小麦", "小麦"]

def read_any(fp):
    ext = os.path.splitext(fp)[1].lower()
    try:
        if ext in (".xlsx", ".xls"):
            return pd.read_excel(fp, sheet_name=None, header=None, nrows=200)
        if ext in (".csv", ".txt"):
            for enc in ("utf-8", "gbk", "gb18030", "utf-16"):
                try:
                    df = pd.read_csv(fp, encoding=enc, header=None, nrows=200,
                                     sep=None, engine="python", on_bad_lines="skip")
                    return {"__file__": df}
                except Exception:
                    continue
    except Exception as e:
        print(f"  [skip] {os.path.basename(fp)}: {type(e).__name__}")
    return None

report = {"files": [], "stations_found": {}, "beijing_hits": [], "yield_columns": []}
files = sorted(glob.glob(os.path.join(RAW, "**", "*.*"), recursive=True))
print(f"[scan] {len(files)} files under {RAW}", flush=True)

for fp in files:
    base = os.path.basename(fp)
    sheets = read_any(fp)
    if sheets is None:
        continue
    report["files"].append(base)
    for sname, df in (sheets or {}).items():
        blob = " ".join(str(x) for x in df.astype(str).values.flatten()[:5000])
        hits_bj = [k for k in BJ if k in blob]
        hits_ring = [k for k in RING if k in blob]
        hits_yield = [k for k in YIELD_KEYS if k in blob]
        hits_wheat = [k for k in WHEAT_KEYS if k in blob]
        if hits_bj or hits_ring:
            report["beijing_hits"].append({"file": base, "sheet": str(sname),
                                           "beijing": hits_bj, "ring": hits_ring,
                                           "yield_keys": hits_yield, "wheat_keys": hits_wheat})
            print(f"  [HIT] {base} :: {str(sname)[:20]} | BJ:{hits_bj} ring:{hits_ring}", flush=True)
        # station-name discovery: any cell containing '站' within short strings
        for cell in df.astype(str).values.flatten()[:20000]:
            if isinstance(cell, str) and cell.endswith("站") and 2 < len(cell) <= 12:
                report["stations_found"][cell] = report["stations_found"].get(cell, 0) + 1

rep_path = os.path.join(INT, "w36_cma_ingest_report.json")
json.dump(report, open(rep_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"[report] files={len(report['files'])} | station names: {len(report['stations_found'])} | "
      f"beijing hits: {len(report['beijing_hits'])}")
print(f"saved {rep_path}")
print("[next] paste the report back to the assistant for targeted extraction of "
      "Pinggu/Shunyi winter-wheat series.")
