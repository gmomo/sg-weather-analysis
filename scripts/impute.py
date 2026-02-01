#!/usr/bin/env python3
"""
Impute missing weather data using:
  Strategy A: Linear interpolation for gaps of 1–2 hours
  Strategy B: Diurnal cycle matching for gaps of 3–24 hours
Gaps >24 hours are left as-is.

Outputs a new CSV with an 'impute_method' column indicating which method was
used for each row/variable combination. The column encodes a comma-separated
list of "variable:strategy" pairs (e.g. "temperature:A,rh:A,wind_speed:B").
Rows with no imputation have an empty impute_method field.
"""

import pandas as pd
import numpy as np
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent

INPUT_CSV = PROJECT_ROOT / "data" / "Hrly data 2015-2020.csv"
OUTPUT_CSV = PROJECT_ROOT / "data" / "imputed_data.csv"

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

# Variables to impute (not rainfall — per the report)
IMPUTE_VARS = ["temperature", "rh", "wind_speed"]


def load_and_clean(path: Path) -> pd.DataFrame:
    print(f"Reading {path} ...")
    df = pd.read_csv(path, encoding="latin-1")
    df.rename(columns=COLUMNS, inplace=True)
    df["date"] = pd.to_datetime(df["date"], format="%d/%m/%Y %H:%M", dayfirst=True)

    # Fix wind direction > 360
    mask = df["wind_dir"].notna()
    df.loc[mask, "wind_dir"] = df.loc[mask, "wind_dir"] % 360

    # Cap RH at 100
    mask_rh = df["rh"].notna() & (df["rh"] > 100)
    df.loc[mask_rh, "rh"] = 100.0

    # Convert wind speed from knots to m/s
    mask_ws = df["wind_speed"].notna()
    df.loc[mask_ws, "wind_speed"] = df.loc[mask_ws, "wind_speed"] * 0.514444

    # Add time components for diurnal profile
    df["month"] = df["date"].dt.month
    df["hour"] = df["date"].dt.hour

    df.sort_values(["station", "date"], inplace=True)
    df.reset_index(drop=True, inplace=True)
    print(f"Loaded {len(df):,} rows, {df['station'].nunique()} stations")
    return df


def find_gaps(is_missing: np.ndarray) -> list[tuple[int, int]]:
    """Return list of (start_idx, length) for each contiguous block of True."""
    gaps = []
    i = 0
    n = len(is_missing)
    while i < n:
        if is_missing[i]:
            start = i
            while i < n and is_missing[i]:
                i += 1
            gaps.append((start, i - start))
        else:
            i += 1
    return gaps


def build_diurnal_profiles(df: pd.DataFrame) -> dict:
    """Compute mean hourly profiles per station per month per variable."""
    profiles = {}
    for var in IMPUTE_VARS:
        profiles[var] = df.groupby(["station", "month", "hour"])[var].mean()
    return profiles


def impute_gap_strategy_b(df_station: pd.DataFrame, indices: list[int],
                          var: str, profiles: dict) -> np.ndarray:
    """
    Diurnal cycle matching for a single gap.
    Uses the station's monthly hourly profile, adjusted by edge offsets.
    """
    station = df_station.iloc[0]["station"]
    rows = df_station.iloc[indices]
    months = rows["month"].values
    hours = rows["hour"].values
    gap_len = len(indices)

    # Get profile values for each hour in the gap
    profile_vals = np.array([
        profiles[var].get((station, m, h), np.nan)
        for m, h in zip(months, hours)
    ])

    # If profile has no data for these hours, can't impute
    if np.all(np.isnan(profile_vals)):
        return np.full(gap_len, np.nan)

    # Get edge values for offset blending
    first_idx = indices[0]
    last_idx = indices[-1]
    col_values = df_station[var].values

    # Value just before the gap
    before_val = np.nan
    if first_idx > 0:
        before_val = col_values[first_idx - 1]

    # Value just after the gap
    after_val = np.nan
    if last_idx < len(col_values) - 1:
        after_val = col_values[last_idx + 1]

    # Profile values at the edges
    before_profile = np.nan
    after_profile = np.nan
    if not np.isnan(before_val) and first_idx > 0:
        prev_row = df_station.iloc[first_idx - 1]
        before_profile = profiles[var].get(
            (station, int(prev_row["month"]), int(prev_row["hour"])), np.nan
        )
    if not np.isnan(after_val) and last_idx < len(col_values) - 1:
        next_row = df_station.iloc[last_idx + 1]
        after_profile = profiles[var].get(
            (station, int(next_row["month"]), int(next_row["hour"])), np.nan
        )

    # Compute offsets
    before_offset = (before_val - before_profile) if (
        not np.isnan(before_val) and not np.isnan(before_profile)
    ) else np.nan
    after_offset = (after_val - after_profile) if (
        not np.isnan(after_val) and not np.isnan(after_profile)
    ) else np.nan

    # Blend offset linearly across the gap
    if not np.isnan(before_offset) and not np.isnan(after_offset):
        weights = np.linspace(1, 0, gap_len)
        offsets = weights * before_offset + (1 - weights) * after_offset
    elif not np.isnan(before_offset):
        offsets = np.full(gap_len, before_offset)
    elif not np.isnan(after_offset):
        offsets = np.full(gap_len, after_offset)
    else:
        offsets = np.zeros(gap_len)

    result = profile_vals + offsets

    # Enforce physical bounds
    if var == "rh":
        result = np.clip(result, 0, 100)
    elif var == "wind_speed":
        result = np.clip(result, 0, None)

    return result


def impute_station(df_station: pd.DataFrame, profiles: dict) -> pd.DataFrame:
    """Apply Strategy A and B to one station's data."""
    df_station = df_station.copy()
    n = len(df_station)

    # Track imputation method per row: list of "var:strategy" strings
    methods = [""] * n

    for var in IMPUTE_VARS:
        is_missing = df_station[var].isna().values
        gaps = find_gaps(is_missing)

        for start, length in gaps:
            if length > 24:
                continue  # Skip gaps > 24 hours

            indices = list(range(start, start + length))

            if length <= 2:
                # Strategy A: linear interpolation
                # Get boundary values
                before_val = np.nan
                after_val = np.nan
                if start > 0:
                    before_val = df_station[var].iloc[start - 1]
                if start + length < n:
                    after_val = df_station[var].iloc[start + length]

                if not np.isnan(before_val) and not np.isnan(after_val):
                    interp = np.linspace(before_val, after_val, length + 2)[1:-1]
                elif not np.isnan(before_val):
                    interp = np.full(length, before_val)
                elif not np.isnan(after_val):
                    interp = np.full(length, after_val)
                else:
                    continue  # No boundary values, skip

                if var == "rh":
                    interp = np.clip(interp, 0, 100)
                elif var == "wind_speed":
                    interp = np.clip(interp, 0, None)

                df_station.iloc[indices, df_station.columns.get_loc(var)] = interp
                strategy = "A"
            else:
                # Strategy B: diurnal cycle matching (3–24 hours)
                filled = impute_gap_strategy_b(df_station, indices, var, profiles)
                if np.all(np.isnan(filled)):
                    continue
                df_station.iloc[indices, df_station.columns.get_loc(var)] = filled
                strategy = "B"

            # Record method
            for idx in indices:
                tag = f"{var}:{strategy}"
                if methods[idx]:
                    methods[idx] += "," + tag
                else:
                    methods[idx] = tag

    df_station["impute_method"] = methods
    return df_station


def main():
    df = load_and_clean(INPUT_CSV)

    print("Building diurnal profiles ...")
    profiles = build_diurnal_profiles(df)

    stations = sorted(df["station"].unique())
    print(f"Imputing {len(stations)} stations ...")

    results = []
    for i, st in enumerate(stations):
        df_st = df[df["station"] == st].copy()
        df_st = impute_station(df_st, profiles)
        results.append(df_st)
        # Count imputed rows
        imputed = (df_st["impute_method"] != "").sum()
        print(f"  [{i+1}/{len(stations)}] {st}: {imputed:,} rows imputed")

    df_out = pd.concat(results, ignore_index=True)
    df_out.sort_values(["station", "date"], inplace=True)

    # Print summary
    total_imputed = (df_out["impute_method"] != "").sum()
    a_count = df_out["impute_method"].str.contains(":A", na=False).sum()
    b_count = df_out["impute_method"].str.contains(":B", na=False).sum()
    print(f"\nImputation complete:")
    print(f"  Total rows with imputation: {total_imputed:,}")
    print(f"  Rows using Strategy A (linear, 1-2h): {a_count:,}")
    print(f"  Rows using Strategy B (diurnal, 3-24h): {b_count:,}")

    # Show remaining missing
    print(f"\nRemaining missing after imputation:")
    for var in IMPUTE_VARS:
        before = df[var].isna().sum()
        after = df_out[var].isna().sum()
        filled = before - after
        print(f"  {var}: {before:,} -> {after:,} ({filled:,} filled, {filled/before*100:.1f}%)")

    # Drop helper columns, format output
    df_out.drop(columns=["month", "hour", "visibility"], inplace=True, errors="ignore")
    df_out["date"] = df_out["date"].dt.strftime("%d/%m/%Y %H:%M")

    # Round numeric columns
    for col in ["temperature", "rh", "wind_speed", "wind_dir", "rainfall", "duration", "global_rad"]:
        if col in df_out.columns:
            df_out[col] = df_out[col].round(2)

    print(f"\nWriting {OUTPUT_CSV} ...")
    df_out.to_csv(OUTPUT_CSV, index=False)
    size_mb = OUTPUT_CSV.stat().st_size / 1_048_576
    print(f"Done. Output size: {size_mb:.1f} MB")


if __name__ == "__main__":
    main()
