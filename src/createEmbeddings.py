import json
import os
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

# Good general-purpose, lightweight model (~80MB, fast on CPU)
model = SentenceTransformer('all-MiniLM-L6-v2')

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(data, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

def add_embeddings(data, text_field, batch_size=64):
    texts = [record.get(text_field, "") for record in data]
    embeddings = model.encode(texts, batch_size=batch_size, show_progress_bar=True)
    for record, emb in zip(data, embeddings):
        record["embedding"] = emb.tolist()  # convert numpy array to list for JSON
    return data

if __name__ == "__main__":
    input_path = "/Users/manop/Desktop/Rag-azure-search/rag-poc-azure-search/data/transformed/Datafiniti_output.json"
    output_path = "/Users/manop/Desktop/Rag-azure-search/rag-poc-azure-search/data/embedded/Datafiniti_output_embedded.json"

    data = load_json(input_path)
    data = add_embeddings(data, text_field="reviews.text")
    save_json(data, output_path)

    print(f"Done. Embedded {len(data)} records.")