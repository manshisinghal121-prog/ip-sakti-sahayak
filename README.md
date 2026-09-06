# IP-SAKTI Sahayak (SIH Project)

A Multilingual, RAG-based (source-cited) AI Assistant for Intellectual Property and Regulatory Guidance in Ayurveda across National & International Regimes.

The current implementation runs locally: FastAPI serves the API, retrieval uses the local vector store, and response generation is handled by the local RAG engine. No Gemini API key or cloud model connection is required.

## Directory Structure
- `backend/`: FastAPI application, RAG pipeline, and citation generation engine.
- `data/`: Raw legal documents, indexed vector stores, and metadata schemas.
- `frontend/`: Next.js / React interactive dashboard.
- `notebooks/`: Experiments for chunking, embeddings, and Indic translation evaluation.

## Quickstart
1. From the project root, install backend dependencies: `python -m pip install -r requirements.txt`
2. Run the backend API from the project root: `python backend/main.py`
3. Open `frontend_wireframe_mockup.html` in a browser after the API is running.

The local API is available at `http://127.0.0.1:8000`. For another device on the same network, use the host computer's Wi-Fi address and port `8000`.

## Simple public deployment

1. Push this project to GitHub.
2. On Render, choose **New Web Service** and select the repository.
3. Render will use `render.yaml`, or enter:
	- Build command: `pip install -r requirements.txt`
	- Start command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
4. Share the Render URL. The website opens at `/`, and API requests use the same public origin.
