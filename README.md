# tell-me-the-rules

## AI disclaimer
This project is using Gemimi CLI *a lot*. So don't trust anything you see.

## Board Game Rules Guru

This project is a "Board Game Rules Guru" designed to help users quickly find answers within board game rulebooks. It leverages a local AI model to provide answers based on uploaded PDF rulebooks.

### Features:
- **PDF Upload:** Upload board game rulebooks in PDF format.
- **Intelligent Q&A:** Ask natural language questions about the rules, and get answers extracted from the uploaded documents.
- **Local AI Inference:** Utilizes [Ollama](https://ollama.com/) to run open-source large language models (LLMs) locally, ensuring privacy and offline capability.
- **Vector Database:** Employs [ChromaDB](https://www.trychroma.com/) as a vector store to efficiently retrieve relevant sections of rulebooks for accurate answers.
- **Containerized Environment:** All components (frontend, backend, ChromaDB, Ollama) are set up to run seamlessly using Docker and Docker Compose.

### Architecture:
- **Frontend:** A simple web interface for uploading PDFs and asking questions.
- **Backend (FastAPI):** Handles PDF processing, interacts with ChromaDB for document storage and retrieval, and communicates with the Ollama service for AI inference.
- **ChromaDB:** Stores and indexes the text content of the rulebooks as vector embeddings.
- **Ollama:** Runs the chosen LLM (e.g., `phi3:mini`, `tinyllama`) to generate answers based on the context provided by ChromaDB.

### Setup and Running:
(Instructions for setting up and running the project will go here, including `docker-compose up --build` and model pulling instructions.)