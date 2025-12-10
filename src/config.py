"""
config.py
---------
Configuration constants for the bedtime story generator.

This module centralizes all configuration values used throughout the
application. Keeping configuration in one place makes it easy to tune
the system's behavior and understand the design choices.

Configuration Categories:
- Model settings: Which model to use (locked to gpt-3.5-turbo)
- Story generation: Temperature, token limits for storytelling
- Judge settings: Temperature, token limits for evaluation
- Pipeline settings: Quality thresholds, refinement limits
- Age range: Target audience parameters

Author: Srinath Begudem
"""

from typing import Tuple

# =============================================================================
# MODEL CONFIGURATION
# =============================================================================

# The OpenAI model to use. Per assignment requirements, this must remain
# gpt-3.5-turbo. Do not change this value.
OPENAI_MODEL: str = "gpt-3.5-turbo"


# =============================================================================
# STORY GENERATION SETTINGS
# =============================================================================

# Temperature for story generation (0.0 to 1.0)
# Higher values produce more creative/varied output
# 0.7 provides good creativity while maintaining coherence
STORY_TEMPERATURE: float = 0.7

# Maximum tokens for generated stories
# At ~1.3 tokens per word, 900 tokens allows stories of ~700 words
# This is appropriate for 3-5 minute bedtime story reading time
MAX_STORY_TOKENS: int = 900


# =============================================================================
# JUDGE SETTINGS
# =============================================================================

# Temperature for judge responses
# Lower temperature makes evaluation more consistent and deterministic
# 0.2 provides stable, reproducible judgments
JUDGE_TEMPERATURE: float = 0.2

# Maximum tokens for judge responses
# The JSON structure with all fields typically needs 200-400 tokens
# 500 provides headroom for detailed feedback
MAX_JUDGE_TOKENS: int = 500


# =============================================================================
# PIPELINE SETTINGS
# =============================================================================

# Minimum overall score (1-10) for a story to be considered acceptable
# Score of 7 represents "good enough" quality
# Stories below this threshold trigger refinement
QUALITY_THRESHOLD: int = 7

# Maximum number of refinement iterations
# Limiting to 2 rounds balances quality improvement with API costs
# Most stories that need improvement reach acceptable quality in 1-2 rounds
MAX_REFINEMENT_ROUNDS: int = 2


# =============================================================================
# TARGET AUDIENCE
# =============================================================================

# Default age range for story generation
# Stories are tailored for children in this age bracket
# (5, 10) covers kindergarten through early elementary school
DEFAULT_AGE_RANGE: Tuple[int, int] = (5, 10)


# =============================================================================
# DISPLAY SETTINGS
# =============================================================================

# Width for terminal output formatting
DISPLAY_WIDTH: int = 70

# Separator character for visual breaks
SEPARATOR_CHAR: str = "-"
