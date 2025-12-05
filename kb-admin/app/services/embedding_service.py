"""
Embedding Service
Generates embeddings using OpenAI or Anthropic
"""
from langchain_openai import OpenAIEmbeddings
from typing import List, Optional
from app.config import settings
import logging
import time

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating text embeddings"""

    def __init__(self, provider: str = "openai", api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize embedding service

        Args:
            provider: "openai" or "anthropic"
            api_key: API key (uses settings if not provided)
            model: Model name (uses default if not provided)
        """
        self.provider = provider.lower()
        self.api_key = api_key or self._get_default_api_key()
        self.model = model or self._get_default_model()

        if not self.api_key:
            raise ValueError(f"API key not provided for {self.provider}")

        self.embeddings = self._initialize_embeddings()

    def _get_default_api_key(self) -> Optional[str]:
        """Get default API key from settings"""
        if self.provider == "openai":
            return settings.OPENAI_API_KEY
        elif self.provider == "anthropic":
            return settings.ANTHROPIC_API_KEY
        return None

    def _get_default_model(self) -> str:
        """Get default model for provider"""
        if self.provider == "openai":
            return "text-embedding-3-small"
        elif self.provider == "anthropic":
            # Note: Anthropic doesn't have official embedding API yet
            # This is a placeholder - would use a different approach in production
            return "claude-3-embedding"  # Placeholder
        return "text-embedding-3-small"

    def _initialize_embeddings(self):
        """Initialize embedding model"""
        if self.provider == "openai":
            return OpenAIEmbeddings(
                openai_api_key=self.api_key,
                model=self.model
            )
        elif self.provider == "anthropic":
            # Note: Anthropic doesn't have official embedding API yet
            # In production, you'd use a different embedding service
            # For now, fallback to OpenAI or use a local model
            logger.warning("Anthropic embeddings not officially supported, using OpenAI as fallback")
            return OpenAIEmbeddings(
                openai_api_key=settings.OPENAI_API_KEY,
                model="text-embedding-3-small"
            )
        else:
            raise ValueError(f"Unsupported embedding provider: {self.provider}")

    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text

        Args:
            text: Text to embed

        Returns:
            Embedding vector as list of floats
        """
        try:
            start_time = time.time()
            embedding = self.embeddings.embed_query(text)
            elapsed = time.time() - start_time

            logger.debug(f"Generated embedding in {elapsed:.2f}s (dim={len(embedding)})")
            return embedding

        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            raise

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts (batched)

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        if not texts:
            return []

        try:
            start_time = time.time()

            # Process in batches to respect rate limits
            batch_size = settings.EMBEDDING_BATCH_SIZE
            all_embeddings = []

            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                embeddings = self.embeddings.embed_documents(batch)
                all_embeddings.extend(embeddings)

                logger.debug(f"Processed batch {i // batch_size + 1} ({len(batch)} texts)")

                # Small delay to avoid rate limiting
                if i + batch_size < len(texts):
                    time.sleep(0.1)

            elapsed = time.time() - start_time
            logger.info(f"Generated {len(all_embeddings)} embeddings in {elapsed:.2f}s")

            return all_embeddings

        except Exception as e:
            logger.error(f"Failed to generate batch embeddings: {e}")
            raise

    def get_embedding_dimension(self) -> int:
        """
        Get dimension of embedding vectors

        Returns:
            Embedding dimension
        """
        if self.provider == "openai":
            if "text-embedding-3-small" in self.model:
                return 1536
            elif "text-embedding-3-large" in self.model:
                return 3072
            else:
                return 1536  # Default
        elif self.provider == "anthropic":
            return 1024  # Placeholder
        return 1536


def get_embedding_service(
    provider: str = "openai",
    api_key: Optional[str] = None,
    model: Optional[str] = None
) -> EmbeddingService:
    """
    Factory function to get embedding service

    Args:
        provider: "openai" or "anthropic"
        api_key: API key (optional)
        model: Model name (optional)

    Returns:
        EmbeddingService instance
    """
    return EmbeddingService(provider=provider, api_key=api_key, model=model)
