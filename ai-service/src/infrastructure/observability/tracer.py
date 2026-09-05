# ─────────────────────────────────────────────────────────────────
# src/infrastructure/observability/tracer.py
# ─────────────────────────────────────────────────────────────────
# Production-grade Telemetry, Node Latency, and LangSmith Tracing Client.
# ─────────────────────────────────────────────────────────────────

import os
import time
from typing import Dict, Any, List, Optional
from src.utils.logger import logger

class ObservabilityTracer:
    """
    Tracks per-node execution latencies, token consumption, and LangSmith environment setup.
    """
    
    def __init__(self, project_name: str = "maven-ai-copilot"):
        self.project_name = project_name
        self.node_latencies: Dict[str, float] = {}
        self._init_langsmith_tracing()

    def _init_langsmith_tracing(self):
        """
        Configures LangSmith environment variables if LANGCHAIN_API_KEY is configured.
        """
        api_key = os.getenv("LANGCHAIN_API_KEY")
        if api_key:
            os.environ["LANGCHAIN_TRACING_V2"] = "true"
            os.environ["LANGCHAIN_PROJECT"] = self.project_name
            os.environ["LANGCHAIN_ENDPOINT"] = os.getenv("LANGCHAIN_ENDPOINT", "https://api.smith.langchain.com")
            logger.info(f"[ObservabilityTracer] LangSmith Tracing enabled for project: '{self.project_name}'")
        else:
            logger.info(f"[ObservabilityTracer] Telemetry initialized (LangSmith API key not configured, local tracing active).")

    def record_node_latency(self, node_name: str, latency_ms: float):
        """
        Records latency for a specific graph execution node.
        """
        self.node_latencies[node_name] = round(latency_ms, 2)
        logger.info(f"[ObservabilityTracer] Node '{node_name}' completed in {latency_ms:.2f}ms")

    def get_telemetry_report(self) -> Dict[str, Any]:
        """
        Returns consolidated telemetry summary.
        """
        total_latency = sum(self.node_latencies.values())
        return {
            "projectName": self.project_name,
            "totalGraphLatencyMs": round(total_latency, 2),
            "nodeLatenciesMs": self.node_latencies,
            "status": "TELEMETRY_RECORDED"
        }
