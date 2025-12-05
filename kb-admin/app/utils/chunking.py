"""
Text Chunking Utilities
Handles document splitting and chunking for vectorization
"""
from langchain.text_splitter import RecursiveCharacterTextSplitter, MarkdownTextSplitter
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class ChunkingService:
    """Service for chunking documents"""

    @staticmethod
    def chunk_text(
        text: str,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        is_markdown: bool = False
    ) -> List[str]:
        """
        Split text into chunks with overlap

        Args:
            text: Text content to chunk
            chunk_size: Maximum chunk size in characters
            chunk_overlap: Overlap between chunks
            is_markdown: Whether text is markdown format

        Returns:
            List of text chunks
        """
        if not text or len(text.strip()) == 0:
            logger.warning("Empty text provided for chunking")
            return []

        try:
            if is_markdown:
                splitter = MarkdownTextSplitter(
                    chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap
                )
            else:
                splitter = RecursiveCharacterTextSplitter(
                    chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap,
                    separators=["\n\n", "\n", ". ", " ", ""]
                )

            chunks = splitter.split_text(text)
            logger.info(f"Split text into {len(chunks)} chunks (avg size: {sum(len(c) for c in chunks) // len(chunks)} chars)")

            return chunks

        except Exception as e:
            logger.error(f"Error chunking text: {e}")
            raise

    @staticmethod
    def chunk_document(
        title: str,
        content: str,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        is_markdown: bool = False
    ) -> List[Dict[str, str]]:
        """
        Chunk a document and return chunks with metadata

        Args:
            title: Document title
            content: Document content
            chunk_size: Maximum chunk size
            chunk_overlap: Overlap between chunks
            is_markdown: Whether content is markdown

        Returns:
            List of dictionaries with chunk content and metadata
        """
        chunks = ChunkingService.chunk_text(content, chunk_size, chunk_overlap, is_markdown)

        chunked_docs = []
        for idx, chunk in enumerate(chunks):
            chunked_docs.append({
                "content": chunk,
                "title": title,
                "chunk_index": idx,
                "total_chunks": len(chunks)
            })

        return chunked_docs

    @staticmethod
    def estimate_chunk_count(text: str, chunk_size: int = 1000) -> int:
        """
        Estimate number of chunks without actually splitting

        Args:
            text: Text content
            chunk_size: Maximum chunk size

        Returns:
            Estimated number of chunks
        """
        if not text:
            return 0

        return max(1, len(text) // chunk_size)
