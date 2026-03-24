# Migrant Education Analysis — Canada

An exploratory data analysis of educational attainment differences across visible minority groups in Canada, using Census data (2006, 2011, 2016, 2021) published by Statistics Canada.

The project investigates questions like:
- Which visible minority groups have the highest rates of bachelor's degree attainment?
- Which groups are most over- or under-represented relative to the national average?
- How does the total visible minority population compare to non-visible minority Canadians in terms of education outcomes?
- Are the observed differences statistically significant?

---

## Repository Structure

```
migrant-education-analysis/
├── data/
│   ├── canada_migrant2006.csv
│   ├── canada_migrant2011.csv
│   ├── canada_migrant2016.csv
│   └── canada_migrant2021.csv
├── src/
│   └── (Shiny interactive app — forthcoming)
├── migrant_education_analysis.ipynb   # Main EDA notebook
└── README.md
```

---

## Data Source

| Field | Detail |
|---|---|
| **Publisher** | Statistics Canada |
| **Table** | 98-10-0641-01 |
| **Title** | Highest level of education by visible minority, selected sociodemographic characteristics and census year |
| **Release date** | 2024-03-26 |
| **Census years** | 2006, 2011, 2016, 2021 |
| **Universe** | Persons in private households — Canada (national level, 25% sample) |
| **DOI** | https://doi.org/10.25318/9810064101-eng |

**Visible minority groups covered:** South Asian, Chinese, Black, Filipino, Arab, Latin American, Southeast Asian, West Asian, Korean, Japanese, Visible minority n.i.e., Multiple visible minorities, Not a visible minority

---

## Notebook Outline

| Section | Description |
|---|---|
| 1. Import Libraries | pandas, numpy, matplotlib, seaborn, scipy |
| 2. Load & Inspect | Load & concatenate 4 CSV files (2006–2021), preview structure |
| 3. Clean & Preprocess | Rename columns, filter to national totals, remove aggregates, build pivot table |
| 4. Education Distribution | Stacked bar chart: education levels across all groups |
| 5. Bachelor's Degree Ranking | Rank groups by attainment; compute percentage-point gap vs. national average |
| 6. No Credential Analysis | Identify groups with highest no-credential rates using z-scores |
| 7. VM vs. Non-VM Comparison | Side-by-side comparison of visible vs. non-visible minority outcomes |
| 8. Multi-Year Trends | Line chart showing bachelor's+ attainment trends across census years |
| 9. Statistical Testing | Chi-square test + Pearson correlation heatmap |
| 10. Interactive Visualization | Shiny app in `src/` folder for interactive exploration |

---

## Key Findings (2006–2021 with 2021 highlights)

- **Koreans** have the highest bachelor's+ attainment at **50.4%** — 23.7 percentage points above the national average
- **West Asians (45.2%)** and **South Asians (44.2%)** also significantly outperform the national average
- **Southeast Asians** have the highest no-credential rate at **25.1%**, more than double the Filipino rate of 8.6%
- The **total visible minority population (38.4%)** has a substantially higher bachelor's+ rate than the **non-visible minority population (22.6%)**
- **Black** and **visible minority n.i.e.** groups cluster near or below the national average across both metrics

---

## How to Run

**Requirements:** Python 3.9+

```bash
# 1. Clone the repo
git clone git@github.com:Jenniferonyebuchi/migrant-education-analysis.git
cd migrant-education-analysis

# 2. Install dependencies (choose one):

# Option A: pip
pip install -r requirements.txt

# Option B: conda
conda env create -f environment.yml
conda activate migrant-education

# 3. Open the notebook
jupyter lab migrant_education_analysis.ipynb
```

Run all cells top-to-bottom. The notebook loads all 4 CSV files from `data/` and runs the full 2006–2021 analysis including trend charts in Section 8.

---