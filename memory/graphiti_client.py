"""
Graphiti Client Singleton for UTLMediCore
==========================================
100% LOCAL — Uses Ollama for LLM + Embeddings. Zero API cost.

Requirements:
- Neo4j Desktop running at bolt://localhost:7687
- ollama pull nomic-embed-text  (embedding model, 274 MB)
- llama3.1:8b or lfm2.5-thinking:1.2b already pulled (you have both)

Usage:
    from memory.graphiti_client import get_graphiti
    graphiti = await get_graphiti()
"""

import os
from graphiti_core import Graphiti
from graphiti_core.llm_client.openai_generic_client import OpenAIGenericClient
from graphiti_core.llm_client.config import LLMConfig
from graphiti_core.embedder.openai import OpenAIEmbedder, OpenAIEmbedderConfig

# ============================================================
# OLLAMA CONFIGURATION
# Ollama runs an OpenAI-compatible API at localhost:11434/v1
# graphiti-core connects to it by pointing base_url here.
# No real OpenAI key needed — "ollama" is a dummy placeholder.
# ============================================================

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")

# LLM for entity extraction & relationship building inside Graphiti.
OLLAMA_LLM_MODEL = os.getenv("GRAPHITI_LLM_MODEL", "llama3.1:8b")

# Embedding model for semantic search inside the memory graph.
OLLAMA_EMBED_MODEL = os.getenv("GRAPHITI_EMBED_MODEL", "nomic-embed-text")
OLLAMA_EMBED_DIM = int(os.getenv("GRAPHITI_EMBED_DIM", "768"))

# ============================================================
# NEO4J CONFIGURATION
# ============================================================
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

_graphiti_instance = None


def _build_llm_client():
    """
    Build an LLM client pointed at local Ollama instead of OpenAI.
    Using OpenAIGenericClient forces all internal LLM calls to use this 
    Ollama model structure effectively avoiding hardcoded models.
    """
    import openai
    from openai import AsyncOpenAI
    import httpx
    
    # Explicitly force the underlying OpenAI library base URL
    openai.base_url = OLLAMA_BASE_URL
    openai.api_key = "ollama"
    
    config = LLMConfig(
        api_key="ollama",
        model=OLLAMA_LLM_MODEL,
        base_url=OLLAMA_BASE_URL,
    )
    
    # Override OpenAI client to wait up to 5 minutes (for slower local models)
    custom_client = AsyncOpenAI(
        api_key="ollama", 
        base_url=OLLAMA_BASE_URL,
        timeout=httpx.Timeout(300.0),
        max_retries=0
    )
    
    return OpenAIGenericClient(config=config, client=custom_client)


def _build_embedder() -> OpenAIEmbedder:
    """
    Build an Embedder pointed at local Ollama/nomic-embed-text.
    First run: ollama pull nomic-embed-text  (~274 MB, one-time)
    """
    from openai import AsyncOpenAI
    import httpx
    
    config = OpenAIEmbedderConfig(
        api_key="ollama",       # Dummy — Ollama doesn't validate this
        embedding_model=OLLAMA_EMBED_MODEL,
        embedding_dim=OLLAMA_EMBED_DIM,
        base_url=OLLAMA_BASE_URL,
    )
    
    custom_client = AsyncOpenAI(
        api_key="ollama", 
        base_url=OLLAMA_BASE_URL,
        timeout=httpx.Timeout(120.0),
        max_retries=0
    )
    
    return OpenAIEmbedder(config=config, client=custom_client)


async def get_graphiti() -> Graphiti:
    """
    Get or create the Graphiti singleton (Ollama-backed).
    Connects to Neo4j on first call, then reuses the connection.
    """
    global _graphiti_instance
    if _graphiti_instance is None:
        print(f"[Graphiti] Connecting...")
        print(f"[Graphiti]   Neo4j : {NEO4J_URI}")
        print(f"[Graphiti]   LLM   : {OLLAMA_LLM_MODEL} via Ollama")
        print(f"[Graphiti]   Embed : {OLLAMA_EMBED_MODEL} (dim={OLLAMA_EMBED_DIM})")

        _graphiti_instance = Graphiti(
            uri=NEO4J_URI,
            user=NEO4J_USER,
            password=NEO4J_PASSWORD,
            llm_client=_build_llm_client(),
            embedder=_build_embedder()
        )
        
        # Override neo4j driver internal timeouts and pool size
        if hasattr(_graphiti_instance, 'driver'):
            _graphiti_instance._driver_kwargs = {
                "connection_timeout": 120.0,
                "connection_acquisition_timeout": 120.0,
                "max_connection_lifetime": 200.0,
                "max_connection_pool_size": 500
            }

        # Build vector indices and constraints — only needed on the very first run.
        # Safe to call repeatedly; it's a no-op if indices already exist.
        await _graphiti_instance.build_indices_and_constraints()
        print("[Graphiti] Memory graph ready - 100% local, zero API cost!")

    return _graphiti_instance


async def close_graphiti():
    """Cleanly close the Graphiti connection (call on Flask shutdown)."""
    global _graphiti_instance
    if _graphiti_instance:
        await _graphiti_instance.close()
        _graphiti_instance = None
        print("[Graphiti] Connection closed.")
