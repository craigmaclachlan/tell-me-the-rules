from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import chromadb
import fitz  # PyMuPDF
import os
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)



# In-memory storage for the ChromaDB client
chroma_client = None
collection = None

def get_chroma_client():
    global chroma_client
    if chroma_client is None:
        host = os.environ.get("CHROMA_HOST", "localhost")
        logger.info(f"Connecting to ChromaDB at {host}:8000")
        chroma_client = chromadb.HttpClient(host=host, port=8000)
    return chroma_client

@app.post("/api/upload")
async def upload_pdf(file: UploadFile = File(...)):
    global collection
    logger.info(f"Received upload request for {file.filename}")
    try:
        client = get_chroma_client()
        collection_name = os.path.splitext(file.filename)[0]
        logger.info(f"Getting or creating ChromaDB collection: {collection_name}")
        collection = client.get_or_create_collection(name=collection_name)

        # Read the PDF content
        pdf_content = await file.read()
        doc = fitz.open(stream=pdf_content, filetype="pdf")

        # Extract text and split into chunks
        text_chunks = []
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text_chunks.append(page.get_text())
        logger.info(f"Extracted {len(text_chunks)} text chunks from PDF")

        # Add text chunks to ChromaDB
        collection.add(
            documents=text_chunks,
            ids=[f"{file.filename}-{i}" for i in range(len(text_chunks))]
        )
        logger.info(f"Added text chunks to ChromaDB for {file.filename}")

        return JSONResponse(content={"message": f"Successfully uploaded and processed {file.filename}"})
    except Exception as e:
        logger.error(f"Error during PDF upload: {e}", exc_info=True)
        return JSONResponse(content={"error": str(e)}, status_code=500)

import requests

def get_ollama_response(prompt):
    ollama_host = os.environ.get("OLLAMA_HOST", "localhost")
    url = f"http://{ollama_host}:11434/api/generate"
    payload = {
        "model": "tinyllama",
        "prompt": prompt
    }
    logger.info(f"Sending request to Ollama: URL={url}, Payload={payload}")
    response = requests.post(url, json=payload)
    response.raise_for_status()  # Raise an exception for bad status codes
    
    # Process the streaming response
    full_response = ""
    for line in response.iter_lines():
        if line:
            json_line = json.loads(line)
            full_response += json_line.get("response", "")
    logger.info(f"Received response from Ollama: {full_response[:200]}...") # Log first 200 chars
    return full_response

@app.post("/api/ask")
async def ask_question(question: str = Form(...)):
    global collection
    logger.info(f"Received question: {question}")
    if collection is None:
        logger.warning("No PDF has been uploaded yet. Returning 400.")
        return JSONResponse(content={"error": "No PDF has been uploaded yet."}, status_code=400)

    try:
        # Query ChromaDB for relevant documents
        logger.info(f"Querying ChromaDB for question: {question}")
        results = collection.query(
            query_texts=[question],
            n_results=5
        )
        logger.info(f"ChromaDB query results: {results}")

        # Create the prompt for the Ollama API
        context = "\n".join(results['documents'][0])
        prompt = f"Based on the following rules, please answer the question.\n\nRules:\n{context}\n\nQuestion: {question}"
        logger.info(f"Generated prompt for Ollama: {prompt[:500]}...") # Log first 500 chars

        # Call the Ollama API
        answer = get_ollama_response(prompt)
        logger.info(f"Final answer from Ollama: {answer[:200]}...") # Log first 200 chars

        return JSONResponse(content={"answer": answer})
    except Exception as e:
        logger.error(f"Error during question answering: {e}", exc_info=True)
        return JSONResponse(content={"error": str(e)}, status_code=500)

