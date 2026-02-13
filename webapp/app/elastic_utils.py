from elasticsearch import Elasticsearch
import os

ELASTIC_HOST = os.environ.get("ELASTIC_HOST", "elasticsearch")
ELASTIC_USER = os.environ.get("ELASTIC_USER", "elastic")
ELASTIC_PASSWORD = os.environ.get("ELASTIC_PASSWORD", "")

# Connexion Elasticsearch
es = Elasticsearch(
    f"http://{ELASTIC_HOST}:9200",
    basic_auth=(ELASTIC_USER, ELASTIC_PASSWORD)
)

index_name = "characters_index"

def check_connection():
    return es.ping()

def search_documents(query: str):
    if not query.strip():
        res = es.search(index=index_name, query={"match_all": {}})
    else:
        res = es.search(index=index_name, query={"match": {"name": query}})
    return res['hits']['hits']
