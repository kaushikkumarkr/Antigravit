"""
Arize Phoenix Integration for LLM Observability

This module initializes Phoenix tracing for LangChain/LangGraph operations.
Traces are sent to the Phoenix collector for visualization and analysis.
"""

import os
import logging

logger = logging.getLogger(__name__)


def init_phoenix():
    """
    Initialize Phoenix observability.
    
    This function:
    1. Registers Phoenix as the OpenTelemetry tracer provider
    2. Instruments LangChain to capture all LLM calls and chain executions
    
    Traces will show a tree structure of:
    - Each agent node execution (Router, Architect, Coder, etc.)
    - LLM calls with input/output, tokens, latency
    - Tool calls (database queries, etc.)
    """
    phoenix_enabled = os.getenv("PHOENIX_ENABLED", "true").lower() == "true"
    
    if not phoenix_enabled:
        logger.info("Phoenix observability is disabled")
        return
    
    try:
        from phoenix.otel import register
        from openinference.instrumentation.langchain import LangChainInstrumentor
        
        # Get Phoenix endpoint from environment
        phoenix_endpoint = os.getenv("PHOENIX_ENDPOINT", "http://localhost:6006")
        
        logger.info(f"Initializing Phoenix observability - Endpoint: {phoenix_endpoint}")
        
        # Register Phoenix as the tracer provider
        tracer_provider = register(
            project_name="antigravirt",
            endpoint=f"{phoenix_endpoint}/v1/traces"
        )
        
        # Instrument LangChain to capture all traces
        LangChainInstrumentor().instrument(tracer_provider=tracer_provider)
        
        logger.info("Phoenix observability initialized successfully")
        logger.info(f"View traces at: {phoenix_endpoint}")
        
    except ImportError as e:
        logger.warning(f"Phoenix packages not installed, skipping observability: {e}")
    except Exception as e:
        logger.error(f"Failed to initialize Phoenix observability: {e}")
