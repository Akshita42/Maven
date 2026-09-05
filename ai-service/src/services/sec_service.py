# ─────────────────────────────────────────────────────────────────
# src/services/sec_service.py
# ─────────────────────────────────────────────────────────────────
# Service for parsing, section-aware chunking, and preparing SEC 
# qualitative disclosures for vector store indexing.
# ─────────────────────────────────────────────────────────────────

from typing import List, Dict, Any
from src.providers.sec_provider import SECProvider
from src.utils.logger import logger

class SECService:
    """
    Coordinates SEC filing retrieval and section-aware text chunking.
    """
    
    def __init__(self, provider: SECProvider = None):
        self.provider = provider or SECProvider()

    def get_filing_chunks(self, ticker: str, chunk_size: int = 400, overlap: int = 50) -> List[Dict[str, Any]]:
        """
        Retrieves SEC filing sections for ticker and chunks text into section-aware chunks.
        Each chunk is returned with structured metadata.
        """
        sections = self.provider.fetch_filing_sections(ticker)
        chunks = []
        chunk_counter = 0
        
        for section_name, content in sections.items():
            if not content.strip():
                continue
                
            # Split text into overlapping windows
            words = content.split()
            step = chunk_size - overlap
            if step <= 0:
                step = chunk_size
                
            for i in range(0, len(words), step):
                chunk_words = words[i:i + chunk_size]
                chunk_text = " ".join(chunk_words)
                
                if len(chunk_text.strip()) < 15:
                    continue
                    
                chunk_counter += 1
                chunks.append({
                    "id": f"{ticker.lower()}-chunk-{chunk_counter}",
                    "text": chunk_text,
                    "metadata": {
                        "ticker": ticker.upper(),
                        "section": section_name,
                        "chunk_index": chunk_counter
                    }
                })
                
        logger.info(f"[SECService] Generated {len(chunks)} text chunks for ticker: {ticker}")
        return chunks
