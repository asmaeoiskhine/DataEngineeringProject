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

CREATE INDEX IF NOT EXISTS idx_characters_name ON characters (name);
CREATE INDEX IF NOT EXISTS idx_characters_anime ON characters (anime);
CREATE INDEX IF NOT EXISTS idx_characters_fandom ON characters (fandom);
