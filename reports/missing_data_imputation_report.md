# Missing Data Imputation Report

## 1. Missing Data Profile

| Variable | Missing Count | % Missing | Gap Count | Median Gap | Max Gap |
|---|---|---|---|---|---|
| Temperature | 53,831 | 5.2% | 3,758 | 5 hours | 281 days |
| RH | 115,089 | 11.1% | 8,268 | 4 hours | 366 days |
| Wind Speed | 77,429 | 7.4% | 5,957 | 5 hours | 201 days |
| Rainfall | 35,722 | 3.4% | 472 | 18 hours | 366 days |

### Gap length breakdown

| Variable | 1h | 2–3h | 4–6h | 7–24h | 1–7 days | >7 days |
|---|---|---|---|---|---|---|
| Temperature | 520 | 884 | 1,516 | 507 | 305 | 26 |
| RH | 1,534 | 1,903 | 2,325 | 2,137 | 332 | 37 |
| Wind Speed | 670 | 403 | 3,097 | 1,414 | 339 | 34 |
| Rainfall | 54 | 25 | 24 | 204 | 134 | 31 |

**Key observation:** The majority of gaps are short (1–6 hours), but a small number of very long gaps (>7 days) exist, most likely full station outages. These two categories require different imputation strategies.

### Co-occurrence of missing values

When temperature is missing:
- RH is also missing **98.7%** of the time
- Wind speed is also missing **90.2%** of the time
- Rainfall is also missing **42.5%** of the time

This indicates that most temperature gaps are caused by **full station outages** where all sensors go offline simultaneously. RH has additional independent sensor failures (only 46.2% of its gaps coincide with missing temperature).

### Stations with high missingness (>10%)

| Station | Temperature | RH | Wind Speed | Rainfall |
|---|---|---|---|---|
| S102 | 22.3% | 22.3% | 12.0% | — |
| S122 | — | **47.2%** | — | — |
| S23 | 17.6% | 26.0% | **34.8%** | — |
| S111 | 12.7% | 15.9% | 12.7% | — |
| S44 | — | 21.9% | — | — |
| S25 | — | — | — | 16.7% |


## 2. Recommended Imputation Strategies

### Strategy A: Short gaps (1–2 hours) — Linear Interpolation

**Rationale:** Hourly lag-1 autocorrelation is very high (~0.91 for temperature and RH), meaning the next hour's value is well predicted by adjacent hours. Gaps of 1–2 hours can be filled reliably by simple linear interpolation since conditions change minimally over such short periods.

**Method:**
```python
# Per station, sorted by time
df.groupby('station').apply(
    lambda g: g.sort_values('date').interpolate(method='linear', limit=2)
)
```

**Applicable to:** Temperature, RH, Wind Speed

**Not recommended for:** Rainfall — linear interpolation between 0 and 0 loses any actual rain events that occurred during the gap. Use zero-fill or leave as-is instead.

**Expected accuracy:** High. Over 1–2 hours in tropical Singapore, temperature typically varies by <1°C and RH by <5%, making linear interpolation well-suited.

### Strategy B: Medium gaps (3–24 hours) — Diurnal Cycle Matching

**Rationale:** Gaps of 3 hours or more can span a significant portion of the diurnal cycle. Linear interpolation over these periods would miss temperature peaks/troughs and humidity swings. Using the station's historical hourly profile preserves the shape of the daily cycle.

**Method:**
1. Compute the station's average hourly profile for the same month across other years.
2. Compute the offset between the known values at the gap edges and the profile.
3. Fill the gap using the profile shape, adjusted by the offset.

```python
# Pseudocode
profile = df.groupby(['station', 'month', 'hour'])[var].mean()
for each gap:
    edge_offset = known_value - profile[edge_hour]
    filled = profile[gap_hours] + edge_offset  # blend offset across gap
```

**Applicable to:** Temperature, RH

**For wind speed:** Use the same approach, though wind is noisier and results will be less accurate. Consider using median instead of mean profiles.

**For rainfall:** Do not impute. Rainfall is episodic and cannot be reconstructed from hourly profiles. Flag as missing.

### Strategy C: Long gaps (1–7 days) — Nearby Station Donor

**Rationale:** Singapore is ~50km across. Weather stations in proximity experience similar conditions. When one station has a multi-day outage, nearby stations with data can serve as donors.

**Method:**
1. Pre-compute station-to-station correlations for each variable using overlapping valid periods.
2. For each long gap, select the best-correlated donor station that has data during the gap period.
3. Apply bias correction: `imputed = donor_value + (target_mean - donor_mean)` using the overlapping period's means.

```python
# Compute pairwise station correlations
corr_matrix = df.pivot_table(index='date', columns='station', values=var).corr()

# For a gap in station X, pick best correlated station Y with data
donor = corr_matrix[X].drop(X).idxmax()
bias = target_mean - donor_mean  # from overlapping valid periods
imputed = donor_values + bias
```

**Applicable to:** Temperature, RH, Wind Speed

**Caveat:** Requires that at least one other station has data during the same period. If multiple stations are down simultaneously, this fails.

### Strategy D: Very long gaps (>7 days) — Do Not Impute

**Rationale:** 26–37 gaps exceed 7 days, with the longest being 281–366 days. These represent extended station outages or decommissioning periods. Imputing months of data from other stations introduces too much uncertainty and masks the reality that the station was non-operational.

**Recommendation:** Leave these as missing. Mark them explicitly in analyses as "station offline" periods. If a complete time series is required for modelling, exclude these stations from the affected period rather than fabricating data.


## 3. Rainfall: Special Handling

Rainfall is fundamentally different from the other variables:
- It is **intermittent** (zero-inflated) — most hours have 0mm rainfall
- It cannot be interpolated (a 0–0 interpolation hides actual rain events)
- It is **spatially patchy** — one station may record rain while a nearby station does not

**Recommendation:**
- **Short gaps (1–6h):** If surrounding hours are all 0mm, fill with 0. Otherwise, leave missing.
- **Medium/long gaps:** Do not impute. Report rainfall statistics with appropriate caveats about data completeness.
- **Alternative:** For monthly/daily aggregates, scale up observed totals proportionally: `estimated_total = observed_total * (total_hours / valid_hours)`, but flag this as an estimate.


## 4. Validation Approach

Before applying imputation to the full dataset, validate using artificial gaps:

1. **Select stations with >95% completeness** (e.g., S104, S50, S86).
2. **Artificially remove** known values to create gaps of various lengths (1h, 6h, 24h, 72h).
3. **Apply each imputation method** and compare imputed values to the known truth.
4. **Metrics:** MAE, RMSE, and bias for each variable and gap length.

Expected benchmark targets:
| Variable | 1–6h gap MAE | 7–24h gap MAE |
|---|---|---|
| Temperature | < 0.5°C | < 1.0°C |
| RH | < 3% | < 5% |
| Wind Speed | < 0.5 m/s | < 1.0 m/s |


## 5. Implementation Order

1. **Linear interpolation for gaps <= 2 hours** — handles the shortest gaps with minimal complexity and high accuracy.
2. **Diurnal cycle matching for 3–24 hour gaps** — handles the bulk of remaining gaps. Validate against artificial gaps first.
3. **Nearby station donor for 1–7 day gaps** — requires station correlation analysis. Implement after steps 1–2 are validated.
4. **Flag remaining long gaps** as non-imputable.

After each step, regenerate `dashboard_data.json` and check the dashboard to confirm gap reduction and that imputed values look physically reasonable (e.g., temperature stays within 20–36°C for Singapore).


## 6. Summary Table

| Gap Length | Method | Variables | Confidence |
|---|---|---|---|
| 1–2 hours | Linear interpolation | Temp, RH, Wind | High |
| 3–24 hours | Diurnal cycle matching | Temp, RH, Wind | Medium-High |
| 1–7 days | Nearby station donor | Temp, RH, Wind | Medium |
| >7 days | Do not impute | All | N/A |
| Any length | Zero-fill (if surrounding = 0) | Rainfall only | High |
| Any length | Do not impute (otherwise) | Rainfall | N/A |
