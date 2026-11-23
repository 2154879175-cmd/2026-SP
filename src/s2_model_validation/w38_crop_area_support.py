# -*- coding: utf-8 -*-
"""Audit the spatial support of Figshare crop areas on the existing Pinggu lattice."""
import csv
from pathlib import Path

import numpy as np
import pandas as pd
import rasterio

ROOT = Path(__file__).resolve().parents[2]
RASTERS = ROOT / "Data" / "CropArea_figshare" / "download"
INTERMEDIATE = ROOT / "Outputs" / "intermediate"
OUTPUT = ROOT / "Outputs" / "reports" / "w38_crop_area_support.csv"
# Figshare v4 Band_Name.docx, Table 1 (China), bands are 1-based.
CROPS = {"wheat": (12, "whea"), "maize": (14, "maiz")}


def main():
    grid = pd.read_csv(INTERMEDIATE / "zenodo_yield_2021_grid.csv")
    coords = grid[["lon", "lat"]]
    if not np.isfinite(coords.to_numpy()).all() or coords.duplicated().any():
        raise ValueError("Pinggu grid requires finite, unique centre coordinates")
    rs_subset = grid["zenodo_yield_tha"].notna().to_numpy()
    records = []
    for year in range(2016, 2023):
        with rasterio.open(RASTERS / f"CHN_{year}.tif") as src:
            if src.crs is None or src.crs.to_epsg() != 4326 or src.count != 14:
                raise ValueError(f"Unexpected CRS or China band count in {year}")
            rows, cols = rasterio.transform.rowcol(src.transform, coords.lon, coords.lat)
            rows, cols = np.asarray(rows), np.asarray(cols)
            inside = (rows >= 0) & (rows < src.height) & (cols >= 0) & (cols < src.width)
            if not inside.all():
                raise ValueError(f"Pinggu grid centres outside the raster in {year}")
            cell_ids = rows * src.width + cols
            for crop, (band, code) in CROPS.items():
                if src.descriptions[band - 1] not in (None, "", code):
                    raise ValueError(f"Unexpected {crop} band description in {year}: {src.descriptions[band - 1]}")
                area = src.read(band, masked=True)[rows, cols].astype(float).filled(np.nan)
                valid = np.isfinite(area)
                if np.any(area[valid] < 0):
                    raise ValueError(f"Unmasked negative {crop} area in {year}")
                subsets = {"pinggu_all": np.ones(len(grid), dtype=bool)}
                if year == 2021:
                    subsets["pinggu_rs_yield_2021"] = rs_subset
                for subset, eligible in subsets.items():
                    present = eligible & valid & (area > 0)
                    records.append({
                        "year": year, "crop": crop, "subset": subset,
                        "grid_centres": int(eligible.sum()),
                        "centres_with_valid_area": int((eligible & valid).sum()),
                        "centres_with_positive_area": int(present.sum()),
                        "distinct_area_pixels": int(np.unique(cell_ids[eligible]).size),
                        "distinct_positive_area_pixels": int(np.unique(cell_ids[present]).size),
                    })
    with OUTPUT.open("w", encoding="utf-8", newline="") as dest:
        writer = csv.DictWriter(dest, fieldnames=records[0].keys(), lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)
    print(f"Wrote {len(records)} coverage summaries to {OUTPUT.name}")


if __name__ == "__main__":
    main()
