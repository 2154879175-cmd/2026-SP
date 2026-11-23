# -*- coding: utf-8 -*-
"""Compare Pinggu wheat yield models with and without lagged crop area."""
import numpy as np
import pandas as pd
import rasterio
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, r2_score, root_mean_squared_error
from sklearn.model_selection import LeaveOneGroupOut
from sklearn.pipeline import make_pipeline

from w38_crop_area_support import CROPS, INTERMEDIATE, RASTERS, ROOT


def main():
    grid = pd.read_csv(INTERMEDIATE / "zenodo_yield_2021_grid.csv")
    grid = grid.loc[grid["zenodo_yield_tha"].notna()].reset_index(drop=True)
    target = grid["zenodo_yield_tha"].to_numpy()
    coords = grid[["lon", "lat"]]
    env_columns = pd.read_csv(ROOT / "Outputs" / "pinggu_environmental_data.csv", nrows=0).columns
    env = grid[env_columns.drop(["lon", "lat"])]
    wheat_band, wheat_code = CROPS["wheat"]
    with rasterio.open(RASTERS / "CHN_2020.tif") as src:
        if src.crs is None or src.crs.to_epsg() != 4326 or src.count != 14:
            raise ValueError("Unexpected CRS or band count in the 2020 area raster")
        if src.descriptions[wheat_band - 1] not in (None, "", wheat_code):
            raise ValueError("Unexpected wheat band description in the 2020 area raster")
        rows, cols = rasterio.transform.rowcol(src.transform, coords.lon, coords.lat)
        rows, cols = np.asarray(rows), np.asarray(cols)
        if not ((rows >= 0) & (rows < src.height) & (cols >= 0) & (cols < src.width)).all():
            raise ValueError("Yield centres outside the 2020 area raster")
        area = src.read(wheat_band, masked=True)[rows, cols].astype(float).filled(np.nan)
        groups = rows * src.width + cols
    if not np.isfinite(area).all() or (area < 0).any():
        raise ValueError("A yield centre lacks valid 2020 crop area")

    predictions = pd.DataFrame({
        "grid_id": grid["grid_id"], "lon": coords.lon, "lat": coords.lat,
        "area_row": rows, "area_col": cols, "wheat_area_2020_ha": area,
        "rs_wheat_yield_2021_tha": target,
    })
    models = {"fold_mean": None, "environment": env, "environment_plus_area": env.assign(area_ha=area)}
    for name, features in models.items():
        predicted = np.full(len(grid), np.nan)
        for train, test in LeaveOneGroupOut().split(grid, target, groups):
            if features is None:
                predicted[test] = target[train].mean()
            else:
                model = make_pipeline(
                    SimpleImputer(strategy="median"),
                    RandomForestRegressor(n_estimators=300, min_samples_leaf=2, random_state=42),
                )
                model.fit(features.iloc[train], target[train])
                predicted[test] = model.predict(features.iloc[test])
        predictions[name] = predicted

    summary = [
        {
            "model": name, "n_centres": len(grid), "n_held_out_area_pixels": np.unique(groups).size,
            "pooled_r2": r2_score(target, predictions[name]),
            "rmse_tha": root_mean_squared_error(target, predictions[name]),
            "mae_tha": mean_absolute_error(target, predictions[name]),
        }
        for name in models
    ]
    out = ROOT / "Outputs" / "reports"
    predictions.to_csv(out / "w39_pinggu_wheat_area_oof.csv", index=False, float_format="%.8f", lineterminator="\n")
    pd.DataFrame(summary).to_csv(
        out / "w39_pinggu_wheat_area_metrics.csv", index=False, float_format="%.8f", lineterminator="\n"
    )
    print(pd.DataFrame(summary).to_string(index=False))


if __name__ == "__main__":
    main()
