"""
Phoenix Experiments - Professional Evaluation Framework

This script integrates with Arize Phoenix's native Experiments API to:
1. Run evaluations with centralized experiment tracking
2. Attach custom evaluator scores directly to traces
3. Enable experiment comparison and version tracking in Phoenix UI

Usage:
    python scripts/phoenix_experiment.py [--limit N] [--experiment-name NAME]
"""

import json
import asyncio
import argparse
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

# Add project root to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

# Phoenix imports
import phoenix as px
from phoenix.evals import (
    run_evals,
    llm_classify,
)
from phoenix.trace import SpanEvaluations
from opentelemetry import trace

# Project imports
from backend.agents.graph import graph
from backend.agents.state import AgentState
from backend.agents.llm import get_llm
from backend.observability.phoenix import init_phoenix

# Initialize Phoenix tracing BEFORE running any agents
print("🔭 Initializing Phoenix tracing...")
init_phoenix()


# ============================================================================
# CUSTOM EVALUATORS
# ============================================================================

INTENT_ACCURACY_TEMPLATE = """You are evaluating if an AI agent correctly classified user intent.

User Question: {input}
Expected Intent: {expected_intent}
Actual Intent: {actual_intent}

Did the agent correctly classify the intent?
Respond with only: CORRECT or INCORRECT"""

SQL_QUALITY_TEMPLATE = """You are evaluating the quality of a generated SQL query.

User Question: {input}
Reference SQL: {reference_sql}
Generated SQL: {generated_sql}

Evaluate if the generated SQL would return equivalent results to the reference SQL.
Consider: table names, column selection, WHERE clauses, aggregations, ORDER BY, LIMIT.

Respond with only: EQUIVALENT, PARTIAL, or WRONG"""

ANSWER_FAITHFULNESS_TEMPLATE = """You are evaluating if an AI assistant's response is faithful to the data.

User Question: {input}
SQL Query Result: {query_result}
Assistant Response: {final_response}

Is the response faithful to the data (no hallucinations, accurate numbers)?
Respond with only: FAITHFUL or UNFAITHFUL"""


async def evaluate_intent(result: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate intent classification accuracy."""
    if result.get("expected_intent") == result.get("actual_intent"):
        return {"score": 1.0, "label": "CORRECT", "explanation": "Intent matched"}
    return {"score": 0.0, "label": "INCORRECT", "explanation": "Intent mismatch"}


async def evaluate_sql(result: Dict[str, Any], llm) -> Dict[str, Any]:
    """Evaluate SQL query quality using LLM."""
    if not result.get("reference_sql") or not result.get("generated_sql"):
        return {"score": 0.5, "label": "SKIP", "explanation": "Missing SQL"}
    
    prompt = SQL_QUALITY_TEMPLATE.format(
        input=result["input"],
        reference_sql=result["reference_sql"],
        generated_sql=result["generated_sql"]
    )
    
    response = await llm.ainvoke(prompt)
    label = response.content.strip().upper()
    
    score_map = {"EQUIVALENT": 1.0, "PARTIAL": 0.5, "WRONG": 0.0}
    return {
        "score": score_map.get(label, 0.5),
        "label": label,
        "explanation": response.content
    }


async def evaluate_faithfulness(result: Dict[str, Any], llm) -> Dict[str, Any]:
    """Evaluate answer faithfulness using LLM."""
    if not result.get("final_response"):
        return {"score": 0.0, "label": "SKIP", "explanation": "No response"}
    
    prompt = ANSWER_FAITHFULNESS_TEMPLATE.format(
        input=result["input"],
        query_result=str(result.get("query_result", []))[:500],
        final_response=result.get("final_response", "")[:500]
    )
    
    response = await llm.ainvoke(prompt)
    label = response.content.strip().upper()
    
    return {
        "score": 1.0 if "FAITHFUL" in label else 0.0,
        "label": label,
        "explanation": response.content
    }


# ============================================================================
# EXPERIMENT RUNNER
# ============================================================================

def load_gold_set(path: str = None) -> List[Dict]:
    """Load evaluation dataset."""
    if path is None:
        path = Path(__file__).parent.parent / "tests" / "eval" / "gold_set.json"
    with open(path, "r") as f:
        return json.load(f)


async def run_single_task(case: Dict[str, Any]) -> Dict[str, Any]:
    """Run a single evaluation task through the agent, capturing trace IDs."""
    # Get the tracer for span ID capture
    tracer = trace.get_tracer(__name__)
    
    result = {
        "id": case["id"],
        "input": case["input"],
        "category": case["category"],
        "expected_intent": case["expected_intent"],
        "reference_sql": case.get("reference_sql"),
        "expected_answer_contains": case.get("expected_answer_contains", []),
        "actual_intent": None,
        "generated_sql": None,
        "query_result": None,
        "final_response": None,
        "error": None,
        "trace_id": None,
        "span_id": None
    }
    
    try:
        initial_state: AgentState = {
            "user_question": case["input"],
            "messages": [],
            "intent": None,
            "confidence": 0.0,
            "tables_needed": [],
            "query_strategy": None,
            "sql_query": None,
            "critic_feedback": None,
            "critic_approved": False,
            "retry_count": 0,
            "query_result": None,
            "needs_visualization": False,
            "visualization_code": None,
            "final_response": None,
            "error_message": None,
        }
        
        # Create a parent span for this evaluation task
        with tracer.start_as_current_span(f"evaluation_{case['id']}") as span:
            # Capture the trace and span IDs for later annotation
            ctx = trace.get_current_span().get_span_context()
            result["trace_id"] = format(ctx.trace_id, '032x')
            result["span_id"] = format(ctx.span_id, '016x')
            
            # Add evaluation metadata to span
            span.set_attribute("eval.test_id", case["id"])
            span.set_attribute("eval.category", case["category"])
            span.set_attribute("eval.expected_intent", case["expected_intent"])
            
            async for event in graph.astream(initial_state):
                for key, value in event.items():
                    if key == "router" and value.get("intent"):
                        result["actual_intent"] = value.get("intent")
                    if key == "coder" and value.get("sql_query"):
                        result["generated_sql"] = value.get("sql_query")
                    if key == "executor" and value.get("query_result") is not None:
                        result["query_result"] = value.get("query_result")
                    if value.get("final_response"):
                        result["final_response"] = value.get("final_response")
                    
    except Exception as e:
        result["error"] = str(e)
    
    return result



async def run_experiment(
    experiment_name: str,
    gold_set: List[Dict],
    limit: Optional[int] = None
) -> Dict[str, Any]:
    """
    Run a complete experiment with Phoenix tracking.
    """
    if limit:
        gold_set = gold_set[:limit]
    
    print(f"\n{'='*60}")
    print(f"  PHOENIX EXPERIMENT: {experiment_name}")
    print(f"{'='*60}")
    print(f"  Test Cases: {len(gold_set)}")
    print(f"  Timestamp: {datetime.now().isoformat()}")
    print(f"{'='*60}\n")
    
    # Get LLM for evaluators
    llm = get_llm(temperature=0.0)
    
    # Run tasks and collect results
    all_results = []
    eval_scores = {
        "intent_accuracy": [],
        "sql_quality": [],
        "faithfulness": []
    }
    
    for i, case in enumerate(gold_set):
        print(f"[{i+1}/{len(gold_set)}] Running: {case['id']} - {case['input'][:50]}...")
        
        # Run the agent
        result = await run_single_task(case)
        all_results.append(result)
        
        # Run evaluators
        intent_eval = await evaluate_intent(result)
        eval_scores["intent_accuracy"].append(intent_eval)
        
        if result.get("reference_sql"):
            sql_eval = await evaluate_sql(result, llm)
            eval_scores["sql_quality"].append(sql_eval)
        
        if result.get("final_response"):
            faith_eval = await evaluate_faithfulness(result, llm)
            eval_scores["faithfulness"].append(faith_eval)
        
        status = "✓" if intent_eval["score"] == 1.0 else "✗"
        print(f"         {status} Intent: {result['actual_intent']}")
    
    # Calculate aggregate scores
    summary = {
        "experiment_name": experiment_name,
        "timestamp": datetime.now().isoformat(),
        "total_cases": len(gold_set),
        "intent_accuracy": sum(e["score"] for e in eval_scores["intent_accuracy"]) / len(eval_scores["intent_accuracy"]) if eval_scores["intent_accuracy"] else 0,
        "sql_quality": sum(e["score"] for e in eval_scores["sql_quality"]) / len(eval_scores["sql_quality"]) if eval_scores["sql_quality"] else 0,
        "faithfulness": sum(e["score"] for e in eval_scores["faithfulness"]) / len(eval_scores["faithfulness"]) if eval_scores["faithfulness"] else 0,
    }
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"          EXPERIMENT RESULTS: {experiment_name}")
    print(f"{'='*60}")
    print(f"  Total Test Cases:    {summary['total_cases']}")
    print(f"  Intent Accuracy:     {summary['intent_accuracy']*100:.1f}%")
    print(f"  SQL Quality:         {summary['sql_quality']*100:.1f}%")
    print(f"  Faithfulness:        {summary['faithfulness']*100:.1f}%")
    print(f"{'='*60}")
    print(f"\n📊 View detailed traces at: http://localhost:6006")
    print(f"   Project: antigravirt")
    print(f"   Experiment: {experiment_name}\n")
    
    # Save results to JSON for Phoenix import
    output_path = Path(__file__).parent.parent / f"experiment_{experiment_name}.json"
    with open(output_path, "w") as f:
        json.dump({
            "summary": summary,
            "results": all_results,
            "evaluations": eval_scores
        }, f, indent=2, default=str)
    
    print(f"Results saved to: {output_path}")
    
    # =========================================================================
    # LOG EVALUATIONS TO PHOENIX (Attach scores to traces as annotations)
    # =========================================================================
    try:
        import pandas as pd
        
        # Create DataFrames for each evaluation type
        eval_dfs = []
        
        for i, result in enumerate(all_results):
            if result.get("span_id"):
                # Intent Accuracy evaluation
                if i < len(eval_scores["intent_accuracy"]):
                    eval_dfs.append({
                        "span_id": result["span_id"],
                        "name": "intent_accuracy",
                        "label": eval_scores["intent_accuracy"][i]["label"],
                        "score": eval_scores["intent_accuracy"][i]["score"],
                        "explanation": eval_scores["intent_accuracy"][i]["explanation"]
                    })
                
                # SQL Quality evaluation
                if i < len(eval_scores["sql_quality"]):
                    eval_dfs.append({
                        "span_id": result["span_id"],
                        "name": "sql_quality",
                        "label": eval_scores["sql_quality"][i]["label"],
                        "score": eval_scores["sql_quality"][i]["score"],
                        "explanation": eval_scores["sql_quality"][i]["explanation"]
                    })
                
                # Faithfulness evaluation
                if i < len(eval_scores["faithfulness"]):
                    eval_dfs.append({
                        "span_id": result["span_id"],
                        "name": "faithfulness",
                        "label": eval_scores["faithfulness"][i]["label"],
                        "score": eval_scores["faithfulness"][i]["score"],
                        "explanation": eval_scores["faithfulness"][i]["explanation"]
                    })
        
        if eval_dfs:
            df = pd.DataFrame(eval_dfs)
            
            # Log to Phoenix for each evaluation type
            client = px.Client()
            
            for eval_name in ["intent_accuracy", "sql_quality", "faithfulness"]:
                eval_subset = df[df["name"] == eval_name]
                if not eval_subset.empty:
                    print(f"📊 Logging {len(eval_subset)} '{eval_name}' evaluations to Phoenix...")
                    client.log_evaluations(
                        SpanEvaluations(
                            eval_name=eval_name,
                            dataframe=eval_subset[["span_id", "label", "score", "explanation"]]
                        )
                    )
            
            print("✅ Evaluations logged to Phoenix successfully!")
            print("   Check the 'Annotations' column in Phoenix Traces view.")
    
    except Exception as e:
        print(f"⚠️  Warning: Could not log evaluations to Phoenix: {e}")
    
    return summary


async def main():
    parser = argparse.ArgumentParser(description="Run Phoenix Experiment")
    parser.add_argument("--experiment-name", type=str, default=f"baseline_{datetime.now().strftime('%Y%m%d_%H%M')}")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--gold-set", type=str, default=None)
    args = parser.parse_args()
    
    gold_set = load_gold_set(args.gold_set)
    summary = await run_experiment(args.experiment_name, gold_set, args.limit)
    
    return summary


if __name__ == "__main__":
    asyncio.run(main())
