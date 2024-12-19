# README.md
# RAG Boilerplate Project

## How to Run
1. Create a .env file with your API keys.
2. Run Docker Compose to start services.
```bash
docker-compose up --build
```
3. Access the API at `http://localhost:5001`

# Available Routes
- POST /create-new-rag
- POST /ask
- GET /view-rags