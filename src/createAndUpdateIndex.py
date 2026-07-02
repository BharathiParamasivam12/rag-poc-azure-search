import os
import json
import uuid
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient

load_dotenv()

service_name = os.getenv("SERVICE_NAME")
endpoint = f"https://{service_name}.search.windows.net/"
key = os.getenv("SEARCH_ADMIN_KEY")
index_name = os.getenv("SEARCH_INDEX_NAME")

assert service_name, "SERVICE_NAME not set"
assert key, "SEARCH_ADMIN_KEY not set"
assert index_name, "SEARCH_INDEX_NAME not set"

search_client = SearchClient(
    endpoint=endpoint,
    index_name=index_name,
    credential=AzureKeyCredential(key)
)

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def prepare_documents(data):
    """Map raw JSON records to match the index schema field names."""
    documents = []
    for record in data:
        doc = {
            "id": str(uuid.uuid4()),  # generate a unique key per doc
            "name": record.get("name", ""),
            "city": record.get("city", ""),
            "province": record.get("province", ""),
            "reviews_rating": float(record.get("reviews.rating", 0) or 0),
            "reviews_title": record.get("reviews.title", ""),
            "reviews_text": record.get("reviews.text", ""),
            "embedding": record.get("embedding", [])
        }
        documents.append(doc)
    return documents

def upload_in_batches(documents, batch_size=1000):
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i + batch_size]
        result = search_client.upload_documents(documents=batch)
        succeeded = sum(1 for r in result if r.succeeded)
        print(f"Batch {i // batch_size + 1}: {succeeded}/{len(batch)} succeeded")

if __name__ == "__main__":
    input_path = "/Users/manop/Desktop/Rag-azure-search/rag-poc-azure-search/data/embedded/Datafiniti_output_embedded.json"

    data = load_json(input_path)
    documents = prepare_documents(data)
    upload_in_batches(documents)

    print(f"Done. Uploaded {len(documents)} documents to index '{index_name}'.")