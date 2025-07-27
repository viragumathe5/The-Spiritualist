from sentence_transformers import SentenceTransformer, util
from elasticsearch import Elasticsearch


# Setting up the elastic search.
es = Elasticsearch("http://localhost:9200", verify_certs=False)
if not es.ping():
    raise ConnectionError("Elasticsearch not reachable")


# Load MPNet model
ranker_model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")
INDEX_NAME = "spiritualist_dense_docs"



def retrieve(query, top_k=5):
    query_vec = ranker_model.encode(query, normalize_embeddings=True).tolist()

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

    retrieve_result = es.search(index=INDEX_NAME, body=dense_query)

    return [{
        "id": hit["_id"],
        "page_number": hit["_source"]["page_number"],
        "title": hit["_source"]["title"],
        "text": hit["_source"]["text"],
        "score": hit["_score"]
    } for hit in retrieve_result["hits"]["hits"]]


def rerank(query, retrieved_docs, top_k=5):
    query_embedding = ranker_model.encode(query, convert_to_tensor=True)

    reranked_results = []
    for doc in retrieved_docs:
        doc_embedding = ranker_model.encode(doc["text"], convert_to_tensor=True)
        score = util.cos_sim(query_embedding, doc_embedding).item()
        reranked_results.append({
            **doc,
            "score": score
        })

    # Sort by semantic_score
    reranked_results.sort(key=lambda x: x["score"], reverse=True)
    return reranked_results[:top_k]



#create_index()
#index_documents()
    
# Test retrieval'

# query = "Liverpool Conference"

# initial_results = retrieve(query, top_k=20)

# # print(initial_results)


# final_results = rerank(query, initial_results, top_k=20)  # Rerank to top 5

# for i, res in enumerate(final_results, 1):
#     print(res["id"])
#     print(res["page_number"])
#     print(f"{i}. {res['title']} (Semantic Score: {res['score']:.4f})")
#     print(f"   {res['text'][:200]}...")