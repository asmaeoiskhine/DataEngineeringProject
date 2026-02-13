import os
import pandas as pd
import streamlit as st
import requests
from PIL import Image
from io import BytesIO
from sqlalchemy import create_engine, text

st.title("Quiz personnalité")

DB_URL = os.environ.get("DATABASE_URL")
if not DB_URL:
    st.error("DATABASE_URL manquante. Lance via docker-compose.")
    st.stop()

engine = create_engine(DB_URL)

@st.cache_data(ttl=10)
def load_df():
    with engine.connect() as conn:

        return pd.read_sql(
            text("SELECT * FROM characters ORDER BY id DESC"),
            conn
        )

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

df = load_df()

st.write("Réponds aux questions pour découvrir quel personnage tu es ;)")

scores = {
    "calme": 0,
    "energique": 0,
    "strategique": 0,
    "protecteur": 0,
    "leader": 0,
}

# --- Questions ---
q1 = st.radio(
    "1. En groupe, tu es plutôt…",
    [
        "Observateur et discret",
        "Meneur naturel",
        "Celui qui motive tout le monde",
        "Celui qui analyse la situation",
    ],
)
if q1 == "Observateur et discret":
    scores["calme"] += 2
elif q1 == "Meneur naturel":
    scores["leader"] += 2
elif q1 == "Celui qui motive tout le monde":
    scores["energique"] += 2
elif q1 == "Celui qui analyse la situation":
    scores["strategique"] += 2

q2 = st.radio(
    "2. Face à un problème, tu préfères…",
    [
        "Réfléchir seul",
        "Agir immédiatement",
        "Protéger les autres",
        "Trouver la meilleure stratégie",
    ],
)
if q2 == "Réfléchir seul":
    scores["calme"] += 1
    scores["strategique"] += 1
elif q2 == "Agir immédiatement":
    scores["energique"] += 2
elif q2 == "Protéger les autres":
    scores["protecteur"] += 2
elif q2 == "Trouver la meilleure stratégie":
    scores["strategique"] += 2

q3 = st.radio(
    "3. Ton plus grand atout est…",
    [
        "Ton sang-froid",
        "Ton intelligence",
        "Ta loyauté",
        "Ton charisme",
    ],
)
if q3 == "Ton sang-froid":
    scores["calme"] += 2
elif q3 == "Ton intelligence":
    scores["strategique"] += 2
elif q3 == "Ta loyauté":
    scores["protecteur"] += 2
elif q3 == "Ton charisme":
    scores["leader"] += 2

q4 = st.radio(
    "4. Dans une équipe, ton rôle est plutôt…",
    [
        "Support discret",
        "Chef d’équipe",
        "Bouclier du groupe",
        "Cerveau de l’équipe",
    ],
)
if q4 == "Support discret":
    scores["calme"] += 1
elif q4 == "Chef d’équipe":
    scores["leader"] += 2
elif q4 == "Bouclier du groupe":
    scores["protecteur"] += 2
elif q4 == "Cerveau de l’équipe":
    scores["strategique"] += 2

q5 = st.radio(
    "5. Tu te décrirais plutôt comme…",
    [
        "Posé et réfléchi",
        "Passionné et intense",
        "Responsable et fiable",
        "Ambitieux et déterminé",
    ],
)
if q5 == "Posé et réfléchi":
    scores["calme"] += 2
elif q5 == "Passionné et intense":
    scores["energique"] += 2
elif q5 == "Responsable et fiable":
    scores["protecteur"] += 2
elif q5 == "Ambitieux et déterminé":
    scores["leader"] += 2

# --- Affichage du résultat ---
if st.button("Découvrir mon personnage"):
    sorted_axes = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top_axes = tuple([sorted_axes[0][0], sorted_axes[1][0]])

    profil_to_character = {
        ("calme", "strategique"): "Johan Liebert",
        ("calme", "protecteur"): "Yasushi Takagi",
        ("calme", "leader"): "Manjiro Sano",
        ("energique", "leader"): "Vegeta",
        ("energique", "protecteur"): "Yato",
        ("energique", "strategique"): "Senku Ishigami",
        ("leader", "protecteur"): "Misaki Ayuzawa",
        ("leader", "strategique"): "Askeladd",
        ("strategique", "protecteur"): "Ayane Yano",
        ("calme", "energique"): "Gintoki Sakata",
        ("protecteur", "calme"): "Kyo Sohma",
        ("leader", "calme"): "Daichi Sawamura",
        ("strategique", "energique"): "Shinichi Kudo",
        ("protecteur", "energique"): "Korosensei",
        ("leader", "energique"): "Momo Ayase",
    }
    fallback_by_axis = {
        "calme": "Johan Liebert",
        "energique": "Vegeta",
        "strategique": "Senku Ishigami",
        "protecteur": "Korosensei",
        "leader": "Manjiro Sano",
    }

    character_name = profil_to_character.get(top_axes)
    if character_name is None:
        character_name = fallback_by_axis.get(top_axes[0])

    row = df[df["name"] == character_name]
    r = row.iloc[0]

    st.success(f"Tu es : {r['name']}")

    img = fetch_image(r.get("image_url", ""))
    if img is not None:
        st.image(img, use_column_width=True)

    st.write("Anime :", r.get("anime"))
    st.markdown(f"[Voir la page Fandom]({r.get('character_url')})")
