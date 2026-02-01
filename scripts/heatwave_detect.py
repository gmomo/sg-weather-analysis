#!/usr/bin/env python3
"""
Heatwave detection based on Perkins & Alexander (2013).

CTX90pct: 3+ consecutive days where Tmax > calendar-day 90th percentile of Tmax
CTN90pct: 3+ consecutive days where Tmin > calendar-day 90th percentile of Tmin

Thresholds use a 15-day centred window across the base period (2015-2020).
"""

import json
import math
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_CSV = BASE_DIR / "data" / "imputed_data.csv"
OUTPUT_JSON = BASE_DIR / "data" / "heatwave_data.json"

BASE_PERIOD = (2015, 2020)
MIN_HOURLY = 18        # minimum valid hourly readings per day
HW_MIN_DAYS = 3        # minimum consecutive days for a heatwave
WINDOW_HALF = 7        # 15-day window = day-7 … day+7


def load_daily(csv_path):
    """Load hourly CSV → compute daily Tmax and Tmin per station."""
    print("Loading CSV …")
    df = pd.read_csv(csv_path, parse_dates=["date"], dayfirst=True)
    df = df.dropna(subset=["temperature"])
    df["day"] = df["date"].dt.date

    print("Computing daily Tmax / Tmin …")
    grouped = df.groupby(["station", "day"])["temperature"]
    counts = grouped.count()
    tmax = grouped.max()
    tmin = grouped.min()

    daily = pd.DataFrame({"tmax": tmax, "tmin": tmin, "count": counts})
    daily = daily[daily["count"] >= MIN_HOURLY].drop(columns="count").reset_index()
    daily["day"] = pd.to_datetime(daily["day"])
    daily["doy"] = daily["day"].dt.dayofyear
    daily["year"] = daily["day"].dt.year
    print(f"  {len(daily)} station-days retained (>={MIN_HOURLY} hourly readings)")
    return daily


def compute_thresholds(daily):
    """Calendar-day 90th-percentile thresholds per station (15-day window, base period)."""
    print("Computing 90th-percentile thresholds …")
    base = daily[(daily["year"] >= BASE_PERIOD[0]) & (daily["year"] <= BASE_PERIOD[1])]
    stations = sorted(daily["station"].unique())
    thresholds = {}  # station → {ctx: [366], ctn: [366]}

    for stn in stations:
        stn_data = base[base["station"] == stn]
        ctx = []
        ctn = []
        for doy in range(1, 367):
            # 15-day centred window (wraps around year boundaries)
            doys_in_window = set()
            for offset in range(-WINDOW_HALF, WINDOW_HALF + 1):
                d = doy + offset
                if d < 1:
                    d += 366
                elif d > 366:
                    d -= 366
                doys_in_window.add(d)
            window = stn_data[stn_data["doy"].isin(doys_in_window)]
            ctx_val = float(np.nanpercentile(window["tmax"], 90)) if len(window) else np.nan
            ctn_val = float(np.nanpercentile(window["tmin"], 90)) if len(window) else np.nan
            ctx.append(round(ctx_val, 2) if not math.isnan(ctx_val) else None)
            ctn.append(round(ctn_val, 2) if not math.isnan(ctn_val) else None)
        thresholds[stn] = {"ctx": ctx, "ctn": ctn}

    print(f"  Thresholds computed for {len(stations)} stations")
    return thresholds


def detect_heatwaves(daily, thresholds):
    """Flag exceedance days and group into heatwave events (>=3 consecutive days)."""
    print("Detecting heatwaves …")
    stations = sorted(daily["station"].unique())
    events = []
    daily_records = []

    for stn in stations:
        stn_df = daily[daily["station"] == stn].sort_values("day").copy()
        ctx_map = thresholds[stn]["ctx"]
        ctn_map = thresholds[stn]["ctn"]

        rows = []
        for _, r in stn_df.iterrows():
            doy = int(r["doy"])
            ctx_thresh = ctx_map[doy - 1]
            ctn_thresh = ctn_map[doy - 1]
            ctx_exc = bool(r["tmax"] > ctx_thresh) if ctx_thresh is not None else False
            ctn_exc = bool(r["tmin"] > ctn_thresh) if ctn_thresh is not None else False
            rows.append({
                "date": r["day"].strftime("%Y-%m-%d"),
                "tmax": round(float(r["tmax"]), 2),
                "tmin": round(float(r["tmin"]), 2),
                "ctx_threshold": ctx_thresh,
                "ctn_threshold": ctn_thresh,
                "ctx_exceeded": ctx_exc,
                "ctn_exceeded": ctn_exc,
            })
        daily_records.append({"station": stn, "days": rows})

        # Group consecutive exceedance days into events
        for hw_type, flag_key, temp_key in [
            ("daytime", "ctx_exceeded", "tmax"),
            ("nighttime", "ctn_exceeded", "tmin"),
        ]:
            run = []
            for row in rows:
                if row[flag_key]:
                    run.append(row)
                else:
                    if len(run) >= HW_MIN_DAYS:
                        temps = [r[temp_key] for r in run]
                        events.append({
                            "station": stn,
                            "type": hw_type,
                            "start_date": run[0]["date"],
                            "end_date": run[-1]["date"],
                            "duration": len(run),
                            "peak_temp": round(max(temps), 2),
                            "mean_temp": round(sum(temps) / len(temps), 2),
                        })
                    run = []
            # flush last run
            if len(run) >= HW_MIN_DAYS:
                temps = [r[temp_key] for r in run]
                events.append({
                    "station": stn,
                    "type": hw_type,
                    "start_date": run[0]["date"],
                    "end_date": run[-1]["date"],
                    "duration": len(run),
                    "peak_temp": round(max(temps), 2),
                    "mean_temp": round(sum(temps) / len(temps), 2),
                })

    print(f"  {len(events)} heatwave events detected")
    return events, daily_records


def compute_yearly_aspects(events):
    """HWN, HWF, HWD, HWA, HWM per station per year per type."""
    print("Computing yearly heatwave aspects …")
    # group events
    groups = defaultdict(list)
    for ev in events:
        year = int(ev["start_date"][:4])
        groups[(ev["station"], year, ev["type"])].append(ev)

    aspects = []
    for (stn, year, hw_type), evts in sorted(groups.items()):
        hwn = len(evts)
        hwf = sum(e["duration"] for e in evts)
        hwd = max(e["duration"] for e in evts)
        hwa = max(e["peak_temp"] for e in evts)
        total_days = sum(e["duration"] for e in evts)
        weighted_sum = sum(e["mean_temp"] * e["duration"] for e in evts)
        hwm = round(weighted_sum / total_days, 2) if total_days else None
        aspects.append({
            "station": stn,
            "year": year,
            "type": hw_type,
            "HWN": hwn,
            "HWF": hwf,
            "HWD": hwd,
            "HWA": round(hwa, 2),
            "HWM": hwm,
        })
    print(f"  {len(aspects)} station-year-type aspect rows")
    return aspects


def main():
    daily = load_daily(INPUT_CSV)
    thresholds = compute_thresholds(daily)
    events, daily_records = detect_heatwaves(daily, thresholds)
    aspects = compute_yearly_aspects(events)

    stations = sorted(daily["station"].unique().tolist())

    output = {
        "stations": stations,
        "thresholds": thresholds,
        "daily": daily_records,
        "events": events,
        "yearly_aspects": aspects,
    }

    print(f"Writing {OUTPUT_JSON} …")
    with open(OUTPUT_JSON, "w") as f:
        json.dump(output, f)
    size_mb = OUTPUT_JSON.stat().st_size / (1024 * 1024)
    print(f"Done — {size_mb:.1f} MB written.")


if __name__ == "__main__":
    main()
