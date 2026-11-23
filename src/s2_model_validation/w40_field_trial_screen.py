# -*- coding: utf-8 -*-
"""Inventory the public field-trial records that may overlap the regional yield product."""
import csv
import hashlib
import math
from collections import defaultdict
from pathlib import Path

from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parents[2]
WORKBOOK = ROOT / "Data" / "external" / "china_yield_centurial" / "download" / "China_yield_centurial_v1.xlsx"
OUTPUT = ROOT / "Outputs" / "reports" / "w40_field_trial_screen.csv"
MD5 = "f709ad47259dec09e1a0ebdca41cec46"
# Published WheatMapNCP bounding box, used only for initial data discovery.
BOUNDS = (105, 29, 123, 42)


def main():
    with WORKBOOK.open("rb") as source:
        if hashlib.file_digest(source, "md5").hexdigest() != MD5:
            raise ValueError("The workbook differs from the verified Figshare v1 file")
    workbook = load_workbook(WORKBOOK, read_only=True, data_only=True)
    counters = defaultdict(list)
    try:
        rows = workbook["Data"].values
        headers = [value.strip() for value in next(rows)]
        for values in rows:
            row = dict(zip(headers, values))
            crop, year = row["Crop_type"], row["Year_sampling"]
            if crop not in ("Wheat", "Maize") or not isinstance(year, int) or not 2016 <= year <= 2021:
                continue
            lon, lat, grain = (row[name] for name in ("Longitude", "Latitude", "GrainYield_mean"))
            if not all(isinstance(v, (int, float)) and math.isfinite(v) for v in (lon, lat, grain)):
                continue
            west, south, east, north = BOUNDS
            if west <= lon <= east and south <= lat <= north and grain > 0:
                counters[crop].append(row)
    finally:
        workbook.close()

    with OUTPUT.open("w", newline="", encoding="utf-8") as dest:
        writer = csv.writer(dest, lineterminator="\n")
        writer.writerow(["crop_label", "year_sampling", "treatment_rows", "studies", "sites",
                         "rows_with_sowing", "rows_with_maturity", "rows_with_n_rate"])
        for crop, rows in sorted(counters.items()):
            groups = [("2016-2021", rows)]
            groups += [(year, [row for row in rows if row["Year_sampling"] == year])
                       for year in range(2016, 2022)]
            for year, group in groups:
                ids = [len({row[column] for row in group if row[column] is not None})
                       for column in ("Study_ID", "Site_ID")]
                observed = [sum(row[column] not in (None, "") for row in group)
                            for column in ("Sowing", "Maturity", "N_rate")]
                writer.writerow([crop, year, len(group), *ids, *observed])
    print(f"Wrote field-trial coverage to {OUTPUT.name}")


if __name__ == "__main__":
    main()
