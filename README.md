
# Chatbot Backend

This repository contains the backend service for the Retrieval-Augmented Generation (RAG) powered chatbot. It provides the API to ingest news articles, generate embeddings, store and retrieve vectors from a vector database, manage chat sessions with Redis caching, and generate answers using Google Gemini API.

---

## Features

- News article ingestion and chunking into passages
- Embedding generation using Jina Embeddings API
- Vector storage and similarity search with Qdrant
- Session-based chat history stored in Redis
- REST API built with FastAPI (or Express if Node.js)
- Integration with Google Gemini API for final answer generation
- Session management with reset and history retrieval endpoints

---

## Tech Stack

- Python 3.9+ (FastAPI)
- Jina Embeddings API
- Qdrant vector database
- Redis for caching chat session history
- Google Gemini API for LLM-powered responses
- Docker (optional, for containerized deployment)

---

## Getting Started

### Prerequisites

- Python 3.9 or newer
- Redis server running locally or remotely
- Qdrant vector database instance running
- Google Gemini API key
- Jina API key

### Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/whadadogdoin/chatbot_backend.git
    cd chatbot_backend
    ```

2. Create and activate a virtual environment:

    ```bash
    python -m venv venv
    source venv/bin/activate   # Linux/Mac
    venv\\Scripts\\activate    # Windows
    ```

3. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

4. Set environment variables

    Create a `.env` file in the root directory with the following:

    ```bash
    JINA_API_KEY=your_jina_api_key
    QDRANT_URL=http://localhost:6333
    QDRANT_API_KEY=your_qdrant_api_key_if_any
    REDIS_URL=redis://localhost:6379
    GOOGLE_GEMINI_API_KEY=your_google_gemini_api_key
    ```

5. Ingest news articles (example assumes you have articles in `/articles` folder):

    ```bash
    python ingest.py
    ```

6. Start the FastAPI server:

    ```bash
    uvicorn main:app --reload
    ```

The API will be available at [http://localhost:8000](http://localhost:8000)

---

## API Endpoints

- `POST /chat`  
  Send a user query and get a bot response. Requires a session ID to maintain conversation context.

- `GET /history/{session_id}`  
  Retrieve the chat history for a given session.

- `POST /reset/{session_id}`  
  Reset the chat session, clearing history.

---

## Architecture Overview

1. **Ingestion:**  
   News articles are chunked and embedded using Jina Embeddings, then stored in Qdrant vector database.

2. **Query:**  
   On receiving a user query, the backend retrieves the top-k relevant passages from Qdrant using vector similarity search.

3. **Answer Generation:**  
   Retrieved passages are passed to Google Gemini LLM API to generate a final natural language response.

4. **Session Management:**  
   Chat histories are cached in Redis for fast retrieval and session persistence.

---

## Folder Structure

\`\`\`
/articles       # News articles to ingest
/app
  /api          # API route handlers
  /core         # Core logic for embeddings, search, and chat management
  /models       # Pydantic models and schemas
  main.py       # FastAPI app entrypoint
ingest.py       # Script to ingest and index news articles
requirements.txt
.env            # Environment variables (not committed)
\`\`\`

---

## Future Improvements

- Add streaming responses for better UX
- Support WebSocket for real-time chat
- Implement authentication and user management
- Add support for multiple vector databases (Pinecone, Chroma)
- Enhance error handling and logging

---

## License

MIT License
EOF
