import os
import glob
import json
import requests
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
from hashlib import md5

load_dotenv()

JINA_API_KEY = os.getenv("JINA_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

API_URL = "https://api.jina.ai/v1/embeddings"

def jina_embed(texts, batch_size=32):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {JINA_API_KEY}"
    }
    embeddings = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        data = {
            "model": "jina-clip-v2",
            "input": [{"text": t} for t in batch]
        }
        print(f"Sending batch {i} to {i+len(batch)} for embedding...")
        response = requests.post(API_URL, headers=headers, data=json.dumps(data))
        if response.status_code != 200:
            raise Exception(f"Jina API error: {response.status_code} {response.text}")    
        json_response = response.json()
        batch_embeddings = [item["embedding"] for item in json_response.get("data", [])]
        if not batch_embeddings:
            print(f"Warning: Empty embeddings returned for batch {i} to {i+len(batch)}")
        embeddings.extend(batch_embeddings)
    print(f"Total embeddings received: {len(embeddings)}")
    return embeddings

def main():
    qdrant = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY, timeout=60)

    passages = []
    for path in glob.glob("bbc_articles_txt/*.txt"):
        text = open(path, encoding="utf-8").read()
        step = 250
        chunk_size = 500
        for i in range(0, max(len(text) - chunk_size + 1, 1), step):
            chunk_text = text[i:i + chunk_size]
            passages.append({"id": f"{os.path.basename(path)}_{i}", "text": chunk_text})

    print(f"Total passages: {len(passages)}")

    texts = [p["text"] for p in passages]
    vectors = jina_embed(texts)

    points = [
        PointStruct(id=int(md5(p["id"].encode()).hexdigest(),16) % (10**12), vector=v, payload={"text": p["text"],"source_id": p["id"]})
        for p, v in zip(passages, vectors)
    ]

    if not points:
        print("No points to ingest.")
        return

    vector_size = len(points[0].vector)
    if qdrant.collection_exists("news"):
        qdrant.delete_collection("news")

    qdrant.create_collection(
        collection_name="news",
        vectors_config={"size": vector_size, "distance": "Cosine"}
    )

    BATCH_SIZE = 100
    for i in range(0, len(points), BATCH_SIZE):
        batch_points = points[i : i + BATCH_SIZE]
        qdrant.upsert(collection_name="news", points=batch_points)
        print(f"Upserted points {i} to {i+len(batch_points)}")

    print(f"Ingested {len(points)} passages into Qdrant collection 'news'.")

if __name__ == "__main__":
    main()
