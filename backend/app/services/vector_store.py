import uuid
import logging
import hashlib
from typing import List, Dict, Any, Optional
import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.exceptions import UnexpectedResponse
from app.database.database import qdrant_client

logger = logging.getLogger("aegisai.services.vector_store")

class AegisVectorStore:
    """
    Manages semantic vector store operations in Qdrant with local memory fallback resilience.
    """
    def __init__(self, client: QdrantClient = qdrant_client, collection_name: str = "aegisai_explanations") -> None:
        self.client = client
        self.collection_name = collection_name
        self.dimension = 384
        self.use_fallback = False
        self.fallback_db: Dict[str, Dict[str, Any]] = {} # id -> {vector: list, payload: dict}
        self._initialize_collection()

    def _initialize_collection(self) -> None:
        """Ensures Qdrant collection is configured and ready."""
        try:
            # Check connection
            collections = self.client.get_collections()
            exists = any(c.name == self.collection_name for c in collections.collections)
            if not exists:
                self.client.recreate_collection(
                    collection_name=self.collection_name,
                    vectors_config=models.VectorParams(size=self.dimension, distance=models.Distance.COSINE)
                )
                logger.info(f"Qdrant collection '{self.collection_name}' initialized successfully.")
        except Exception as e:
            self.use_fallback = True
            logger.warning(f"Qdrant service unreachable: {e}. Activating memory fallback storage.")

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generates a 384-dimensional deterministic feature hashing embedding representation.
        Uses SHA-256 to map word tokens to reproducible weights.
        """
        words = text.lower().split()
        vector = np.zeros(self.dimension)
        if not words:
            return [0.0] * self.dimension
            
        for word in words:
            # Hash token to an index in [0, 383]
            h = hashlib.sha256(word.encode("utf-8")).hexdigest()
            idx = int(h, 16) % self.dimension
            # Add frequency weight
            vector[idx] += 1.0

        # L2 normalization
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm

        return vector.tolist()

    async def upsert_explanation(
        self,
        transaction_id: uuid.UUID,
        explanation_text: str,
        verdict: str,
        risk_score: float,
        timestamp: str
    ) -> Optional[uuid.UUID]:
        """
        Indexes an explanation entry to the semantic search ledger.
        """
        point_id = uuid.uuid5(uuid.NAMESPACE_DNS, str(transaction_id))
        vector = self.generate_embedding(explanation_text)
        payload = {
            "transaction_id": str(transaction_id),
            "explanation": explanation_text,
            "verdict": verdict,
            "risk_score": float(risk_score),
            "timestamp": timestamp
        }

        if self.use_fallback:
            self.fallback_db[str(point_id)] = {"vector": vector, "payload": payload}
            return point_id

        try:
            self.client.upsert(
                collection_name=self.collection_name,
                points=[
                    models.PointStruct(
                        id=str(point_id),
                        vector=vector,
                        payload=payload
                    )
                ]
            )
            return point_id
        except Exception as e:
            logger.error(f"Failed to upsert to Qdrant: {e}. Falling back.")
            self.fallback_db[str(point_id)] = {"vector": vector, "payload": payload}
            return point_id

    async def search_similar(self, query_text: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Performs cosine-similarity semantic searches over indexed governance decisions.
        """
        query_vector = self.generate_embedding(query_text)
        results = []

        if self.use_fallback:
            # Calculate manual cosine similarity
            q_arr = np.array(query_vector)
            q_norm = np.linalg.norm(q_arr)
            for pid, doc in self.fallback_db.items():
                d_arr = np.array(doc["vector"])
                d_norm = np.linalg.norm(d_arr)
                if q_norm > 0 and d_norm > 0:
                    sim = float(np.dot(q_arr, d_arr) / (q_norm * d_norm))
                else:
                    sim = 0.0
                results.append({"payload": doc["payload"], "score": sim})
            # Sort by similarity score desc
            results.sort(key=lambda x: x["score"], reverse=True)
            return results[:limit]

        try:
            response = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit
            )
            for hit in response:
                results.append({
                    "payload": hit.payload,
                    "score": hit.score
                })
            return results
        except Exception as e:
            logger.error(f"Failed to search Qdrant: {e}")
            return []

# Instantiate global vector storage adapter
aegis_vector_store = AegisVectorStore()
