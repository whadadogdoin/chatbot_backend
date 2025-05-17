import os
from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import SearchParams
from ingest import jina_embed
import google.generativeai as genai
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
genai.list_models()
gemini_model = genai.GenerativeModel("gemini-1.5-flash")

qdrant = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str
    top_k: int = 5

class QueryResponse(BaseModel):
    result: str

@app.get("/")
async def root():
    return {"message": "Hello, I am alive!"}

@app.post("/query", response_model=QueryResponse)
async def query_handler(payload: QueryRequest):
    try:
        query_vector = jina_embed([payload.query])[0]
        results = qdrant.search(
            collection_name="news",
            query_vector=query_vector,
            limit=payload.top_k,
            search_params=SearchParams(hnsw_ef=128),
        )
        for r in results:
            print("Score:", r.score)
            print("Text:", r.payload["text"])
        passages = [hit.payload["text"] for hit in results]
        if not passages:
            return QueryResponse(result="No relevant articles found.")
        context = "\n\n".join(passages)
        prompt = f"Use the following context to answer the question.\n\nContext:\n{context}\n\nQuestion: {payload.query}"
        response = gemini_model.generate_content(prompt)
        answer = response.text.strip()
        return QueryResponse(result=answer)
    except Exception as e:
        return QueryResponse(result=f"Error: {str(e)}")