# Ethiopia LSMS Wave 4 — Household Cover Dashboard

An interactive Streamlit dashboard built on the **Ethiopia Living Standards Measurement Study – Integrated Surveys on Agriculture (LSMS-ISA), Wave 4** household cover file. It summarizes household counts, household size, urban/rural residence, and fieldwork progress across Ethiopia's 11 regions.

![Dashboard preview](output/preview.png)

> If the image above doesn't render, run the app and take a screenshot, then drop it at `output/preview.png`.

---

## What this project does

- Loads the raw Wave 4 household cover file (`sect_cover_hh_w4.csv`)
- Cleans and decodes survey codes (`saq01`, `saq04`, `saq09`, `saq13`, `saq14`, …)
- Maps region codes to names using the official Ethiopia LSMS region coding
- Flags a small number of records with bogus pre-2019 interview dates
- Provides an interactive dashboard with sidebar filters and CSV export

---

## Data

| File | Description |
|---|---|
| `data/sect_cover_hh_w4.csv` | Raw household cover file — **do not edit** |
| `data/local_area_unit_conversion.csv` | Region / zone / woreda lookup table |

Source: [World Bank LSMS-ISA — Ethiopia](https://microdata.worldbank.org/index.php/catalog/lsms)

### Variables used

| Raw column | Meaning | Notes |
|---|---|---|
| `household_id` | Household identifier | Kept as string (leading zeros matter) |
| `ea_id` | Enumeration area ID | Cluster identifier |
| `saq01` | Region code | Mapped to names |
| `saq02` | Zone code | |
| `saq03` | Woreda code | |
| `saq04` | City code | 1, 2, 3, 4, 8 (urban hierarchy) |
| `saq09` | Household size | Real household count |
| `saq13` | Completed post-planting questionnaire | Yes / No |
| `saq14` | Residence | 1 = Rural, 2 = Urban |
| `pw_w4` | Household weight | Used for weighted statistics |
| `InterviewStart` | Timestamp | Filtered to 2019 only for time series |

Columns `saq11`, `saq12`, `saq17`, `saq18`, `saq21` are confidential and are dropped during cleaning.

---

## Project structure

```
data-dashboard-project/
├── data/
│   ├── sect_cover_hh_w4.csv
│   └── local_area_unit_conversion.csv
├── src/
│   └── dashboard.py
├── output/
│   └── sect_cover_hh_w4_clean.csv
├── requirements.txt
└── README.md
```

---

## Setup

### 1. Clone / open the project

```powershell
cd C:\Users\hp\data-dashboard-project
```

### 2. Create a virtual environment (recommended)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

---

## Running the dashboard

```powershell
python -m streamlit run src\dashboard.py
```

Then open **http://localhost:8501** in your browser.

> Using `python -m streamlit` avoids the "streamlit is not recognized" error that happens when the Scripts folder isn't on your PATH.

To stop the app, press **Ctrl+C** in the terminal.

---

## Running the diagnostics-only mode

The same script also runs as a plain Python file — no Streamlit needed:

```powershell
python src\dashboard.py
```

This prints summary statistics and writes `output/sect_cover_hh_w4_clean.csv`.

---

## Dashboard features

| Section | Content |
|---|---|
| **KPI row** | Households, mean HH size, median HH size, urban share, post-planting completion |
| **Region bar** | Households per region (horizontal bar) |
| **Residence donut** | Urban vs Rural split |
| **HH size histogram** | Distribution split by residence |
| **HH size boxplot** | By region |
| **Urban vs Rural violin** | Side-by-side comparison |
| **Interviews over time** | Daily count of interviews |
| **Weighted stats** | Weighted vs unweighted mean HH size using `pw_w4` |
| **Data explorer** | Filtered table + CSV download button |

### Sidebar filters

- Region (multi-select)
- Residence (Urban / Rural)
- Completed post-planting (Yes / No)
- Household size range (slider)
- Use only valid 2019 interview dates (checkbox)

Every filter updates every chart instantly.

---

## Key findings (from the current data)

- **Sample:** 6,770 households across all 11 Ethiopian regions
- **Mean household size:** 4.24 (median 4, max 19)
- **Residence:** 3,655 Urban / 3,115 Rural — the sample deliberately over-samples urban areas; use `pw_w4` for population-level estimates
- **Post-planting completion:** 2,774 Yes / 3,996 No
- **Interview window:** June–September 2019 (23 records with bogus 2014–2018 dates are flagged and excluded from time series)

---

## Notes and caveats

1. **Sex of household head** is *not* in this file — it lives in the roster file (`sect1_hh_w4.csv`). It is therefore not shown in the dashboard.
2. **`saq04` (city code)** and **`saq14` (residence)** use Ethiopian LSMS code conventions. Verified against the Wave 4 basic information document.
3. The 23 records with pre-2019 interview dates are data-entry artifacts; they are excluded from the interviews-over-time chart but kept in the main dataset.
4. Weights (`pw_w4`) are required for population-representative statistics.

---

## License and attribution

Data: World Bank LSMS-ISA Ethiopia Wave 4 (public, anonymized microdata).
Code: Free to reuse with attribution.

---

## Author

Built as a data-cleaning and visualization portfolio project.