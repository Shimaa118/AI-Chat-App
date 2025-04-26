# AI Chat App with RAG and Agent Capabilities

A React-based chat application that combines Retrieval-Augmented Generation (RAG) with AI agent capabilities. Users can upload documents, ask questions, and get AI-powered responses that may include tool usage when needed.

## Features

- Document upload and processing (.txt, .pdf)
- RAG-based question answering using Gemini
- AI agent with tool usage (calculator)
- Conversation memory for context-aware responses
- Modern React frontend
- FastAPI backend
- Persistent document storage

## Project Structure

```
ai-chat/
├── backend/           # FastAPI backend
│   ├── agent.py      # Agent and vector store management
│   └── routes.py     # API routes and models
├── frontend/         # React frontend
│   ├── src/
│   │   ├── App.js    # Main React component
│   │   └── index.js  # React entry point
│   └── package.json
├── main.py           # Application entry point
├── requirements.txt  # Python dependencies
├── .env.example      # Example environment variables
└── README.md
```

## Prerequisites

- Python 3.8+
- Node.js 14+
- Google API Key for Gemini
- Anaconda or Miniconda

## Setup Instructions

### Backend Setup

1. Create a conda environment:
```bash
conda create -n ai-chat python=3.8
conda activate ai-chat
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
```
Then edit the `.env` file with your Google API key:
```
GOOGLE_API_KEY=your_google_api_key_here
```

4. Start the backend server:
```bash
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
The backend will be available at http://localhost:8000

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```
The frontend will be available at http://localhost:3000

## Usage Guide

### Document Upload and Question Answering

1. **Upload Documents**:
   - Click the "Upload" button in the interface
   - Select a .txt or .pdf file
   - Wait for the upload confirmation message
   - The document will be processed and stored in the vector store

2. **Ask Questions**:
   - Type your question in the chat input
   - Press Enter or click Send
   - The AI will:
     - Search the uploaded documents for relevant context
     - Use the calculator tool if needed
     - Consider conversation history
     - Provide a comprehensive answer

3. **Example Questions**:
   - "What is the main topic of the document?"
   - "Summarize the key points"
   - "What is 2+2?" (will use calculator)
   - Follow-up questions about previous answers

## Technical Implementation

### RAG (Retrieval-Augmented Generation)

1. **Document Processing**:
   - Documents are split into chunks using RecursiveCharacterTextSplitter
   - Each chunk is embedded using HuggingFace embeddings
   - Chunks are stored in a FAISS vector store

2. **Question Answering**:
   - User question is embedded
   - Similar chunks are retrieved from the vector store
   - Retrieved context is combined with the question
   - Gemini model generates an answer using the context

### Agent Implementation

1. **Tool Usage**:
   - Agent can use a calculator tool for mathematical queries
   - Tool selection is automatic based on the query
   - Results are incorporated into the response

2. **Memory Management**:
   - Conversation history is maintained
   - Context from previous interactions is considered
   - Memory persists during the session

## Testing

1. **Document Upload Test**:
   ```bash
   # Upload a test document
   curl -X POST -F "file=@test.pdf" http://localhost:8000/upload
   ```

2. **Question Answering Test**:
   ```bash
   # Ask a question
   curl -X POST -H "Content-Type: application/json" \
        -d '{"question":"What is the main topic?"}' \
        http://localhost:8000/chat
   ```

3. **Calculator Test**:
   ```bash
   # Test calculator functionality
   curl -X POST -H "Content-Type: application/json" \
        -d '{"question":"What is 144 + 5?"}' \
        http://localhost:8000/chat
   ```

## Troubleshooting

### Common Issues

1. **Backend Connection Error**
   - Ensure the backend server is running on port 8000
   - Check if CORS is properly configured
   - Verify the GOOGLE_API_KEY is set correctly in .env
   - Make sure the conda environment is activated

2. **File Upload Issues**
   - Verify file format (.txt or .pdf)
   - Check file size (should be reasonable)
   - Ensure the server is running and accessible

3. **API Key Issues**
   - Ensure GOOGLE_API_KEY is set in .env file
   - Verify the API key has sufficient credits
   - Check for any rate limiting or quota issues

4. **Memory Issues**
   - Memory is maintained per server session
   - Restarting the server will clear conversation history
   - Document storage persists between restarts

## Contributing

Feel free to submit issues and enhancement requests! 