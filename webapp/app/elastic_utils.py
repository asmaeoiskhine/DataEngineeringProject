# webapp/elastic_utils.py
from elasticsearch import Elasticsearch

# Connexion Elasticsearch
es = Elasticsearch("http://localhost:9200")
index_name = "characters_index"

def check_connection():
    return es.ping()

def search_documents(query: str):
    if not query.strip():
        res = es.search(index=index_name, query={"match_all": {}})
    else:
        res = es.search(index=index_name, query={"match": {"name": query}})
    return res['hits']['hits']
