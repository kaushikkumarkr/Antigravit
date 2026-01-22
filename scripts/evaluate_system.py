"""
System Evaluation Script for Antigravirt

This script runs a batch evaluation of the agentic system against a curated 
Gold Set of test cases. It uses Arize Phoenix for observability and trace capture.

Usage:
    python scripts/evaluate_system.py [--limit N] [--output results.csv]
"""

import json
import asyncio
import argparse
import csv
import time
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Optional, List

# Add project root to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.agents.graph import graph
from backend.agents.state import AgentState


@dataclass
class EvalResult:
    """Result of a single evaluation run."""
    id: str
    input: str
    category: str
    expected_intent: str
    actual_intent: Optional[str]
    intent_correct: bool
    reference_sql: Optional[str]
    generated_sql: Optional[str]
    sql_executed: bool
    final_response: Optional[str]
    answer_contains_expected: bool
    latency_ms: float
    error: Optional[str]
    timestamp: str


def load_gold_set(path: str = None) -> List[dict]:
    """Load the gold evaluation dataset."""
    if path is None:
        path = Path(__file__).parent.parent / "tests" / "eval" / "gold_set.json"
    
    with open(path, "r") as f:
        return json.load(f)


def check_answer_contains(response: str, expected_keywords: List[str]) -> bool:
    """Check if the response contains expected keywords (case-insensitive)."""
    if not response:
        return False
    response_lower = response.lower()
    return any(keyword.lower() in response_lower for keyword in expected_keywords)


async def evaluate_single_case(graph, case: dict) -> EvalResult:
    """Run a single evaluation case through the agent pipeline."""
    start_time = time.time()
    error = None
    actual_intent = None
    generated_sql = None
    final_response = None
    sql_executed = False
    
    try:
        # Initialize state with the test question
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
        
        # Run the graph
        final_state = None
        async for event in graph.astream(initial_state):
            for key, value in event.items():
                if key == "router" and value.get("intent"):
                    actual_intent = value.get("intent")
                if key == "coder" and value.get("sql_query"):
                    generated_sql = value.get("sql_query")
                if key == "executor" and value.get("query_result") is not None:
                    sql_executed = True
                if value.get("final_response"):
                    final_response = value.get("final_response")
        
    except Exception as e:
        error = str(e)
    
    latency_ms = (time.time() - start_time) * 1000
    
    # Evaluate results
    intent_correct = (actual_intent == case["expected_intent"]) if actual_intent else False
    answer_contains_expected = check_answer_contains(
        final_response, 
        case.get("expected_answer_contains", [])
    )
    
    return EvalResult(
        id=case["id"],
        input=case["input"],
        category=case["category"],
        expected_intent=case["expected_intent"],
        actual_intent=actual_intent,
        intent_correct=intent_correct,
        reference_sql=case.get("reference_sql"),
        generated_sql=generated_sql,
        sql_executed=sql_executed,
        final_response=final_response[:500] if final_response else None,  # Truncate
        answer_contains_expected=answer_contains_expected,
        latency_ms=round(latency_ms, 2),
        error=error,
        timestamp=datetime.now().isoformat()
    )


def save_results_csv(results: List[EvalResult], output_path: str):
    """Save evaluation results to CSV."""
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(asdict(results[0]).keys()))
        writer.writeheader()
        for result in results:
            writer.writerow(asdict(result))
    print(f"Results saved to: {output_path}")


def print_summary(results: List[EvalResult]):
    """Print a summary of evaluation results."""
    total = len(results)
    intent_correct = sum(1 for r in results if r.intent_correct)
    sql_executed = sum(1 for r in results if r.sql_executed)
    answer_correct = sum(1 for r in results if r.answer_contains_expected)
    errors = sum(1 for r in results if r.error)
    avg_latency = sum(r.latency_ms for r in results) / total if total > 0 else 0
    
    print("\n" + "=" * 60)
    print("          ANTIGRAVIRT EVALUATION SUMMARY")
    print("=" * 60)
    print(f"  Total Test Cases:      {total}")
    print(f"  Intent Accuracy:       {intent_correct}/{total} ({100*intent_correct/total:.1f}%)")
    print(f"  SQL Execution Success: {sql_executed}/{total} ({100*sql_executed/total:.1f}%)")
    print(f"  Answer Quality:        {answer_correct}/{total} ({100*answer_correct/total:.1f}%)")
    print(f"  Error Rate:            {errors}/{total} ({100*errors/total:.1f}%)")
    print(f"  Avg Latency:           {avg_latency:.0f}ms")
    print("=" * 60)
    
    # Per-category breakdown
    categories = set(r.category for r in results)
    print("\nPer-Category Breakdown:")
    for cat in categories:
        cat_results = [r for r in results if r.category == cat]
        cat_correct = sum(1 for r in cat_results if r.intent_correct)
        print(f"  {cat}: {cat_correct}/{len(cat_results)} intent correct")
    
    print("\n")


async def main():
    parser = argparse.ArgumentParser(description="Evaluate Antigravirt Agent System")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of test cases")
    parser.add_argument("--output", type=str, default="eval_results.csv", help="Output CSV path")
    parser.add_argument("--gold-set", type=str, default=None, help="Path to gold_set.json")
    args = parser.parse_args()
    
    print("=" * 60)
    print("     ANTIGRAVIRT SYSTEM EVALUATION")
    print("=" * 60)
    
    # Load test cases
    gold_set = load_gold_set(args.gold_set)
    if args.limit:
        gold_set = gold_set[:args.limit]
    
    print(f"Loaded {len(gold_set)} test cases")
    
    # The graph is already compiled in the import
    print("Using pre-compiled agent graph...")
    
    # Run evaluations
    results: List[EvalResult] = []
    
    for i, case in enumerate(gold_set):
        print(f"[{i+1}/{len(gold_set)}] Evaluating: {case['id']} - {case['input'][:50]}...")
        result = await evaluate_single_case(graph, case)
        results.append(result)
        
        # Status indicator
        status = "✓" if result.intent_correct and result.answer_contains_expected else "✗"
        print(f"         {status} Intent: {result.actual_intent}, Latency: {result.latency_ms:.0f}ms")
    
    # Save and summarize
    save_results_csv(results, args.output)
    print_summary(results)
    
    return results


if __name__ == "__main__":
    asyncio.run(main())
