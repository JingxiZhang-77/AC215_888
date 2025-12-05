"""
RAG Service for Safety Event Classification

Retrieves relevant policy documents from ChromaDB based on department
and integrates them into the classification prompt.
"""

import os
import chromadb
from typing import List, Dict, Optional
from google import genai
from google.genai import types
from utils.logger import logger
from utils.config import settings


class RAGService:
    """
    Service for retrieving relevant policy context from vector database
    """
    
    def __init__(self):
        """Initialize RAG service with ChromaDB connection"""
        # Get ChromaDB connection details from environment
        self.chromadb_host = os.environ.get("CHROMADB_HOST", "safety-chromadb")
        self.chromadb_port = int(os.environ.get("CHROMADB_PORT", "8000"))
        self.collection_name = "safety-policies-char-split"
        self.embedding_model = "text-embedding-004"
        self.embedding_dimension = 256
        
        # Initialize LLM client for embeddings
        gcp_project = os.environ.get("GCP_PROJECT", "apcomp215-group88")
        gcp_location = os.environ.get("GCP_REGION", "us-central1")
        
        try:
            self.llm_client = genai.Client(
                vertexai=True, 
                project=gcp_project, 
                location=gcp_location
            )
            
            # Test ChromaDB connection on startup
            try:
                test_client = chromadb.HttpClient(
                    host=self.chromadb_host,
                    port=self.chromadb_port
                )
                test_client.heartbeat()
                self.rag_available = True
                logger.info(f"RAG service initialized. ChromaDB connected at {self.chromadb_host}:{self.chromadb_port}")
            except Exception as chroma_error:
                self.rag_available = False
                logger.warning(f"ChromaDB not available at {self.chromadb_host}:{self.chromadb_port}: {chroma_error}")
                logger.warning("RAG service will operate without policy context. Classification will still work.")
                
        except Exception as e:
            self.rag_available = False
            logger.warning(f"RAG service initialization failed: {e}")
        
        # Department mapping
        self.department_mapping = {
            "internal medicine": "internal_medicine",
            "internal_medicine": "internal_medicine",
            "surgery": "surgery",
            "ob/gyn/nicu": "ob_gyn_nicu",
            "ob_gyn_nicu": "ob_gyn_nicu",
            "radiology/imaging": "radiology_imaging",
            "radiology_imaging": "radiology_imaging",
            "outpatient/ER": "outpatient_er",
            "outpatient/er": "outpatient_er",
            "outpatient_er": "outpatient_er",
            "unspecified": "internal_medicine"  # Default fallback
        }
    
    def _normalize_department(self, department: str) -> str:
        """Normalize department name to match vector DB metadata"""
        dept_lower = department.lower().strip()
        return self.department_mapping.get(dept_lower, "internal_medicine")
    
    def _generate_query_embedding(self, query: str) -> List[float]:
        """Generate embedding for query text"""
        try:
            kwargs = {
                "output_dimensionality": self.embedding_dimension
            }
            response = self.llm_client.models.embed_content(
                model=self.embedding_model,
                contents=query,
                config=types.EmbedContentConfig(**kwargs)
            )
            return response.embeddings[0].values
        except Exception as e:
            logger.error(f"Error generating query embedding: {e}")
            return []
    
    def retrieve_policy_context(
        self, 
        incident_description: str, 
        department: str,
        n_results: int = 5
    ) -> Dict[str, any]:
        """
        Retrieve relevant policy documents from vector database
        
        Args:
            incident_description: The safety incident description
            department: The department where incident occurred
            n_results: Number of relevant chunks to retrieve
            
        Returns:
            Dictionary containing retrieved context and metadata
        """
        if not self.rag_available:
            logger.warning("RAG service not available, skipping context retrieval")
            return {
                "context": "",
                "retrieved": False,
                "error": "RAG service not initialized"
            }
        
        try:
            # Normalize department
            normalized_dept = self._normalize_department(department)
            logger.info(f"Retrieving policy context for department: {normalized_dept}")
            
            # Generate query embedding
            query_embedding = self._generate_query_embedding(incident_description)
            
            if not query_embedding:
                return {
                    "context": "",
                    "retrieved": False,
                    "error": "Failed to generate query embedding"
                }
            
            # Connect to ChromaDB
            client = chromadb.HttpClient(
                host=self.chromadb_host, 
                port=self.chromadb_port
            )
            
            # Get collection
            collection = client.get_collection(name=self.collection_name)
            
            # Query vector database with department filter
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where={"department": normalized_dept}
            )
            
            # Extract and format context
            if results and results["documents"] and len(results["documents"][0]) > 0:
                context_chunks = results["documents"][0]
                context = "\n\n".join([
                    f"[Policy Guideline {i+1}]\n{chunk}" 
                    for i, chunk in enumerate(context_chunks)
                ])
                
                logger.info(f"Retrieved {len(context_chunks)} policy chunks for {normalized_dept}")
                
                return {
                    "context": context,
                    "retrieved": True,
                    "num_chunks": len(context_chunks),
                    "department": normalized_dept
                }
            else:
                logger.warning(f"No policy context found for department: {normalized_dept}")
                return {
                    "context": "",
                    "retrieved": False,
                    "error": "No relevant policies found"
                }
                
        except Exception as e:
            logger.error(f"Error retrieving policy context: {e}")
            return {
                "context": "",
                "retrieved": False,
                "error": str(e)
            }
    
    def augment_prompt_with_context(
        self, 
        original_prompt: str, 
        context: str
    ) -> str:
        """
        Augment the classification prompt with retrieved policy context
        
        Args:
            original_prompt: The original classification prompt
            context: Retrieved policy context
            
        Returns:
            Augmented prompt with policy context
        """
        if not context:
            return original_prompt
        
        augmented_prompt = f"""You are analyzing a safety event. Use the following relevant department policies and guidelines to inform your analysis:

{context}

---

Now, analyze the following incident according to the question below. Base your response on both the policies above and the incident details:

{original_prompt}"""
        
        return augmented_prompt


# Global RAG service instance
rag_service = RAGService()
