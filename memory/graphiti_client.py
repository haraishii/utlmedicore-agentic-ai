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
from graphiti_core.llm_client.client import LLMClient
from graphiti_core.llm_client.openai_generic_client import OpenAIGenericClient
from graphiti_core.llm_client.config import LLMConfig, DEFAULT_MAX_TOKENS, ModelSize
from graphiti_core.llm_client.errors import RateLimitError
from graphiti_core.embedder.openai import OpenAIEmbedder, OpenAIEmbedderConfig
from graphiti_core.prompts.models import Message

# Load .env file FIRST so os.getenv() picks up OLLAMA_CLOUD_API_KEY etc.
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not installed, rely on system env vars

# ============================================================
# OLLAMA CONFIGURATION
# Ollama runs an OpenAI-compatible API at localhost:11434/v1
# graphiti-core connects to it by pointing base_url here.
# No real OpenAI key needed — "ollama" is a dummy placeholder.
# ============================================================

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")

# ============================================================
# 🔧 GRAPHITI LLM MODEL CONFIGURATION
# ─────────────────────────────────────────────────────────────
# Graphiti uses this model to EXTRACT ENTITIES & BUILD EDGES
# from each patient snapshot text. Faster = better for this.
#
# ✅ CONFIRMED WORKING CLOUD MODELS (via Ollama Cloud):
#    "glm4.7:cloud"             ← Default (fast, good JSON extraction)
#    "mistral-large-3:675b"     ← More powerful, slightly slower
#    "kimi-k2-thinking"         ← Smartest, 200k context, slowest
#
# ✅ LOCAL FALLBACK (slower but free):
#    "llama3.1:8b"
#    "lfm2.5-thinking:1.2b"
#
# To change model, edit GRAPHITI_CLOUD_MODEL below ↓
# ============================================================

OLLAMA_CLOUD_BASE_URL = os.getenv("OLLAMA_CLOUD_BASE_URL", "https://api.ollama.com/v1")
OLLAMA_CLOUD_API_KEY  = os.getenv("OLLAMA_CLOUD_API_KEY", "")

# ─────────────────────────────────────────────────────────────
# ★ TOGGLE: set GRAPHITI_USE_CLOUD=false in .env to force local
#   (useful to save tokens or test local speed)
# ─────────────────────────────────────────────────────────────
GRAPHITI_USE_CLOUD = os.getenv("GRAPHITI_USE_CLOUD", "true").lower() == "true"

# ★ CHANGE THIS LINE to swap cloud extraction model:
GRAPHITI_CLOUD_MODEL  = os.getenv("GRAPHITI_CLOUD_MODEL", "mistral-large-3:675b")

# ★ CHANGE THIS LINE to swap local extraction model:
#   Options (fastest → slowest):
#   "llama3.1:8b"           ← balanced, yields strictly well-formatted JSON
#   "lfm2.5-thinking:1.2b"  ← too verbose, fails graphiti schema validations
GRAPHITI_LOCAL_MODEL  = os.getenv("GRAPHITI_LLM_MODEL", "llama3.1:8b")

# Embedding model stays local (fast & free, no need for cloud)
OLLAMA_EMBED_MODEL = os.getenv("GRAPHITI_EMBED_MODEL", "nomic-embed-text")
OLLAMA_EMBED_DIM = int(os.getenv("GRAPHITI_EMBED_DIM", "768"))

# ============================================================
# NEO4J CONFIGURATION
# ============================================================
NEO4J_URI      = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER     = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

_graphiti_instance = None


class OllamaCloudLLMClient(LLMClient):
    """
    Custom Graphiti LLMClient that uses the native ollama Python library
    to call Ollama Cloud — same protocol as call_ollama_cloud() in the main app.
    
    Properly inherits from graphiti_core's LLMClient ABC so set_tracer,
    caching, and retry logic are all handled by the base class.
    """

    def __init__(self, model: str, api_key: str):
        config = LLMConfig(
            api_key=api_key,
            model=model,
            base_url="https://ollama.com",
        )
        super().__init__(config=config, cache=False)
        self._ollama_api_key = api_key
        self._ollama_client = None

    def _get_ollama_client(self):
        """Lazy-init the native ollama.Client (same as call_ollama_cloud)."""
        if self._ollama_client is None:
            from ollama import Client as _OllamaClient
            self._ollama_client = _OllamaClient(
                host='https://ollama.com',
                headers={'Authorization': 'Bearer ' + self._ollama_api_key}
            )
        return self._ollama_client

    async def _generate_response(
        self,
        messages: list[Message],
        response_model=None,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        model_size: ModelSize = ModelSize.medium,
    ) -> dict:
        """
        Required abstract method from LLMClient.
        Calls Ollama Cloud via native protocol and returns a dict.
        """
        import asyncio

        # Convert graphiti Message objects → ollama dicts
        msg_dicts = [{"role": m.role, "content": m.content} for m in messages]

        client = self._get_ollama_client()

        # Run the synchronous ollama.Client.chat() in a thread pool
        resp = await asyncio.to_thread(
            client.chat,
            model=self.model,
            messages=msg_dicts,
            stream=False
        )

        content = resp['message']['content'] if isinstance(resp, dict) else resp.message.content

        # Graphiti expects a dict back from _generate_response
        # Parse JSON if a response_model was injected into the prompt by the base class
        if response_model is not None:
            import json
            clean = content.strip()
            # Strip markdown code fences if present
            if clean.startswith("```"):
                lines = clean.split("\n")
                clean = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
            try:
                return json.loads(clean)
            except json.JSONDecodeError:
                # Return raw so Graphiti can handle the error itself
                return {"content": content}

        return {"content": content}


def _build_llm_client():
    """
    Build LLM client for Graphiti entity extraction.
    Cloud (fast, costs tokens) → Local (free, slower).
    Toggle with GRAPHITI_USE_CLOUD=false in .env
    """
    import openai
    from openai import AsyncOpenAI
    import httpx

    # ── USE CLOUD if API key present AND toggle is on ─────────
    if OLLAMA_CLOUD_API_KEY and GRAPHITI_USE_CLOUD:
        print(f"[Graphiti] [CLOUD]  Using CLOUD model: {GRAPHITI_CLOUD_MODEL}")
        print(f"[Graphiti]    (set GRAPHITI_USE_CLOUD=false in .env to switch to local)")
        return OllamaCloudLLMClient(
            model=GRAPHITI_CLOUD_MODEL,
            api_key=OLLAMA_CLOUD_API_KEY,
        )

    # ── LOCAL Ollama ──────────────────────────────────────────
    reason = "GRAPHITI_USE_CLOUD=false" if not GRAPHITI_USE_CLOUD else "no cloud key"
    print(f"[Graphiti] [LOCAL]  Using LOCAL model: {GRAPHITI_LOCAL_MODEL} ({reason})")
    config = LLMConfig(
        api_key="ollama",
        model=GRAPHITI_LOCAL_MODEL,
        base_url=OLLAMA_BASE_URL,
    )
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
        active_model = GRAPHITI_CLOUD_MODEL if OLLAMA_CLOUD_API_KEY else GRAPHITI_LOCAL_MODEL
        print(f"[Graphiti]   LLM   : {active_model} ({'Cloud' if OLLAMA_CLOUD_API_KEY else 'Local'})")
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
