#!/usr/bin/env python3
"""Preprocess hourly weather data (2015-2020) into aggregated JSON for the dashboard."""

import json
import math
import pandas as pd
import numpy as np
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent

INPUT_CSV = PROJECT_ROOT / "data" / "Hrly data 2015-2020.csv"
OUTPUT_JSON = PROJECT_ROOT / "data" / "dashboard_data.json"

COLUMNS = {
    "DATE Asia/Singapore (+0800)": "date",
    "ID_STATION": "station",
    "Temperature (°C)": "temperature",
    "RH (%)": "rh",
    "Scalar Mean Wind Direction (°)": "wind_dir",
    "Scalar Mean Wind Speed (kts)": "wind_speed",
    "Total Rainfall (mm)": "rainfall",
    "Total Duration (mins)": "duration",
    "Visibility": "visibility",
    "Global Rad (MJ/m²)": "global_rad",
}

VARS_FOR_DASHBOARD = ["temperature", "rh", "wind_speed", "rainfall", "global_rad"]
VAR_LABELS = {
    "temperature": "Temperature (°C)",
    "rh": "RH (%)",
    "wind_speed": "Wind Speed (m/s)",
    "rainfall": "Rainfall (mm)",
    "global_rad": "Global Radiation (MJ/m²)",
}


def load_and_clean(path: Path) -> pd.DataFrame:
    print(f"Reading {path} ...")
    df = pd.read_csv(path, encoding="latin-1")
    df.rename(columns=COLUMNS, inplace=True)

    # Parse dates
    df["date"] = pd.to_datetime(df["date"], format="%d/%m/%Y %H:%M", dayfirst=True)
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df["hour"] = df["date"].dt.hour
    df["ym"] = df["date"].dt.to_period("M").astype(str)  # e.g. "2015-01"
    df["ymd"] = df["date"].dt.strftime("%Y-%m-%d")

    # Drop Visibility (82.5% missing)
    df.drop(columns=["visibility"], inplace=True, errors="ignore")

    # Fix wind direction > 360
    mask = df["wind_dir"].notna()
    df.loc[mask, "wind_dir"] = df.loc[mask, "wind_dir"] % 360

    # Cap RH at 100
    mask_rh = df["rh"].notna() & (df["rh"] > 100)
    df.loc[mask_rh, "rh"] = 100.0

    # Convert wind speed from knots to m/s (1 kt = 0.514444 m/s)
    mask_ws = df["wind_speed"].notna()
    df.loc[mask_ws, "wind_speed"] = df.loc[mask_ws, "wind_speed"] * 0.514444

    print(f"Loaded {len(df):,} rows, {df['station'].nunique()} stations")
    return df


def missing_data_summary(df: pd.DataFrame) -> list:
    """Overall % missing per station per variable."""
    stations = sorted(df["station"].unique())
    rows = []
    for st in stations:
        sub = df[df["station"] == st]
        total = len(sub)
        row = {"station": st}
        for v in VARS_FOR_DASHBOARD:
            missing = int(sub[v].isna().sum())
            row[v] = round(missing / total * 100, 1) if total > 0 else 0
        rows.append(row)
    return rows


def monthly_aggregates(df: pd.DataFrame) -> list:
    """Monthly averages (and rainfall totals) per station."""
    records = []
    grouped = df.groupby(["station", "ym"])
    for (st, ym), g in grouped:
        total = len(g)
        rec = {"station": st, "ym": ym}
        # Temperature, RH, wind_speed: mean; rainfall: sum; global_rad: mean
        for v in VARS_FOR_DASHBOARD:
            valid = g[v].dropna()
            missing_pct = round((total - len(valid)) / total * 100, 1)
            rec[f"{v}_missing_pct"] = missing_pct
            if v == "rainfall":
                rec[v] = round(float(valid.sum()), 2) if len(valid) > 0 else None
            else:
                rec[v] = round(float(valid.mean()), 2) if len(valid) > 0 else None
        records.append(rec)
    return records


def monthly_missing_counts(df: pd.DataFrame) -> list:
    """Missing data count per station per month per variable (for timeline chart)."""
    records = []
    grouped = df.groupby(["station", "ym"])
    for (st, ym), g in grouped:
        rec = {"station": st, "ym": ym}
        for v in VARS_FOR_DASHBOARD:
            rec[v] = int(g[v].isna().sum())
        records.append(rec)
    return records


def hourly_profiles(df: pd.DataFrame) -> list:
    """Average by hour-of-day per station (across all years)."""
    records = []
    grouped = df.groupby(["station", "hour"])
    for (st, h), g in grouped:
        rec = {"station": st, "hour": int(h)}
        for v in ["temperature", "rh"]:
            valid = g[v].dropna()
            rec[v] = round(float(valid.mean()), 2) if len(valid) > 0 else None
        records.append(rec)
    return records


def daily_temp_minmax(df: pd.DataFrame) -> list:
    """Daily min and max temperature per station."""
    records = []
    grouped = df.groupby(["station", "ymd"])
    for (st, ymd), g in grouped:
        valid = g["temperature"].dropna()
        if len(valid) == 0:
            continue
        records.append({
            "station": st,
            "date": ymd,
            "t_min": round(float(valid.min()), 1),
            "t_max": round(float(valid.max()), 1),
        })
    return records


def yearly_summary(df: pd.DataFrame) -> list:
    """Yearly averages per station."""
    records = []
    grouped = df.groupby(["station", "year"])
    for (st, yr), g in grouped:
        rec = {"station": st, "year": int(yr)}
        for v in VARS_FOR_DASHBOARD:
            valid = g[v].dropna()
            if v == "rainfall":
                rec[v] = round(float(valid.sum()), 2) if len(valid) > 0 else None
            else:
                rec[v] = round(float(valid.mean()), 2) if len(valid) > 0 else None
        records.append(rec)
    return records


def sanitize(obj):
    """Replace NaN/inf with None for JSON serialization."""
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    if isinstance(obj, dict):
        return {k: sanitize(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [sanitize(v) for v in obj]
    return obj


def main():
    df = load_and_clean(INPUT_CSV)

    stations = sorted(df["station"].unique().tolist())
    print(f"Stations: {stations}")

    print("Computing missing data summary ...")
    missing_summary = missing_data_summary(df)

    print("Computing monthly aggregates ...")
    monthly = monthly_aggregates(df)

    print("Computing monthly missing counts ...")
    missing_timeline = monthly_missing_counts(df)

    print("Computing hourly profiles ...")
    hourly = hourly_profiles(df)

    print("Computing daily temperature min/max ...")
    daily_temp = daily_temp_minmax(df)

    print("Computing yearly summary ...")
    yearly = yearly_summary(df)

    payload = {
        "stations": stations,
        "var_labels": VAR_LABELS,
        "missing_summary": missing_summary,
        "monthly": monthly,
        "missing_timeline": missing_timeline,
        "hourly": hourly,
        "daily_temp": daily_temp,
        "yearly": yearly,
    }

    payload = sanitize(payload)

    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    print(f"Writing {OUTPUT_JSON} ...")
    with open(OUTPUT_JSON, "w") as f:
        json.dump(payload, f)

    size_mb = OUTPUT_JSON.stat().st_size / 1_048_576
    print(f"Done. Output size: {size_mb:.1f} MB")


if __name__ == "__main__":
    main()
