import os
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text

import requests
from PIL import Image
from io import BytesIO

st.set_page_config(page_title="Anime Characters Dashboard", layout="wide")

DB_URL = os.environ["DATABASE_URL"]
engine = create_engine(DB_URL)

st.title("🧩 Anime Characters — Données scrapées (Fandom)")

@st.cache_data(ttl=10)
def load_df():
    with engine.connect() as conn:
        df = pd.read_sql(text("SELECT * FROM characters ORDER BY scraped_at DESC NULLS LAST, id DESC"), conn)
    return df

df = load_df()

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

# Sidebar: filtres
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

# Colonnes clean (car utilisées plus bas)
def clean_gender(x):
    if not isinstance(x, str) or not x.strip():
        return "Unknown"
    return x.replace("♂", "").replace("♀", "").strip()

def clean_status(x):
    if not isinstance(x, str) or not x.strip():
        return "Unknown"
    return x.strip()

df_view["gender_clean"] = df_view["gender"].apply(clean_gender)
df_view["status_clean"] = df_view["status"].apply(clean_status)

# KPI
colA, colB, colC, colD = st.columns(4)
colA.metric("Total", len(df))
colB.metric("Affichés", len(df_view))
colC.metric("Animes", df["anime"].nunique(dropna=True))

st.divider()

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
    st.subheader("Répartition")
    by_anime = df_view["anime"].fillna("Unknown").value_counts().head(15)
    st.bar_chart(by_anime)


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
        st.caption(f"{r.get('anime','Unknown')} • {r.get('gender_clean','Unknown')} • {r.get('status_clean','Unknown')}")

        url = r.get("character_url", "")
        if isinstance(url, str) and url.startswith("http"):
            st.markdown(f"[Ouvrir la page]({url})")
