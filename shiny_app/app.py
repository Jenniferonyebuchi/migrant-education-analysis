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

# UI

sidebar = ui.sidebar(
    ui.h6("Filters", class_="fw-bold mb-2"),
    ui.input_checkbox_group(
        "sel_groups",
        "Visible Minority Groups",
        choices={g: g for g in ALL_GROUPS},
        selected=[
            "South Asian", "Chinese", "Black",
            "Filipino", "Korean", "Not a visible minority",
        ],
    ),
    ui.hr(),
    ui.input_checkbox_group(
        "sel_years",
        "Census Years",
        choices={y: y for y in ALL_YEARS},
        selected=ALL_YEARS,
    ),
    ui.hr(),
    ui.input_checkbox_group(
        "sel_edu",
        "Education Levels",
        choices={k: v for k, v in EDU_SHORT.items() if "higher" not in k.lower()},
        selected=[k for k in EDU_SHORT if "higher" not in k.lower()],
    ),
    width=300,
)

app_ui = ui.page_navbar(
    ui.nav_panel(
        "Overview",
        ui.layout_columns(
            ui.value_box(
                "Groups Selected",
                ui.output_text("vbox_groups"),
                showcase=ui.tags.i(class_="fa-solid fa-users"),
                theme="primary",
            ),
            ui.value_box(
                "Top Group — Bach. or higher (2021)",
                ui.output_text("vbox_top"),
                showcase=ui.tags.i(class_="fa-solid fa-graduation-cap"),
                theme="success",
            ),
            ui.value_box(
                "Biggest Gain 2006 \u2192 2021",
                ui.output_text("vbox_gain"),
                showcase=ui.tags.i(class_="fa-solid fa-arrow-trend-up"),
                theme="info",
            ),
            col_widths=[4, 4, 4],
        ),
        ui.card(
            ui.card_header(
                "Education Level Distribution by Visible Minority Group "
                "(most recent selected year)"
            ),
            output_widget("bar_overview"),
            full_screen=True,
        ),
    ),
    ui.nav_panel(
        "Analysis",
        ui.layout_columns(
            ui.card(
                ui.card_header(
                    "Bachelor\u2019s Degree or Higher \u2014 Trend Across Census Years"
                ),
                output_widget("line_trend"),
                full_screen=True,
            ),
            ui.card(
                ui.card_header(
                    "World Origin Regions of Selected Groups \u2014 "
                    "colour = Bach. or higher attainment (2021)"
                ),
                output_widget("world_map"),
                full_screen=True,
            ),
            col_widths=[6, 6],
        ),
        ui.card(
            ui.card_header("Filtered Dataset"),
            ui.output_data_frame("data_table"),
            full_screen=True,
        ),
    ),
    title="Migrant Education in Canada",
    sidebar=sidebar,
    fillable=True,
    header=ui.tags.head(
        ui.tags.link(
            rel="stylesheet",
            href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css",
        )
    ),
)

#  Server

def server(input, output, session):

    # Shared reactive dataset
    @reactive.calc
    def filtered():
        req(input.sel_groups(), input.sel_years(), input.sel_edu())
        return df_analysis[
            df_analysis["visible_minority"].isin(list(input.sel_groups()))
            & df_analysis["census_year"].isin(list(input.sel_years()))
            & df_analysis["education_level"].isin(list(input.sel_edu()))
        ].copy()

    # Value boxes
    @render.text
    def vbox_groups():
        return str(len(input.sel_groups()))

    @render.text
    def vbox_top():
        bach_edu = next(
            (
                e for e in df_clean["education_level"].unique()
                if "bachelor" in e.lower() and "higher" in e.lower()
            ),
            None,
        )
        if not bach_edu:
            return "N/A"
        sub = df_analysis[
            (df_analysis["education_level"] == bach_edu)
            & (df_analysis["census_year"] == "2021")
            & (df_analysis["visible_minority"].isin(list(input.sel_groups())))
        ]
        if sub.empty:
            return "N/A"
        row = sub.loc[sub["pct"].idxmax()]
        return f"{row['visible_minority']}  ({row['pct']:.1f}%)"

    @render.text
    def vbox_gain():
        bach_edu = next(
            (
                e for e in df_clean["education_level"].unique()
                if "bachelor" in e.lower() and "higher" in e.lower()
            ),
            None,
        )
        if not bach_edu:
            return "N/A"
        sub = df_analysis[
            (df_analysis["education_level"] == bach_edu)
            & (df_analysis["census_year"].isin(["2006", "2021"]))
            & (df_analysis["visible_minority"].isin(list(input.sel_groups())))
        ].pivot_table(index="visible_minority", columns="census_year", values="pct")

        if sub.empty or not {"2006", "2021"}.issubset(sub.columns):
            return "N/A"
        sub["gain"] = sub["2021"] - sub["2006"]
        best = sub["gain"].idxmax()
        return f"{best}  (+{sub.loc[best, 'gain']:.1f} pp)"

    # Tab 1: Overview grouped bar chart
    @render_widget
    def bar_overview():
        df_f = filtered()
        if df_f.empty:
            return go.Figure()

        latest = max(input.sel_years())
        df_f = df_f[df_f["census_year"] == latest].copy()
        df_f["edu_short"] = (
            df_f["education_level"].map(EDU_SHORT).fillna(df_f["education_level"])
        )

        present_order = [
            EDU_SHORT[k]
            for k in EDU_ORDER
            if EDU_SHORT.get(k) in df_f["edu_short"].values
        ]

        fig = px.bar(
            df_f,
            x="visible_minority",
            y="pct",
            color="edu_short",
            barmode="group",
            category_orders={"edu_short": present_order},
            labels={
                "visible_minority": "Visible Minority Group",
                "pct": "Percentage (%)",
                "edu_short": "Education Level",
            },
            color_discrete_sequence=px.colors.qualitative.Bold,
            template="plotly_white",
        )
        fig.update_layout(
            xaxis_tickangle=-35,
            legend_title_text="Education Level",
            height=480,
            margin=dict(b=130),
            yaxis_ticksuffix="%",
        )
        return fig

 # Tab 2: Trend line chart
    @render_widget
    def line_trend():
        bach_edu = next(
            (
                e for e in df_clean["education_level"].unique()
                if "bachelor" in e.lower() and "higher" in e.lower()
            ),
            None,
        )
        if not bach_edu:
            return go.Figure()

        df_t = df_clean[
            df_clean["visible_minority"].isin(list(input.sel_groups()))
            & (df_clean["education_level"] == bach_edu)
        ][["census_year", "visible_minority", "pct"]].copy()

        if df_t.empty:
            return go.Figure()

        fig = px.line(
            df_t,
            x="census_year",
            y="pct",
            color="visible_minority",
            markers=True,
            labels={
                "census_year": "Census Year",
                "pct": "% with Bach. or higher",
                "visible_minority": "Group",
            },
            template="plotly_white",
            color_discrete_sequence=px.colors.qualitative.Bold,
        )
        fig.update_layout(
            legend_title_text="Visible Minority Group",
            height=480,
            yaxis_ticksuffix="%",
        )
        return fig

    