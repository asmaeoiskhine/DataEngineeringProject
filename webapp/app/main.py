import os
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text

import requests
from PIL import Image
from io import BytesIO
import plotly.express as px

import streamlit as st
from elastic_utils import check_connection, search_documents

st.set_page_config(page_title="Anime Characters Dashboard", layout="wide")

DB_URL = os.environ["DATABASE_URL"]
engine = create_engine(DB_URL)

st.title("🧩 Anime Characters — Données scrapées (Fandom)")

# -----------------------------
# Load data
# -----------------------------
@st.cache_data(ttl=10)
def load_df():
    with engine.connect() as conn:
        df = pd.read_sql(text("SELECT * FROM characters ORDER BY scraped_at DESC NULLS LAST, id DESC"), conn)
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
# Sidebar filters + Elasticsearch
# -----------------------------
st.sidebar.header("Filtres")

# Filtrage traditionnel sur dataframe
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

# Recherche Elasticsearch
st.sidebar.subheader("🔍 Recherche avancée Elasticsearch")
if check_connection():
    es_query = st.sidebar.text_input("Chercher un personnage dans Elasticsearch :", "")
    if es_query.strip():
        hits = search_documents(es_query)
        st.sidebar.write(f"{len(hits)} documents trouvés :")
        for hit in hits:
            src = hit["_source"]
            st.sidebar.write(f"**{src.get('name','')}** - {src.get('anime','Unknown')} - {src.get('gender','Unknown')}")
else:
    st.sidebar.warning("Elasticsearch non disponible")


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
    st.subheader("Table (liens cliquables)")
    show = df_view[["name", "anime", "gender", "status", "character_url", "image_url", "scraped_at"]].copy()
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
    #---------------------------
    # Répartition globale
    #---------------------------
    st.subheader("Répartition")
    by_anime = df_view["anime"].fillna("Unknown").value_counts().head(15)
    st.bar_chart(by_anime)

# -----------------------------
# Nouvelle ligne pour les graphiques côte à côte
# -----------------------------
col1, col2 = st.columns(2, gap="large")

with col1:
    st.subheader("Alive vs Deceased par anime")

    import altair as alt

    # Filtrer Alive et Deceased
    df_status = df_view[df_view["status"].isin(["Alive", "Deceased"])].copy()
    df_status["anime"] = df_status["anime"].fillna("Unknown")

    # Comptage par anime et status
    counts = (
        df_status
        .groupby(["anime", "status"])
        .size()
        .reset_index(name="count")
    )

    # Top 15 animes
    top_animes = (
        df_status["anime"]
        .value_counts()
        .head(15)
        .index
    )

    counts = counts[counts["anime"].isin(top_animes)]

    # Graphique Altair (2 barres par anime)
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
    st.subheader("Male vs Female par anime")

    # Filtrer Male et Female
    df_gender = df_view[df_view["gender"].isin(["Male", "Female"])].copy()
    df_gender["anime"] = df_gender["anime"].fillna("Unknown")

    # Comptage par anime + gender
    counts_gender = (
        df_gender
        .groupby(["anime", "gender"])
        .size()
        .reset_index(name="count")
    )

    # Garder les 15 animes les plus représentés
    top_animes_gender = df_gender["anime"].value_counts().head(15).index
    counts_gender = counts_gender[counts_gender["anime"].isin(top_animes_gender)]

    # Graphique Altair avec barres côte à côte
    chart_gender = (
        alt.Chart(counts_gender)
        .mark_bar()
        .encode(
            x=alt.X("anime:N", sort="-y", title="Anime"),
            y=alt.Y("count:Q", title="Nombre de personnages"),
            xOffset="gender:N",
            color=alt.Color(
                "gender:N",
                scale=alt.Scale(
                    domain=["Male", "Female"],
                    range=["green", "hotpink"]  # couleurs personnalisées
                ),
                title="Genre"
            ),
            tooltip=["anime", "gender", "count"]
        )
        .properties(height=350)
    )

    st.altair_chart(chart_gender, use_container_width=True)



# -----------------------------
# Galerie des personnages
# -----------------------------
st.subheader("🖼️ Galerie des personnages")

cols = st.slider("Colonnes", 2, 6, 4)
limit = st.slider("Nombre d'images", 8, 60, 24)

gallery_df = df_view.copy()
gallery_df = gallery_df[
    gallery_df["image_url"].notna() &
    gallery_df["image_url"].astype(str).str.startswith("http")
]
gallery_df = gallery_df.sample(frac=1, random_state=None).head(limit)

grid = st.columns(cols)
for i, (_, r) in enumerate(gallery_df.iterrows()):
    with grid[i % cols]:
        img = fetch_image(r.get("image_url", ""))
        if img is not None:
            st.image(img, use_column_width=True)
        else:
            st.caption("Image indisponible")
        st.markdown(f"**{r.get('name','')}**")
        st.caption(f"{r.get('anime','Unknown')} • {r.get('gender','Unknown')} • {r.get('status','Unknown')}")
        url = r.get("character_url", "")
        if isinstance(url, str) and url.startswith("http"):
            st.markdown(f"[Ouvrir la page]({url})")
