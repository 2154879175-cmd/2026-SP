# -*- coding: utf-8 -*-
"""Verify the Figshare v4 China files against the publisher manifest and inventory CMA."""
import argparse
import csv
import hashlib
import json
import shutil
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[2]
FIGSHARE = ROOT / "Data" / "CropArea_figshare"
FIG_DL = FIGSHARE / "download"
CMA_DL = ROOT / "Data" / "CMA_agromet" / "download"
MIN_YEARS = range(2016, 2023)


def matches(path, entry):
    if not path.is_file() or path.stat().st_size != int(entry["size"]):
        return False
    with path.open("rb") as source:
        return hashlib.file_digest(source, "md5").hexdigest() == entry["computed_md5"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--download", action="store_true", help="Fetch missing or invalid Figshare files")
    args = parser.parse_args()

    with (FIGSHARE / "figshare_v4_manifest.csv").open(encoding="utf-8-sig", newline="") as source:
        entries = list(csv.DictReader(source))
    found, invalid, missing = [], [], []
    for entry in entries:
        name = entry["name"]
        path = FIG_DL / name
        if args.download and not matches(path, entry):
            FIG_DL.mkdir(parents=True, exist_ok=True)
            part = path.with_suffix(path.suffix + ".part")
            with urlopen(entry["download_url"], timeout=60) as source, part.open("wb") as dest:
                shutil.copyfileobj(source, dest)
            if matches(part, entry):
                part.replace(path)
            else:
                raise ValueError(f"Figshare size or MD5 mismatch: {name}")
        if matches(path, entry):
            found.append(name)
        elif path.exists():
            invalid.append(name)
        else:
            missing.append(name)

    missing_min_years = [year for year in MIN_YEARS if f"CHN_{year}.tif" not in found]
    cma_files = sorted(str(path.relative_to(CMA_DL)) for path in CMA_DL.rglob("*") if path.is_file())
    report = {
        "figshare": {
            "version": 4, "found": found, "invalid": invalid, "missing": missing,
            "missing_2016_2022": missing_min_years,
        },
        "cma": {
            "found": cma_files,
            "note": "Inspect the yield files with w36_cma_ingest.py" if cma_files
            else "No local station yield files found",
        },
    }
    out = ROOT / "Outputs" / "intermediate" / "w36d_download_status.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"[figshare] {len(found)}/{len(entries)} verified; {len(invalid)} invalid; {len(missing)} missing")
    print(f"[figshare] missing 2016–2022: {missing_min_years}")
    print(f"[CMA] {len(cma_files)} local files")
    print(f"status -> {out}")
    return bool(invalid or missing)


if __name__ == "__main__":
    raise SystemExit(main())
