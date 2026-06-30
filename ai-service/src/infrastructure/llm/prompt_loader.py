# ─────────────────────────────────────────────────────────────────
# src/infrastructure/llm/prompt_loader.py
# ─────────────────────────────────────────────────────────────────

import os
import hashlib
from typing import Dict, Tuple

class PromptLoader:
    """
    Loads and caches prompts from the filesystem.
    Calculates SHA256 hashes for observability.
    """
    _cache: Dict[str, Tuple[str, str]] = {}
    
    @classmethod
    def load_prompt(cls, prompt_name: str, version: str) -> Tuple[str, str, str]:
        """
        Loads a prompt by name and version.
        Returns: (prompt_content, version, prompt_hash)
        """
        cache_key = f"{prompt_name}_v{version}"
        if cache_key in cls._cache:
            content, prompt_hash = cls._cache[cache_key]
            return content, version, prompt_hash
            
        # Resolve path
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        prompt_path = os.path.join(base_dir, "prompts", prompt_name, f"v{version}.md")
        
        if not os.path.exists(prompt_path):
            raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
            
        with open(prompt_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            
        prompt_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
        
        cls._cache[cache_key] = (content, prompt_hash)
        return content, version, prompt_hash
