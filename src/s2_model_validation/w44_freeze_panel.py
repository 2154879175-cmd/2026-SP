"""Join weather and yield and freeze W42 eligibility, county IDs, and fold membership."""
import pandas as pd

from w41_pair_county_yield import OUTPUT
from w44_build_fingerprints import FEATURES, PROVINCES

YEARS = range(2017, 2022)
KEY = ["shape_id", "harvest_year"]
SCENARIOS = ("primary", "strict", "unscreened")


def split_sets(panel):
    year = panel.harvest_year
    province = panel.province
    for area in PROVINCES:
        yield "leave_region", area, province.ne(area), province.eq(area)
    for target_year in range(2019, 2022):
        yield "forward_year", str(target_year), year.lt(target_year), year.eq(target_year)
        for area in PROVINCES:
            yield ("region_and_future", f"{area}_{target_year}",
                   province.ne(area) & year.lt(target_year), province.eq(area) & year.eq(target_year))


def main():
    paired = pd.concat([pd.read_csv(OUTPUT / f"w43_county_yield_pairing_{year}.csv")
                        for year in YEARS], ignore_index=True)
    weather = pd.read_csv(OUTPUT / "w44_power_fingerprints.csv")
    panel = paired.merge(weather[KEY + ["weather_series_id", *FEATURES]], on=KEY, how="left", validate="one_to_one")
    in_regions = panel.province.isin(PROVINCES)
    proportional_area = panel.remote_area_to_stats_sown_area
    core = (in_regions & panel.county.ne("泰山区") & panel.stats_kg_ha.gt(0)
            & panel.remote_winter_wheat_kg_ha.gt(0) & panel[list(FEATURES)].notna().all(axis=1))
    panel["unscreened"] = core
    panel["primary"] = core & proportional_area.between(2/3, 1.5)
    panel["strict"] = core & proportional_area.between(0.8, 1.25)
    panel.sort_values(["harvest_year", "province", "county"], inplace=True, ignore_index=True)
    panel.to_csv(OUTPUT / "w44_frozen_panel.csv", index=False, lineterminator="\n")

    membership, coverage = [], []
    for scenario in SCENARIOS:
        eligible = panel.loc[panel[scenario]]
        for scheme, fold, train, test in split_sets(eligible):
            training, testing = eligible.loc[train], eligible.loc[test]
            train_years = training.harvest_year.nunique()
            valid = train_years >= 2 and len(training) >= 4 and len(testing) > 0
            coverage.append((scenario, scheme, fold, len(training), train_years, len(testing), valid))
            if valid:
                if scheme in ("leave_region", "region_and_future"):
                    assert set(training.shape_id).isdisjoint(testing.shape_id)
                    assert set(training.weather_series_id).isdisjoint(testing.weather_series_id)
                if scheme in ("forward_year", "region_and_future"):
                    assert training.harvest_year.max() < testing.harvest_year.min()
                for role, subset in (("train", training), ("test", testing)):
                    membership.extend((scenario, scheme, fold, role, key, year)
                                      for key, year in subset[KEY].itertuples(index=False, name=None))
    pd.DataFrame(membership, columns=["scenario", "scheme", "fold", "role", *KEY]).to_csv(
        OUTPUT / "w44_folds.csv", index=False, lineterminator="\n")
    pd.DataFrame(coverage, columns=["scenario", "scheme", "fold", "train_rows", "train_years",
                                    "test_rows", "usable"]).to_csv(
        OUTPUT / "w44_fold_coverage.csv", index=False, lineterminator="\n")
    print(panel.groupby("province")[list(SCENARIOS)].sum().to_string())


if __name__ == "__main__":
    main()
