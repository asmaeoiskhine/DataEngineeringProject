import os
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text

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

# Sidebar: filtres
st.sidebar.header("Filtres")
animes = sorted([a for a in df["anime"].dropna().unique().tolist() if a.strip() != ""])
fandoms = sorted([f for f in df["fandom"].dropna().unique().tolist() if f.strip() != ""])

anime_sel = st.sidebar.multiselect("Anime", animes)
fandom_sel = st.sidebar.multiselect("Fandom", fandoms)

q = st.sidebar.text_input("Recherche (nom / genre / statut)", "")

df_view = df.copy()
if anime_sel:
    df_view = df_view[df_view["anime"].isin(anime_sel)]
if fandom_sel:
    df_view = df_view[df_view["fandom"].isin(fandom_sel)]
if q.strip():
    ql = q.strip().lower()
    def match_row(row):
        for col in ["name", "gender", "status", "anime", "fandom"]:
            v = row.get(col)
            if isinstance(v, str) and ql in v.lower():
                return True
        return False
    df_view = df_view[df_view.apply(match_row, axis=1)]

# KPI
colA, colB, colC, colD = st.columns(4)
colA.metric("Total", len(df))
colB.metric("Affichés", len(df_view))
colC.metric("Animes", df["anime"].nunique(dropna=True))
colD.metric("Fandoms", df["fandom"].nunique(dropna=True))

st.divider()

left, right = st.columns([2, 1], gap="large")

with left:
    st.subheader("Table (clique les liens)")
    show = df_view[["name", "anime", "fandom", "gender", "status", "character_url", "image_url", "scraped_at"]].copy()

    # rendre URLs cliquables
    def as_link(url):
        if isinstance(url, str) and url.startswith("http"):
            return f"[lien]({url})"
        return ""

    show["character_url"] = show["character_url"].apply(as_link)
    show["image_url"] = show["image_url"].apply(as_link)

    st.dataframe(show, use_container_width=True, height=520)

with right:
    st.subheader("Répartition")
    by_anime = df_view["anime"].fillna("Unknown").value_counts().head(15)
    st.bar_chart(by_anime)

    st.subheader("Galerie (top 12)")
    with_images = df_view[df_view["image_url"].notna() & df_view["image_url"].astype(str).str.startswith("http")].head(12)
    for _, r in with_images.iterrows():
        st.image(r["image_url"], caption=f'{r["name"]} — {r.get("anime","")}', use_column_width=True)
