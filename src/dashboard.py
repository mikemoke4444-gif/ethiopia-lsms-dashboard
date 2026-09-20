"""
Ethiopia LSMS Wave 4 — Household Cover Dashboard
Run as an app:      streamlit run src/dashboard.py
Run as diagnostics: python src/dashboard.py
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# PATHS
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR     = PROJECT_ROOT / "data"
OUTPUT_DIR   = PROJECT_ROOT / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

REGION_MAP = {
    1: "Tigray", 2: "Afar", 3: "Amhara", 4: "Oromia",
    5: "Somali", 6: "Benishangul-Gumuz", 7: "SNNP",
    12: "Gambela", 13: "Harari", 14: "Addis Ababa", 15: "Dire Dawa",
}


def load_clean() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "sect_cover_hh_w4.csv",
                     dtype={"household_id": str})

    conf_cols = ["saq11", "saq12", "saq17", "saq18", "saq21"]
    df = df.drop(columns=[c for c in conf_cols if c in df.columns])

    df["InterviewStart"] = pd.to_datetime(df["InterviewStart"], errors="coerce")

    df["region_name"]            = df["saq01"].map(REGION_MAP)
    df["residence"]              = df["saq14"].map({1: "Rural", 2: "Urban"})
    df["hh_size"]                = df["saq09"]
    df["completed_postplanting"] = df["saq13"].map({1: "Yes", 2: "No"})
    df["city_code"]              = df["saq04"]

    df["interview_date"]  = df["InterviewStart"].dt.date
    df["interview_month"] = df["InterviewStart"].dt.to_period("M").astype(str)
    df["is_valid_date"]   = df["InterviewStart"].dt.year == 2019

    return df


# ===========================================================================
# MODE 1 — plain python: diagnostics
# ===========================================================================
def run_diagnostics():
    df = load_clean()
    print("Loaded:", df.shape)
    print("\n=== hh_size describe ===")
    print(df["hh_size"].describe())
    print("\n=== residence ===")
    print(df["residence"].value_counts())
    print("\n=== region_name ===")
    print(df["region_name"].value_counts())
    print("\nSaved:", OUTPUT_DIR / "sect_cover_hh_w4_clean.csv")
    df.to_csv(OUTPUT_DIR / "sect_cover_hh_w4_clean.csv", index=False)


# ===========================================================================
# MODE 2 — streamlit: dashboard
# ===========================================================================
def run_dashboard():
    import streamlit as st
    import plotly.express as px

    st.set_page_config(
        page_title="Ethiopia LSMS W4 — Household Cover",
        page_icon="🏠",
        layout="wide",
    )

    @st.cache_data(show_spinner="Loading household cover data…")
    def _cached():
        return load_clean()

    df = _cached()

    # ---------------- sidebar filters -------------------------------------
    st.sidebar.title("🔎 Filters")

    regions = sorted(df["region_name"].dropna().unique())
    sel_regions = st.sidebar.multiselect("Region", regions, default=regions)

    residences = sorted(df["residence"].dropna().unique())
    sel_res = st.sidebar.multiselect("Residence", residences, default=residences)

    post = sorted(df["completed_postplanting"].dropna().unique())
    sel_post = st.sidebar.multiselect("Completed post-planting", post, default=post)

    hh_min = int(df["hh_size"].min())
    hh_max = int(df["hh_size"].max())
    sel_hh = st.sidebar.slider("Household size range",
                               hh_min, hh_max, (hh_min, hh_max))

    valid_only = st.sidebar.checkbox("Use only valid 2019 interview dates",
                                     value=True)

    # ---------------- apply filters ---------------------------------------
    mask = (
        df["region_name"].isin(sel_regions)
        & df["residence"].isin(sel_res)
        & df["completed_postplanting"].isin(sel_post)
        & df["hh_size"].between(sel_hh[0], sel_hh[1])
    )
    if valid_only:
        mask &= df["is_valid_date"]

    fdf = df[mask].copy()

    # ---------------- header + KPIs ---------------------------------------
    st.title("🏠 Ethiopia LSMS Wave 4 — Household Cover Dashboard")
    st.caption(f"Filtered households: **{len(fdf):,}** of {len(df):,}")

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Households", f"{len(fdf):,}")
    c2.metric("Mean HH size",
              f"{fdf['hh_size'].mean():.2f}" if len(fdf) else "—")
    c3.metric("Median HH size",
              f"{fdf['hh_size'].median():.0f}" if len(fdf) else "—")
    c4.metric("Urban share",
              f"{(fdf['residence'] == 'Urban').mean() * 100:.1f}%"
              if len(fdf) else "—")
    c5.metric("Post-planting done",
              f"{(fdf['completed_postplanting'] == 'Yes').mean() * 100:.1f}%"
              if len(fdf) else "—")

    st.divider()

    # ---------------- row 1: region bar + urban/rural donut --------------
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Households per Region")
        rc = (fdf["region_name"].value_counts()
              .rename_axis("Region").reset_index(name="Households"))
        if not rc.empty:
            fig = px.bar(rc.sort_values("Households"),
                         x="Households", y="Region", orientation="h",
                         color="Households", color_continuous_scale="Blues",
                         text="Households")
            fig.update_traces(textposition="outside")
            fig.update_layout(height=420, coloraxis_showscale=False,
                              margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data for current filters.")

    with col2:
        st.subheader("Urban vs Rural")
        if len(fdf):
            rc2 = fdf["residence"].value_counts().reset_index()
            rc2.columns = ["Residence", "Count"]
            fig = px.pie(rc2, names="Residence", values="Count", hole=0.45,
                         color="Residence",
                         color_discrete_map={"Urban": "#4C72B0",
                                             "Rural": "#55A868"})
            fig.update_layout(height=420,
                              margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data.")

    st.divider()

    # ---------------- row 2: hh size dist + boxplot by region -----------
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Household Size Distribution")
        if len(fdf):
            fig = px.histogram(fdf, x="hh_size", nbins=19,
                               color="residence", barmode="overlay",
                               color_discrete_sequence=px.colors.qualitative.Set2)
            fig.update_layout(height=400, xaxis_title="Household size",
                              yaxis_title="Households",
                              margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data.")

    with col2:
        st.subheader("Household Size by Region")
        if len(fdf):
            fig = px.box(fdf, x="region_name", y="hh_size",
                         color="region_name", points=False)
            fig.update_layout(height=400, showlegend=False,
                              xaxis_title="", yaxis_title="Household size",
                              margin=dict(l=10, r=10, t=10, b=10))
            fig.update_xaxes(tickangle=-40)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data.")

    st.divider()

    # ---------------- row 3: violin + interviews over time --------------
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Urban vs Rural — Household Size")
        if len(fdf):
            fig = px.violin(fdf, x="residence", y="hh_size",
                            box=True, points="outliers", color="residence",
                            color_discrete_sequence=px.colors.qualitative.Set2)
            fig.update_layout(height=400, showlegend=False,
                              xaxis_title="", yaxis_title="Household size",
                              margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data.")

    with col2:
        st.subheader("Interviews Over Time")
        if len(fdf) and fdf["InterviewStart"].notna().any():
            daily = (fdf.dropna(subset=["InterviewStart"])
                        .set_index("InterviewStart")
                        .resample("D").size()
                        .reset_index(name="Interviews"))
            fig = px.line(daily, x="InterviewStart", y="Interviews",
                          markers=True)
            fig.update_layout(height=400, xaxis_title="",
                              yaxis_title="Interviews",
                              margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No interview dates available.")

    st.divider()

    # ---------------- row 4: weighted household size --------------------
    st.subheader("Weighted Household Size (using pw_w4)")
    if len(fdf) and fdf["pw_w4"].notna().any() and fdf["pw_w4"].sum() > 0:
        weighted_mean = np.average(fdf["hh_size"], weights=fdf["pw_w4"])
        col1, col2, col3 = st.columns(3)
        col1.metric("Weighted mean HH size", f"{weighted_mean:.2f}")
        col2.metric("Unweighted mean", f"{fdf['hh_size'].mean():.2f}")
        col3.metric("Weight sum", f"{fdf['pw_w4'].sum():,.0f}")
    else:
        st.info("Weights not available for the current selection.")

    st.divider()

    # ---------------- row 5: data explorer + download ------------------
    with st.expander("🔍 Explore filtered data"):
        st.dataframe(fdf.head(500), use_container_width=True, height=350)
        st.download_button(
            "⬇️ Download filtered CSV",
            data=fdf.to_csv(index=False).encode("utf-8"),
            file_name="sect_cover_hh_w4_filtered.csv",
            mime="text/csv",
        )

    st.caption("Source: Ethiopia LSMS-ISA Wave 4 — sect_cover_hh_w4.csv")


# ===========================================================================
# DISPATCHER
# ===========================================================================
def _running_under_streamlit() -> bool:
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        return get_script_run_ctx() is not None
    except Exception:
        return False


if _running_under_streamlit():
    run_dashboard()
else:
    run_diagnostics()