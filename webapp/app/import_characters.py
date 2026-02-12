import json
import os
import subprocess
from pathlib import Path
from datetime import datetime
from sqlalchemy import create_engine, text

# =====================
# CONFIG
# =====================
DB_URL = os.environ["DATABASE_URL"]

PROJECT_ROOT = Path(__file__).resolve().parents[2]  # -> .../webapp
PROJECT_ROOT = PROJECT_ROOT.parent                  # -> racine du repo

SCRAPY_DIR = Path(os.environ.get("SCRAPY_DIR", PROJECT_ROOT / "scrapy" / "crawler")).resolve()
JSON_PATH = Path(os.environ.get("JSON_PATH", SCRAPY_DIR / "characters.json")).resolve()

SPIDER_NAME = os.environ.get("SPIDER_NAME", "characters")
RUN_SCRAPY_ON_START = os.environ.get("RUN_SCRAPY_ON_START", "1") == "1"


# =====================
# UTILS
# =====================
def parse_dt(s):
    if not s:
        return None
    try:
        return datetime.fromisoformat(s)
    except Exception:
        return None


# =====================
# SCRAPY
# =====================
def run_scrapy():
    print(f"[SCRAPY] cwd = {SCRAPY_DIR}")
    subprocess.run(
        ["scrapy", "crawl", SPIDER_NAME, "-O", str(JSON_PATH.name)],
        cwd=str(SCRAPY_DIR),
        check=True,
    )
    print("[SCRAPY] Terminé.")



# =====================
# DB
# =====================
def init_db(engine):
    with engine.begin() as conn:
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS characters (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            anime TEXT,
            fandom TEXT,
            character_url TEXT UNIQUE,
            gender TEXT,
            status TEXT,
            image_url TEXT,
            scraped_at TIMESTAMP
        );
        """))


def import_json(engine):
    if not os.path.exists(JSON_PATH):
        print(f"[IMPORT] Fichier introuvable : {JSON_PATH}")
        return

    with open(JSON_PATH, "r", encoding="utf-8") as f:
        items = json.load(f)

    sql = text("""
        INSERT INTO characters (name, anime, fandom, character_url, gender, status, image_url, scraped_at)
        VALUES (:name, :anime, :fandom, :character_url, :gender, :status, :image_url, :scraped_at)
        ON CONFLICT (character_url) DO UPDATE SET
            name = EXCLUDED.name,
            anime = EXCLUDED.anime,
            fandom = EXCLUDED.fandom,
            gender = EXCLUDED.gender,
            status = EXCLUDED.status,
            image_url = EXCLUDED.image_url,
            scraped_at = EXCLUDED.scraped_at
    """)

    count = 0
    with engine.begin() as conn:
        for it in items:
            if not it.get("name") or not it.get("character_url"):
                continue

            conn.execute(sql, {
                "name": it.get("name"),
                "anime": it.get("anime"),
                "fandom": it.get("fandom"),
                "character_url": it.get("character_url"),
                "gender": it.get("gender"),
                "status": it.get("status"),
                "image_url": it.get("image_url"),
                "scraped_at": parse_dt(it.get("scraped_at")),
            })
            count += 1

    print(f"[IMPORT] {count} personnages importés.")


# =====================
# MAIN
# =====================
def main():
    engine = create_engine(DB_URL)

    init_db(engine)

    if RUN_SCRAPY_ON_START:
        run_scrapy()

    import_json(engine)


if __name__ == "__main__":
    main()
