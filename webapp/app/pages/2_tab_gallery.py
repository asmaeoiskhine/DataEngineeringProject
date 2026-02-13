import os
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text

import requests
from PIL import Image
from io import BytesIO

st.title("Galerie")

DB_URL = os.environ.get("DATABASE_URL")
if not DB_URL:
    st.error("DATABASE_URL manquante. Lance via docker-compose.")
    st.stop()

engine = create_engine(DB_URL)

@st.cache_data(ttl=10)
def load_df():
    with engine.connect() as conn:
        return pd.read_sql(text("SELECT * FROM characters ORDER BY id DESC"), conn)

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

st.subheader("Galerie de portrait")

cols = st.slider("Colonnes", 2, 6, 4)
limit = st.slider("Nombre d'images", 8, 60, 24)

gallery_df = df.copy()
gallery_df = gallery_df[
    gallery_df["image_url"].notna()
    & gallery_df["image_url"].astype(str).str.startswith("http")
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
        url = r.get("character_url", "")
        if isinstance(url, str) and url.startswith("http"):
            st.markdown(f"[page descriptive]({url})")
