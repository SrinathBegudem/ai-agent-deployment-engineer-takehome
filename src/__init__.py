"""
Bedtime Story Generator
-----------------------

A story generation system that creates age-appropriate bedtime stories
for children aged 5-10, using GPT-3.5-turbo with an LLM judge for
quality assurance.

Main Components:
    - storyteller: Generates bedtime stories from user requests
    - judge: Evaluates stories on multiple quality dimensions
    - pipeline: Orchestrates generation and refinement
    - llm_client: Handles OpenAI API communication
    - config: Centralized configuration

Usage:
    from src.pipeline import run_pipeline
    
    result = run_pipeline("A story about a brave little mouse")
    print(result.story)
"""

from src.pipeline import run_pipeline, generate_with_feedback, PipelineResult
from src.storyteller import generate_story
from src.judge import judge_story, JudgeResult
from src.llm_client import call_model, call_chat_model
from src.config import DEFAULT_AGE_RANGE, QUALITY_THRESHOLD

__version__ = "1.0.0"
__author__ = "Srinath Begudem"

__all__ = [
    "run_pipeline",
    "generate_with_feedback",
    "PipelineResult",
    "generate_story",
    "judge_story",
    "JudgeResult",
    "call_model",
    "call_chat_model",
    "DEFAULT_AGE_RANGE",
    "QUALITY_THRESHOLD",
]
