FROM python:3.11-slim

WORKDIR /project

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# requirements à la racine webapp/
COPY webapp/requirements.txt /project/requirements.txt
RUN pip install --no-cache-dir -r /project/requirements.txt

# copie du code webapp + scrapy (car on lance Scrapy depuis le container)
COPY webapp /project/webapp
COPY scrapy /project/scrapy

EXPOSE 8501

# Lance crawl+import puis démarre la webapp (adapte la commande de run si Flask/Dash)
CMD ["bash", "-lc", "python /project/webapp/app/import_characters.py && streamlit run /project/webapp/app/main.py --server.address=0.0.0.0 --server.port=8501"]
