"""
app.py — Migrant Education in Canada
Shiny for Python interactive dashboard

Run with:
    shiny run shiny_app/app.py --reload
"""

import os
import glob

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from shiny import App, ui, render, reactive, req
from shinywidgets import output_widget, render_widget

#  Data loading & preprocessing

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

df_raw = pd.concat(
    [
        pd.read_csv(f, encoding="utf-8-sig")
        for f in sorted(glob.glob(os.path.join(DATA_DIR, "*.csv")))
    ],
    ignore_index=True,
)

df = df_raw.rename(
    columns={
        "REF_DATE": "year",
        "GEO": "geography",
        "Visible minority (15)": "visible_minority",
        "Highest certificate, diploma or degree (7A)": "education_level",
        "Immigrant and generation status (9)": "immigrant_status",
        "Gender (3a)": "gender",
        "Age (15A)": "age",
        "First official language spoken (5)": "language",
        "VALUE": "pct",
        "Census year (4)": "census_year",
    }
)

df["pct"] = pd.to_numeric(df["pct"], errors="coerce")
df["census_year"] = df["census_year"].astype(str)

# Keep national totals only (match the notebook's analysis filter)
mask = (
    (df["gender"] == "Total - Gender")
    & (df["age"] == "Total - Age")
    & (df["language"] == "Total - First official language spoken")
    & (df["immigrant_status"] == "Total \u2013 Immigrant and generation status")
    & (df["geography"] == "Canada")
)
df_clean = df[mask].copy()

# Remove aggregate rows so charts don't double-count
AGGREGATES = [
    "Total - Visible minority",
    "Total - Highest certificate, diploma or degree",
]
df_analysis = df_clean[
    ~df_clean["visible_minority"].isin(AGGREGATES)
    & ~df_clean["education_level"].str.startswith("Total", na=False)
].copy()


# Static lookup tables

EDU_SHORT = {
    "No certificate, diploma or degree": "No credential",
    "High (secondary) school diploma or equivalency certificate": "High school",
    "Postsecondary certificate or diploma below bachelor level": "Post-sec (below Bach.)",
    "Bachelor\u2019s degree": "Bachelor\u2019s",
    "University certificate, diploma or degree above bachelor level": "Above bachelor",
    "Bachelor\u2019s degree or higher": "Bach. or higher",
}
EDU_ORDER = list(EDU_SHORT.keys())

# Meaningful groups only (exclude meta-aggregates used as reference points)
EXCLUDE_GROUPS = {
    "Total visible minority population",
    "Multiple visible minorities",
    "Visible minority, n.i.e.",
}
ALL_GROUPS = sorted(
    g for g in df_analysis["visible_minority"].unique() if g not in EXCLUDE_GROUPS
)

ALL_YEARS = sorted(df_analysis["census_year"].unique())

# ISO-3 origin-country mapping for the choropleth map
GROUP_ISO: dict[str, list[str]] = {
    "Arab": [
        "EGY", "SAU", "SYR", "LBN", "JOR", "IRQ",
        "MAR", "DZA", "TUN", "LBY", "SDN", "YEM",
        "OMN", "ARE", "KWT", "QAT", "BHR",
    ],
    "Black": [
        "NGA", "ETH", "GHA", "KEN", "TZA", "ZAF",
        "COD", "UGA", "CMR", "CIV", "AGO", "SEN",
        "ZMB", "ZWE", "JAM", "HTI", "TTO",
    ],
    "Chinese": ["CHN", "TWN", "HKG"],
    "Filipino": ["PHL"],
    "Japanese": ["JPN"],
    "Korean": ["KOR"],
    "Latin American": [
        "MEX", "COL", "ARG", "PER", "VEN", "CHL",
        "ECU", "BOL", "GTM", "CUB", "DOM", "HND",
        "SLV", "BRA", "URY", "PRY",
    ],
    "South Asian": ["IND", "PAK", "BGD", "LKA", "NPL"],
    "Southeast Asian": ["VNM", "THA", "IDN", "MYS", "MMR", "KHM", "SGP"],
    "West Asian": ["IRN", "TUR", "AFG", "ARM", "AZE", "GEO"],
    "Not a visible minority": ["CAN"],
}


