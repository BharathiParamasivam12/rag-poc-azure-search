import os
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from sentence_transformers import SentenceTransformer

load_dotenv()

service_name = os.getenv("SERVICE_NAME")
endpoint = f"https://{service_name}.search.windows.net/"
key = os.getenv("SEARCH_ADMIN_KEY")
index_name = os.getenv("SEARCH_INDEX_NAME")

search_client = SearchClient(
    endpoint=endpoint,
    index_name=index_name,
    credential=AzureKeyCredential(key)
)

# Same model used to create the embeddings — must match for vector search to make sense
model = SentenceTransformer('all-MiniLM-L6-v2')


def keyword_search(query_text, top=5):
    """Plain full-text search (no vectors) — good for exact term matches."""
    results = search_client.search(
        search_text=query_text,
        select=["name", "city", "province", "reviews_rating", "reviews_title", "reviews_text"],
        top=top
    )
    return list(results)


def vector_search(query_text, top=5):
    """Pure vector (semantic) search — finds meaning matches, not just keyword overlap."""
    query_embedding = model.encode(query_text).tolist()

    vector_query = VectorizedQuery(
        vector=query_embedding,
        k_nearest_neighbors=top,
        fields="embedding"
    )

    results = search_client.search(
        search_text=None,
        vector_queries=[vector_query],
        select=["name", "city", "province", "reviews_rating", "reviews_title", "reviews_text"],
        top=top
    )
    return list(results)


def hybrid_search(query_text, top=5):
    """Combines keyword + vector search — usually gives the best relevance."""
    query_embedding = model.encode(query_text).tolist()

    vector_query = VectorizedQuery(
        vector=query_embedding,
        k_nearest_neighbors=top,
        fields="embedding"
    )

    results = search_client.search(
        search_text=query_text,
        vector_queries=[vector_query],
        select=["name", "city", "province", "reviews_rating", "reviews_title", "reviews_text"],
        top=top
    )
    return list(results)


def print_results(results):
    for i, r in enumerate(results, 1):
        print(f"\n--- Result {i} (score: {r['@search.score']:.4f}) ---")
        print(f"Hotel: {r.get('name')}")
        print(f"Location: {r.get('city')}, {r.get('province')}")
        print(f"Rating: {r.get('reviews_rating')}")
        print(f"Title: {r.get('reviews_title')}")
        print(f"Review: {r.get('reviews_text')[:200]}...")
     

if __name__ == "__main__":
    query = "walkable"

    print("=== KEYWORD SEARCH ===")
    print_results(keyword_search(query))

    print("\n\n=== VECTOR SEARCH ===")
    print_results(vector_search(query))

    print("\n\n=== HYBRID SEARCH ===")
    print_results(hybrid_search(query))