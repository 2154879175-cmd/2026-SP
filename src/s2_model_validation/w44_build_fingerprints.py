"""Build fixed pre-May weather fingerprints from NASA POWER daily data."""
import csv
import datetime as dt
import hashlib
import json
import subprocess
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlencode

from rasterio.features import bounds

from w41_pair_county_yield import DOWNLOAD, EXTERNAL, INPUT, OUTPUT

HEBEI = EXTERNAL / "w42_sjz_winter_wheat.csv"
PROVINCES = ("河北省", "山东省")
PARAMETERS = ("T2M", "T2M_MIN", "T2M_MAX", "PRECTOTCORR")
FEATURES = ("autumn_gdd0", "winter_cold_days", "winter_precip_mm",
            "spring_gdd0", "spring_precip_mm", "april_hot_days")


def counties():
    names = {}
    for source in (INPUT, HEBEI):
        with source.open(encoding="utf-8-sig", newline="") as data:
            for row in csv.DictReader(data):
                if row["province"] in PROVINCES:
                    names[row["shape_id"]] = (row["province"], row["county"])
    return names


def daily_weather(key, geometry):
    left, bottom, right, top = bounds(geometry)
    lon, lat = round((left+right)/2, 5), round((bottom+top)/2, 5)
    query = urlencode({"parameters": ",".join(PARAMETERS), "community": "AG", "longitude": lon,
                       "latitude": lat, "start": "20161001", "end": "20210430",
                       "format": "JSON", "time-standard": "LST"})
    url = "https://power.larc.nasa.gov/api/temporal/daily/point?" + query
    dest = DOWNLOAD / f"w44_power_{key}.json"
    cached = dest.is_file()
    raw = dest.read_bytes() if cached else subprocess.run(
        ["curl", "-fsSL", "--retry", "2", "--connect-timeout", "12", "--max-time", "60", url],
        check=True, capture_output=True,
    ).stdout
    result = json.loads(raw)
    if "MERRA2" not in result["header"]["sources"] or result["header"]["time_standard"] != "LST":
        raise ValueError(f"Unexpected POWER data source or time standard for {key}")
    days = result["properties"]["parameter"]
    return (lon, lat), days, (dest, raw if not cached else None, url, hashlib.sha256(raw).hexdigest())


def fingerprint(days, year):
    start, end = dt.date(year-1, 10, 1), dt.date(year, 4, 30)
    autumn_gdd, cold_days, winter_rain, spring_gdd, spring_rain, hot_days = (0,)*6
    for i in range((end-start).days+1):
        date = start+dt.timedelta(days=i)
        key = date.strftime("%Y%m%d")
        tmean, tmin, tmax, rain = (days[name][key] for name in PARAMETERS)
        if tmin < -80 or tmax > 65 or not tmin <= tmean <= tmax or rain < 0:
            raise ValueError(f"Invalid source weather for {key}")
        if date.month in (10, 11):
            autumn_gdd += max(tmean, 0)
        if date.month in (12, 1, 2):
            cold_days += tmin < -5
            winter_rain += rain
        if date.month in (3, 4):
            spring_gdd += max(tmean, 0)
            spring_rain += rain
        if date.month == 4:
            hot_days += tmax >= 25
    return (round(autumn_gdd, 4), cold_days, round(winter_rain, 4), round(spring_gdd, 4),
            round(spring_rain, 4), hot_days)


def main():
    names = counties()
    boundaries = json.loads((DOWNLOAD / "geoBoundaries-CHN-ADM3.geojson").read_text(encoding="utf-8"))
    shapes = {f["properties"]["shapeID"]: f["geometry"] for f in boundaries["features"]}
    rows, sources = [], []
    with ThreadPoolExecutor(max_workers=3) as pool:
        requests = {key: pool.submit(daily_weather, key, shapes[key]) for key in names}
        for key, future in sorted(requests.items()):
            (lon, lat), days, (dest, raw, url, sha256) = future.result()
            yearly = [(year, fingerprint(days, year)) for year in range(2017, 2022)]
            if raw is not None:
                dest.write_bytes(raw)
            signature = hashlib.sha256(json.dumps(days, sort_keys=True).encode()).hexdigest()[:16]
            rows.extend([key, *names[key], year, lon, lat, signature, *values] for year, values in yearly)
            sources.append({"shape_id": key, "url": url, "sha256": sha256})
    with (OUTPUT / "w44_power_fingerprints.csv").open("w", encoding="utf-8", newline="") as output:
        writer = csv.writer(output, lineterminator="\n")
        writer.writerow(("shape_id", "province", "county", "harvest_year", "longitude", "latitude", "weather_series_id", *FEATURES))
        writer.writerows(rows)
    (OUTPUT / "w44_power_sources.json").write_text(json.dumps(sources, indent=2)+"\n", encoding="utf-8")
    print(f"Prepared {len(rows)} county-year fingerprints from {len(names)} points")


if __name__ == "__main__":
    main()
