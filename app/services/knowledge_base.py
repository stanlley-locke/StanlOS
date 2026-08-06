import logging
import json
import numpy as np
from typing import List, Dict, Any, Optional

from app.services.ai_cloudflare import ai_client
from app.core.database import db

logger = logging.getLogger(__name__)

class KnowledgeBaseService:
    async def add_document(self, user_id: int, file_name: str, file_type: str, raw_text: str, metadata: dict = None) -> bool:
        """
        Embeds the document text and stores it in the database.
        """
        try:
            # 1. Generate embedding using Cloudflare AI
            embedding = await ai_client.generate_embeddings(raw_text)
            if not embedding:
                logger.error("Failed to generate embedding.")
                return False
                
            embedding_json = json.dumps(embedding)
            metadata_json = json.dumps(metadata or {})
            
            # 2. Save to database
            query = """
            INSERT INTO documents (user_id, file_name, file_type, raw_text, metadata_json, embedding_json)
            VALUES (?, ?, ?, ?, ?, ?)
            """
            await db.execute(query, (user_id, file_name, file_type, raw_text, metadata_json, embedding_json))
            return True
        except Exception as e:
            logger.error(f"Error adding document: {e}")
            return False

    async def search_similar(self, user_id: int, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Searches for similar documents using Cloudflare Embeddings and NumPy cosine similarity.
        """
        try:
            # 1. Get query embedding
            query_embedding = await ai_client.generate_embeddings(query)
            if not query_embedding:
                return []
            
            query_vec = np.array(query_embedding)
            
            # 2. Fetch all user documents and their embeddings
            # (For massive scale this requires Vectorize/pgvector, but for personal bot NumPy in-memory is fast enough)
            sql = "SELECT id, file_name, raw_text, embedding_json FROM documents WHERE user_id = ?"
            docs = await db.execute(sql, (user_id,), fetch=True)
            
            if not docs:
                return []
                
            results = []
            for doc in docs:
                doc_id, file_name, raw_text, embedding_json = doc
                if not embedding_json:
                    continue
                    
                doc_vec = np.array(json.loads(embedding_json))
                
                # Calculate Cosine Similarity
                similarity = np.dot(query_vec, doc_vec) / (np.linalg.norm(query_vec) * np.linalg.norm(doc_vec))
                
                results.append({
                    "id": doc_id,
                    "file_name": file_name,
                    "raw_text": raw_text,
                    "score": float(similarity)
                })
            
            # Sort by highest score first
            results.sort(key=lambda x: x["score"], reverse=True)
            return results[:top_k]
            
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return []

    async def get_context_for_query(self, user_id: int, query: str) -> Optional[str]:
        """
        Retrieve relevant context for an LLM prompt.
        """
        results = await self.search_similar(user_id, query)
        if not results:
            return None
            
        context_parts = []
        for res in results:
            context_parts.append(f"--- Document: {res['file_name']} ---\n{res['raw_text']}")
            
        return "\n\n".join(context_parts)

kb_service = KnowledgeBaseService()
