"""
FastAPI Routes Module

This module defines the API routes and request/response models for the application.
It handles file uploads, chat interactions, and test endpoints.

Classes:
    ChatRequest: Model for chat request payload
    ChatResponse: Model for chat response payload

Routes:
    /upload: Endpoint for file uploads
    /chat: Endpoint for chat interactions
    /test: Endpoint for testing connection
"""

from fastapi import APIRouter, FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import tempfile
import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from backend.agent import agent_manager

# Initialize router
router = APIRouter()

class ChatRequest(BaseModel):
    """
    Model for chat request payload.
    
    Attributes:
        question (str): The user's question
    """
    question: str

class ChatResponse(BaseModel):
    """
    Model for chat response payload.
    
    Attributes:
        answer (str): The agent's answer
        reasoning (Optional[str]): The agent's reasoning process
    """
    answer: str
    reasoning: Optional[str] = None

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload and process a file.
    
    This endpoint:
    1. Validates file type (.txt or .pdf)
    2. Reads file content
    3. Splits text into chunks
    4. Updates vector store with new content
    
    Args:
        file (UploadFile): The file to upload
        
    Returns:
        dict: Success message
        
    Raises:
        HTTPException: If file type is invalid or processing fails
    """
    if not file.filename.endswith(('.txt', '.pdf')):
        raise HTTPException(status_code=400, detail="File must be .txt or .pdf")
    
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        content = await file.read()
        temp_file.write(content)
        temp_file_path = temp_file.name

    try:
        if file.filename.endswith('.txt'):
            with open(temp_file_path, 'r', encoding='utf-8') as f:
                text = f.read()
        else:
            from pypdf import PdfReader
            reader = PdfReader(temp_file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text()

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        chunks = text_splitter.split_text(text)
        agent_manager.update_vector_store(chunks)
        return {"message": "File processed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        os.unlink(temp_file_path)


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process a chat request.
    
    This endpoint:
    1. Retrieves relevant context from vector store
    2. Constructs a prompt with context and question
    3. Gets response from agent
    4. Returns formatted response
    
    Args:
        request (ChatRequest): The chat request
        
    Returns:
        ChatResponse: The agent's response
        
    Raises:
        HTTPException: If processing fails
    """
    try:
        docs = agent_manager.get_similar_docs(request.question)
        context = "\n".join([doc.page_content for doc in docs])
        
        prompt = f"""You are a helpful AI assistant.

Context from documents (if available):
{context}

User Question: {request.question}

Instructions:
- First, try to answer the question based on the provided context.
- If the context does not contain the necessary information, rely on your general knowledge to answer.
- If the question requires calculations, use the calculator tool.
- Consider the conversation history when formulating your response.

Provide a clear, helpful, and accurate answer."""

        response = agent_manager.run_agent(prompt)
        return ChatResponse(
            answer=response,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/test")
async def test_connection():
    """
    Test the backend connection.
    
    Returns:
        dict: Success message
    """
    return {"message": "Backend is working!"}

def create_app():
    """
    Create and configure the FastAPI application.
    
    This function:
    1. Creates a FastAPI app
    2. Configures CORS
    3. Includes routes
    
    Returns:
        FastAPI: The configured application
    """
    app = FastAPI()
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"]
    )
    
    # Include routes
    app.include_router(router)
    
    return app 