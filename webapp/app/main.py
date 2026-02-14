import os
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text

import requests
from PIL import Image
from io import BytesIO
import plotly.express as px

import streamlit as st


st.set_page_config(page_title="Dashboard - Personnages d'Animes", layout="wide")

DB_URL = os.environ["DATABASE_URL"]
engine = create_engine(DB_URL)

st.title("Personnages d'Animes — Données scrapées sur Fandom")

# -----------------------------
# Load data
# -----------------------------
@st.cache_data(ttl=10)
def load_df():
    with engine.connect() as conn:
        df = pd.read_sql(text("SELECT * FROM characters ORDER BY id DESC"), conn)
    return df

df = load_df()

# -----------------------------
# Image fetching
# -----------------------------
@st.cache_data(ttl=3600)
def fetch_image(url: str):
    if not isinstance(url, str) or not url.startswith("http"):
        return None
    try:
        r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        return Image.open(BytesIO(r.content))
    except Exception:
        return None

# -----------------------------
# Normalize gender and status
# -----------------------------
def clean_gender(x):
    if not isinstance(x, str) or not x.strip():
        return "Unknown"
    x = x.lower()
    if "female" in x or "♀" in x:
        return "Female"
    elif "male" in x or "♂" in x:
        return "Male"
    else:
        return "Unknown"

def clean_status(x):
    if not isinstance(x, str) or not x.strip():
        return "Unknown"
    x = x.lower()
    if "alive" in x:
        return "Alive"
    elif "deceased" in x:
        return "Deceased"
    else:
        return "Unknown"

df["gender"] = df["gender"].apply(clean_gender)
df["status"] = df["status"].apply(clean_status)

# -----------------------------
# Sidebar filters
# -----------------------------
st.sidebar.header("Filtres")

animes = sorted([a for a in df["anime"].dropna().unique().tolist() if a.strip() != ""])
anime_sel = st.sidebar.multiselect("Anime", animes)
q = st.sidebar.text_input("Recherche (nom / genre / statut)", "")

df_view = df.copy()
if anime_sel:
    df_view = df_view[df_view["anime"].isin(anime_sel)]
if q.strip():
    ql = q.strip().lower()
    def match_row(row):
        for col in ["name", "gender", "status", "anime"]:
            v = row.get(col)
            if isinstance(v, str) and ql in v.lower():
                return True
        return False
    df_view = df_view[df_view.apply(match_row, axis=1)]

# -----------------------------
# KPI
# -----------------------------
colA, colB, colC, colD = st.columns(4)
colA.metric("Total", len(df))
colB.metric("Affichés", len(df_view))
colC.metric("Animes", df["anime"].nunique(dropna=True))

st.divider()

# -----------------------------
# Table + Répartition
# -----------------------------
left, right = st.columns([2, 1], gap="large")

with left:
    st.subheader("Tableau général")
    show = df_view[["name", "anime", "gender", "status", "character_url", "image_url"]].copy()
    st.data_editor(
        show,
        use_container_width=True,
        height=520,
        column_config={
            "character_url": st.column_config.LinkColumn("Page Fandom", display_text="ouvrir"),
            "image_url": st.column_config.LinkColumn("Image", display_text="voir"),
        },
        disabled=True
    )

with right:
    st.subheader("Distribution du nombre de personnages par Anime")
    by_anime = df_view["anime"].fillna("Unknown").value_counts().head(15)
    st.bar_chart(by_anime)

# -----------------------------
# Graphiques Gender et Status
# -----------------------------
col1, col2 = st.columns(2, gap="large")

with col1:
    st.subheader("Distribution des status Alive/Deceased par Anime")

    import altair as alt

    df_status = df_view[df_view["status"].isin(["Alive", "Deceased"])].copy()
    df_status["anime"] = df_status["anime"].fillna("Unknown")

    counts = (
        df_status
        .groupby(["anime", "status"])
        .size()
        .reset_index(name="count")
    )

    top_animes = (
        df_status["anime"]
        .value_counts()
        .head(15)
        .index
    )

    counts = counts[counts["anime"].isin(top_animes)]

    chart = (
        alt.Chart(counts)
        .mark_bar()
        .encode(
            x=alt.X("anime:N", sort="-y", title="Anime"),
            y=alt.Y("count:Q", title="Nombre de personnages"),
            xOffset="status:N",
            color=alt.Color(
                "status:N",
                scale=alt.Scale(
                    domain=["Alive", "Deceased"],
                    range=["steelblue", "red"]
                ),
                title="Status"
            ),
            tooltip=["anime", "status", "count"]
        )
        .properties(height=350)
    )

    st.altair_chart(chart, use_container_width=True)

with col2:
    st.subheader("Ratio Male/Female par Anime")

    import altair as alt

    df_gender = df_view[df_view["gender"].isin(["Male", "Female"])].copy()
    df_gender["anime"] = df_gender["anime"].fillna("Unknown")

    top_animes_gender = df_gender["anime"].value_counts().head(15).index
    df_gender = df_gender[df_gender["anime"].isin(top_animes_gender)]

    counts_gender = (
        df_gender
        .groupby(["anime", "gender"])
        .size()
        .reset_index(name="count")
    )

    totals = (
        counts_gender
        .groupby("anime")["count"]
        .sum()
        .reset_index(name="total")
    )

    counts_gender = counts_gender.merge(totals, on="anime")
    counts_gender["percentage"] = (
        counts_gender["count"] / counts_gender["total"] * 100
    )

    chart_gender = (
        alt.Chart(counts_gender)
        .mark_bar()
        .encode(
            x=alt.X(
                "anime:N",
                sort="-y",
                title="Anime"
            ),
            y=alt.Y(
                "percentage:Q",
                title="Pourcentage (%)",
                scale=alt.Scale(domain=[0, 100])
            ),
            color=alt.Color(
                "gender:N",
                scale=alt.Scale(
                    domain=["Male", "Female"],
                    range=["green", "hotpink"]
                ),
                title="Genre"
            ),
            tooltip=[
                "anime",
                "gender",
                alt.Tooltip("percentage:Q", format=".1f", title="Pourcentage (%)")
            ]
        )
        .properties(height=350)
    )

    st.altair_chart(chart_gender, use_container_width=True)
