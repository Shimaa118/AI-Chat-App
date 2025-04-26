"""
Agent Manager Module

This module provides a class for managing the AI agent, vector store, and related components.
It handles the initialization and management of the Gemini model, vector store, and tools.

The module implements:
- Document processing and storage using FAISS vector store
- Question answering using Gemini model
- Tool usage (calculator) for mathematical queries
- Conversation memory for context-aware responses

"""

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool
from langchain_experimental.utilities import PythonREPL
from langchain.memory import ConversationBufferMemory
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class AgentManager:
    """
    A class to manage the AI agent, vector store, and related components.
    
    This class provides a unified interface for:
    - Document storage and retrieval using FAISS vector store
    - Question answering using Gemini model
    - Tool usage (calculator) for mathematical queries
    - Conversation memory for context-aware responses
    
    Attributes:
        agent (Agent): The initialized LangChain agent for processing queries
        vector_store (FAISS): Vector store for document storage and retrieval
        embeddings (HuggingFaceEmbeddings): Model for text embeddings
    """
    
    def __init__(self):
        """
        Initialize the AgentManager and its components.
        
        This method:
        1. Initializes the vector store with embeddings
        2. Sets up the agent with tools and memory
        3. Configures the Gemini model for question answering
        
        Note:
            Requires GOOGLE_API_KEY to be set in environment variables
        """
        self.agent = None
        self.vector_store = None
        self.embeddings = None
        self._initialize_components()

    def _initialize_components(self):
        """
        Initialize all components needed for the agent.
        
        This method:
        1. Sets up the HuggingFace embeddings model
        2. Creates an empty FAISS vector store
        3. Initializes the agent with tools and memory
        
        The vector store is initialized with an empty text to ensure proper setup.
        """
        # Setup vector store
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        self.vector_store = FAISS.from_texts([""], self.embeddings)

        # Setup agent
        self.agent = self._setup_agent()

    def _setup_agent(self):
        """
        Setup the agent with tools and memory.
        
        This method:
        1. Creates a calculator tool using Python REPL
        2. Gets the Google API key from environment
        3. Initializes the Gemini model
        4. Sets up conversation memory
        5. Creates the agent with all components
        
        Returns:
            Agent: The initialized LangChain agent
 
        """
        # Create a Python REPL tool for calculations
        python_repl = PythonREPL()
        calculator = Tool(
            name="calculator",
            func=python_repl.run,
            description="Useful for when you need to perform mathematical calculations. Input should be a valid Python expression."
        )

        # Get Google API key from environment
        google_api_key = os.getenv("GOOGLE_API_KEY")
        if not google_api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is not set")

        # Initialize LLM
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-001",
            temperature=0,
        )

        # Initialize conversation memory
        memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        
        # Initialize agent with tools
        tools = [calculator]
        agent = initialize_agent(
            tools,
            llm,
            agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
            verbose=True,
            memory=memory
        )

        return agent

    def update_vector_store(self, texts):
        """
        Update the vector store with new texts.
        
        This method replaces the current vector store with a new one containing
        the provided texts. Each text is split into chunks and embedded using
        the HuggingFace embeddings model.
        
        Args:
            texts (list): List of text chunks to add to the vector store

        """
        self.vector_store = FAISS.from_texts(texts, self.embeddings)

    def get_similar_docs(self, query, k=3):
        """
        Get similar documents from the vector store.
        
        Args:
            query (str): The search query
            k (int): Number of similar documents to retrieve (default: 3)
            
        Returns:
            list: List of similar documents
        """
        return self.vector_store.similarity_search(query, k=k)

    def run_agent(self, prompt):
        """
        Run the agent with the given prompt.
        
        Args:
            prompt (str): The prompt to send to the agent
            
        Returns:
            str: The agent's response
        """
        return self.agent.run(prompt)

# Create a global instance
agent_manager = AgentManager() 