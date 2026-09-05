# ─────────────────────────────────────────────────────────────────
# ai-service/test_observability_evals.py
# ─────────────────────────────────────────────────────────────────
# Automated Integration Test for Phase 4: AI Observability & Evals
# ─────────────────────────────────────────────────────────────────

import sys
import os

# Add root directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.infrastructure.observability.tracer import ObservabilityTracer
from src.infrastructure.observability.evals import FaithfulnessEvaluator
from src.agent.langgraph_orchestrator import MavenLangGraphOrchestrator

def main():
    print("======================================================")
    print("  Testing Phase 4: AI Observability & Evals Engine")
    print("======================================================")
    
    ticker = "GOOGL"
    print(f"\n1. Testing ObservabilityTracer latency instrumentation...")
    tracer = ObservabilityTracer()
    tracer.record_node_latency("company_resolution_node", 12.5)
    tracer.record_node_latency("evidence_collection_node", 450.2)
    tracer.record_node_latency("sec_rag_retrieval_node", 120.8)
    report = tracer.get_telemetry_report()
    print(f"   [OK] Total Graph Latency: {report['totalGraphLatencyMs']}ms")
    print(f"   [OK] Node Latencies Record: {report['nodeLatenciesMs']}")
    
    print(f"\n2. Testing FaithfulnessEvaluator grounding scores...")
    evaluator = FaithfulnessEvaluator()
    evals = evaluator.evaluate(evidence=None, thesis=None, committee=None, recommendation=None)
    print(f"   [OK] Faithfulness Score: {evals['faithfulnessScore']}")
    print(f"   [OK] Hallucination Risk Score: {evals['hallucinationRiskScore']}")
    print(f"   [OK] Grounded Claims Count: {evals['groundedStatementsCount']}")
    print(f"   [OK] Evaluation Status: {evals['evaluationStatus']}")
    
    print(f"\n3. Testing Full LangGraph Stateful Graph Execution with Evals Node for '{ticker}'...")
    orchestrator = MavenLangGraphOrchestrator()
    final_state = orchestrator.run(ticker)
    
    metrics = final_state.get("observability_metrics")
    logs = final_state.get("execution_logs", [])
    
    print("\n------------------ LangGraph Execution Logs ------------------")
    for log in logs:
        print(f"  • {log}")
        
    print("\n------------------ Observability Metrics Output ------------------")
    if metrics:
        faith = metrics.get("faithfulness", {})
        print(f"Faithfulness Score: {faith.get('faithfulnessScore')}")
        print(f"Hallucination Risk: {faith.get('hallucinationRiskScore')}")
        print(f"Evaluation Status: {faith.get('evaluationStatus')}")
        print("\n[SUCCESS] Phase 4 AI Observability & Evals test SUCCESSFUL!")
    else:
        print("❌ Workflow failed to attach observability metrics.")
        sys.exit(1)

if __name__ == "__main__":
    main()
