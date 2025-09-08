import json
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer

# --- Configuration ---
INDEX_NAME = "spiritualist_dense_docs"
DATA_PATH = "./retrieved_documents.json"
MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"

# --- Connect to Elasticsearch ---
es = Elasticsearch("http://localhost:9200", verify_certs=False)
if not es.ping():
    raise ConnectionError("Elasticsearch not reachable")

# --- Load the embedding model ---
model = SentenceTransformer(MODEL_NAME)

# --- Create index with dense_vector mapping ---
def create_index():
    mapping = {
        "mappings": {
            "properties": {
                "id": {"type": "keyword"},
                "page_number": {"type": "keyword"},
                "title": {"type": "text"},
                "text": {"type": "text"},
                "text_embedding": {
                    "type": "dense_vector",
                    "dims": 768,  # MPNet output size
                    "index": True,
                    "similarity": "cosine"  # important
                }
            }
        }
    }

    if es.indices.exists(index=INDEX_NAME):
        es.indices.delete(index=INDEX_NAME)
    es.indices.create(index=INDEX_NAME, body=mapping)

# --- Index documents with embeddings ---
def index_documents():
    with open(DATA_PATH, "r") as f:
        documents = json.load(f)

    for i, doc in enumerate(documents):
        text = doc["text"]
        embedding = model.encode(text, normalize_embeddings=True).tolist()

        body = {
            "id": doc["id"],
            "page_number": doc["page_number"],
            "title": doc["title"],
            "text": doc["text"],
            "text_embedding": embedding
        }

        es.index(index=INDEX_NAME, id=doc["id"], body=body)

        if i % 100 == 0:
            print(f"Indexed {i}/{len(documents)} documents")

# --- Dense vector retrieval ---
def retrieve(query, top_k=5):
    query_vec = model.encode(query, normalize_embeddings=True).tolist()

    dense_query = {
        "size": top_k,
        "query": {
            "script_score": {
                "query": {"match_all": {}},
                "script": {
                    "source": "cosineSimilarity(params.query_vector, 'text_embedding') + 1.0",
                    "params": {"query_vector": query_vec}
                }
            }
        }
    }

    res = es.search(index=INDEX_NAME, body=dense_query)

    return [{
        "id": hit["_id"],
        "title": hit["_source"]["title"],
        "text": hit["_source"]["text"],
        "score": hit["_score"]
    } for hit in res["hits"]["hits"]]

# # --- Run everything ---
# if __name__ == "__main__":
#     create_index()
#     index_documents()

#     query = "Spiritual photography in London"
#     results = retrieve(query)

#     for i, doc in enumerate(results, 1):
#         print(f"\n{i}. {doc['title']} (Score: {doc['score']:.4f})")
#         print(doc["text"][:200] + "...")
