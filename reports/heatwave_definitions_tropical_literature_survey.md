# Heatwave Definitions for Tropical Weather: A Literature Survey

## 1. Introduction

Heatwaves are among the most dangerous natural hazards globally, yet defining them in tropical regions remains a significant scientific challenge. Unlike mid-latitude regions with pronounced seasonal cycles and large day-to-day temperature variability, tropical climates exhibit narrow temperature distributions (seasonal amplitude ~6 deg C vs ~20 deg C in mid-latitudes), making standard heatwave definitions inadequate or misleading. This report surveys the existing literature on heatwave definitions, with particular emphasis on their applicability to tropical weather.

---

## 2. General Heatwave Definitions

### 2.1 WMO Definition
The World Meteorological Organization defines a heatwave as **5 or more consecutive days** during which the daily maximum temperature exceeds the average maximum temperature by **5 deg C or more** (WMO). A more practical WMO definition describes heatwaves as *"periods of unusually hot and dry or hot and humid weather that have a subtle onset and cessation, a duration of at least two to three days and a discernible impact on human activities"* (WMO).

**Critical limitation for tropics:** Using the WMO 5-day/5 deg C definition, most tropical regions registered **zero heatwave events** over 1983-2015, while continental and polar regions averaged 80-90 events (Perkins-Kirkpatrick & Lewis, 2020; Climatic Change, 2023).

### 2.2 Absolute Threshold Definitions
Some countries use fixed temperature thresholds:
- **India (IMD):** Heatwave declared when Tmax >= 40 deg C (plains) or >= 30 deg C (hilly regions), with departure from normal of 5-6 deg C. Severe heatwave when Tmax >= 45 deg C regardless of normal. Must persist at 2+ stations for 2+ consecutive days.
- **US (NWS):** Based on Heat Index values; watches/warnings when daytime heat index > 103 deg F and nighttime > 81 deg F for 48+ hours.

### 2.3 Percentile-Based (Relative) Definitions
The most common approach uses daily temperature exceeding the **90th, 92.5th, 95th, or 97.5th percentile** of the historical distribution for 2+ or 3+ consecutive days (Perkins & Alexander, 2013).

**Tropical challenge:** All percentile-based definitions show **very large changes in heatwave frequency and duration** over tropical regions due to the narrow temperature distributions, potentially overestimating trend magnitudes (Perkins-Kirkpatrick & Lewis, 2020).

---

## 3. Heatwave Metrics and Indices

### 3.1 Excess Heat Factor (EHF)
Developed by Nairn & Fawcett (2015), the EHF is a two-component index based on 3-day averaged daily mean temperature:
- **Significance component:** Excess heat relative to the climatological 95th percentile (long-term adaptation).
- **Acclimatisation component:** Excess heat relative to the previous 30 days (short-term adaptation).
- Severity classified using the 85th percentile of positive EHF values; extreme = 3x the severe threshold.

**Tropical behaviour:** EHF values are **lowest in tropical regions** due to reduced daily temperature variability. Smaller temperature excursions are needed to trigger severe heatwaves in the tropics compared to mid-latitudes. A key limitation is that EHF uses only ambient temperature, potentially underestimating severity in **humid tropical regions** where humidity amplifies health impacts (Nairn & Fawcett, 2015; PMC).

### 3.2 Heat Wave Magnitude Index (HWMI / HWMId)
Proposed by Russo et al. (2014, 2015):
- A heatwave = 3+ consecutive days with Tmax above the **90th percentile** (31-day running window, 1981-2010 baseline).
- HWMI normalizes excess temperatures, enabling **cross-regional comparison** of heatwave severity.
- HWMId (daily version) addresses saturation issues in HWMI at high temperatures.
- Categories range from "normal" to "ultra extreme" (HWMI > 32).

**Tropical relevance:** The HWMI was explicitly designed to allow comparison across climatic zones, addressing the problem that "temperatures considered normal in one region can be categorized as hot/cold in others" (Russo et al., 2014).

### 3.3 Perkins-Kirkpatrick Heatwave Aspects
Perkins & Alexander (2013) and Perkins (2015) proposed a suite of metrics:
- **HWN:** Number of heatwave events per year
- **HWD:** Duration of the longest event
- **HWF:** Total heatwave days per year
- **HWA:** Hottest day of the hottest event
- **HWM:** Average magnitude across all events

These use the CTX90pct threshold (calendar-day 90th percentile of Tmax, 15-day window).

---

## 4. The Humidity Problem: Wet-Bulb and Heat Index Approaches

### 4.1 Why Temperature Alone Is Insufficient in the Tropics
In humid tropical environments, the body's ability to cool via sweat evaporation is severely impaired. The same air temperature is **far more dangerous** in humid conditions than in dry conditions. Dry-bulb temperature metrics systematically underestimate heat stress in tropical regions (Sherwood & Huber, 2010; Raymond et al., 2020).

### 4.2 Wet-Bulb Temperature (Tw)
- A **Tw of 35 deg C** is considered the upper limit of human survivability, even for fit individuals at rest in shade with ventilation (Sherwood & Huber, 2010).
- Limiting global warming to 1.5 deg C would prevent most of the tropics from reaching this threshold.
- By late 21st century under business-as-usual, South Asian extremes of Tw are projected to **approach or exceed** 35 deg C in some locations (Im et al., 2017, Science Advances).

### 4.3 Wet-Bulb Globe Temperature (WBGT)
- An ISO-approved metric combining: air temperature (10%), natural wet-bulb temperature (70%), and black globe/radiant temperature (20%).
- Originally developed by US military in the 1950s.
- Better at capturing actual heat stress than dry-bulb temperature or heat index alone.
- By 2080, extreme WBGT events could increase by a **factor of 100-250 in the tropics** (Li et al., 2020, PMC).

### 4.4 Heat Index
- Combines ambient temperature and relative humidity.
- Used by NWS for heat warnings.
- Limitation: designed for shady conditions, does not account for solar radiation or wind.

### 4.5 Humid Heatwaves in the Tropics (2025)
A 2025 study in Nature Communications (Birch et al.) found that:
- In **moisture-limited** tropical environments, humid heatwaves occur **during or immediately after** enhanced rainfall.
- In **energy-limited** tropical environments, humid heatwaves occur after **suppression of rainfall** for 2+ days.
- Daily rainfall variability is a key control on humid heatwave occurrence in the tropics and subtropics.

---

## 5. Regional Heatwave Definitions in Tropical Countries

### 5.1 India
- **IMD Criteria:** Tmax >= 40 deg C (plains) / >= 30 deg C (hills); departure from normal >= 5 deg C (heatwave) or >= 7 deg C (severe). Tmax >= 45 deg C automatically qualifies. Must persist 2+ days at 2+ stations in a meteorological sub-division.
- Recent work incorporates both Tmax and Tmin, recognizing that warm nights compound health impacts.
- Pre-monsoon months (March-June) are peak heatwave season, with significant intensification in 2016, 2019, 2022, and 2023.

### 5.2 Southeast Asia
- No standardized regional heatwave definition exists.
- The unprecedented April-May 2023 heatwave broke temperature records across all continental SEA countries, with Thailand recording 49 deg C (npj Climate and Atmospheric Science, 2024).
- Malaysia: Recent studies (Muhammad et al., 2024, Scientific Reports) have proposed heatwave indices using both Tmax and Tmin to evaluate shifts in heatwave features in Peninsular Malaysia.

### 5.3 West Africa and the Sahel
- Absolute threshold approaches are poorly suited due to reduced seasonal thermal amplitude (~6 deg C).
- **Relative thresholds** (percentile-based) are generally adopted.
- Sahelian heatwaves: typically 1-2 events/year, lasting 3-5 days, with severe magnitude. Eastern Sahel is more at risk than western Sahel (Barbier et al., 2020, Climate Dynamics).
- Daytime and nighttime heatwaves are **distinct phenomena** in the Sahel; concomitant events are rare.
- Humidity plays an important role in nighttime events.
- The April 2024 Sahel heatwave (Tmax > 45 deg C, Tmin 32 deg C in Burkina Faso; 48.5 deg C in Kayes, Mali) was attributed to climate change (World Weather Attribution).

### 5.4 Tropical Australia
- Bureau of Meteorology uses EHF-based 7-day heatwave severity maps (operational since 2014).
- Tropical northern Australia shows lower EHF values but requires smaller temperature excursions for severe classification.

---

## 6. Key Challenges and Open Questions

| Challenge | Description |
|-----------|-------------|
| **Low variability** | Tropical temperature distributions are narrow, making both absolute and percentile thresholds problematic |
| **Humidity omission** | Most standard metrics use dry-bulb temperature only, underestimating tropical heat stress |
| **Nighttime heat** | Warm tropical nights prevent recovery; most definitions focus on daytime Tmax |
| **Urban heat islands** | Rapidly urbanizing tropical cities amplify heat exposure beyond what station data capture |
| **Data scarcity** | Many tropical regions lack dense, long-duration station networks for robust baseline estimation |
| **Acclimatisation** | Tropical populations may have higher heat tolerance but lower adaptive capacity (infrastructure, cooling) |
| **No universal definition** | UNDRR and WMO acknowledge that universal numeric limits are not possible due to local factors |

---

## 7. Emerging Consensus and Recommendations from Literature

1. **Composite metrics** incorporating both temperature and humidity (WBGT, Tw, or heat index) are increasingly recommended for tropical heatwave definitions over dry-bulb-only approaches.
2. **Locally calibrated percentile thresholds** (rather than fixed absolute thresholds or global percentiles) are preferred for tropical regions.
3. **Nighttime temperatures** should be incorporated alongside daytime maxima, as warm nights are particularly dangerous in humid tropical climates.
4. **Duration thresholds** of 2-3 consecutive days are generally sufficient for tropical heatwaves (vs. 5 days in WMO definition), reflecting faster health impacts in humid heat.
5. **Health-outcome-driven definitions** that link meteorological thresholds to mortality/morbidity data are gaining traction but require robust health surveillance systems that many tropical countries lack.
6. The **EHF framework** applied with humidity-adjusted indices (apparent temperature or WBGT instead of dry-bulb temperature) shows promise for globally consistent yet locally relevant heatwave monitoring.

---

## 8. Key References

1. Perkins, S.E. & Alexander, L.V. (2013). On the measurement of heat waves. *J. Climate*, 26, 4500-4517.
2. Perkins, S.E. (2015). A review of heat wave metrics from a health perspective. *Int. J. Climatol.*, 35, 4515-4532.
3. Russo, S. et al. (2014). Magnitude of extreme heat waves in present climate and their projection in a warming world. *J. Geophys. Res. Atmos.*, 119, 12500-12512.
4. Nairn, J.R. & Fawcett, R.J.B. (2015). The Excess Heat Factor: A metric for heatwave intensity and its use in classifying heatwave severity. *Int. J. Environ. Res. Public Health*, 12, 227-253.
5. Sherwood, S.C. & Huber, M. (2010). An adaptability limit to climate change due to heat stress. *PNAS*, 107, 9552-9555.
6. Im, E.S. et al. (2017). Deadly heat waves projected in the densely populated agricultural regions of South Asia. *Science Advances*, 3, e1603322.
7. Birch, C.E. et al. (2025). Daily rainfall variability controls humid heatwaves in the global tropics and subtropics. *Nature Communications*.
8. Barbier, J. et al. (2020). Characteristics and thermodynamics of Sahelian heatwaves. *Climate Dynamics*.
9. Guigma, K.H. et al. (2023). Heat wave monitoring over West African cities: uncertainties, characterization and recent trends. *NHESS*, 23, 1313-1333.
10. Muhammad, F.R. et al. (2024). Heatwaves in Peninsular Malaysia: a spatiotemporal analysis. *Scientific Reports*.
11. Freychet, N. et al. (2024). The 2023 Southeast Asia heatwave: characterization, mechanism, predictability and impacts. *npj Clim. Atmos. Sci.*
12. Perkins-Kirkpatrick, S.E. & Lewis, S.C. (2020). Increasing trends in regional heatwaves. *Nature Communications*, 11, 3357.
13. Burgstall, A. et al. (2023). Challenging the universality of heatwave definitions: gridded temperature discrepancies across climate regions. *Climatic Change*.
14. Li, D. et al. (2020). Temperature and humidity based projections of a rapid rise in global heat stress exposure during the 21st century. *PMC*.
15. Patel, D. et al. (2024). Temperature projections and heatwave attribution scenarios over India: A systematic review. *PMC*.
16. WMO (2023). Guidelines on the Definition and Characterization of Extreme Weather and Climate Events.
17. UNDRR. Heatwave Hazard Definition.
18. World Weather Attribution (2024). Extreme Sahel heatwave attribution.
19. Nairn, J.R. & Fawcett, R.J.B. (2018). Performance of Excess Heat Factor Severity as a Global Heatwave Health Impact Index. *Int. J. Environ. Res. Public Health*.
20. Robinson, P.J. (2001). On the definition of a heat wave. *J. Appl. Meteorol. Climatol.*, 40, 762-775.
