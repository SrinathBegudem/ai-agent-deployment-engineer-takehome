"""
judge.py
--------
LLM-based story evaluation module.

This module implements a judge that assesses bedtime stories across multiple
quality dimensions. The judge provides both numerical scores and actionable
feedback for story improvement.

The judge evaluates stories on five key dimensions:
1. Age Appropriateness - Is the content suitable for 5-10 year olds?
2. Clarity - Is the language clear and easy to follow?
3. Engagement - Will children find the story interesting?
4. Emotional Tone - Is the mood appropriate for bedtime?
5. Story Structure - Does it follow a proper narrative arc?

The judge is designed to be strict but fair, providing specific and
constructive feedback rather than vague criticisms.

Author: Srinath Begudem
"""

import json
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
from src.llm_client import call_chat_model
from src.config import (
    JUDGE_TEMPERATURE,
    MAX_JUDGE_TOKENS,
    DEFAULT_AGE_RANGE,
)


@dataclass
class JudgeResult:
    """
    Structured result from the story judge.
    
    Attributes:
        overall_score: Weighted average score from 1-10
        age_appropriateness: How suitable for the target age range (1-10)
        clarity: How clear and understandable the language is (1-10)
        engagement: How interesting and captivating the story is (1-10)
        emotional_tone: How appropriate the mood is for bedtime (1-10)
        story_structure: How well the narrative arc is executed (1-10)
        strengths: What the story does well
        improvements: Specific actionable feedback for improvement
        is_acceptable: Whether the story meets minimum quality threshold
    """
    overall_score: int
    age_appropriateness: int
    clarity: int
    engagement: int
    emotional_tone: int
    story_structure: int
    strengths: str
    improvements: str
    is_acceptable: bool
    
    def __str__(self) -> str:
        """Human-readable summary of the judge result."""
        return f"""Story Evaluation Summary
------------------------
Overall Score: {self.overall_score}/10
Age Appropriateness: {self.age_appropriateness}/10
Clarity: {self.clarity}/10
Engagement: {self.engagement}/10
Emotional Tone: {self.emotional_tone}/10
Story Structure: {self.story_structure}/10

Strengths: {self.strengths}

Areas for Improvement: {self.improvements}"""


# Judge system prompt - instructs the model how to evaluate stories
JUDGE_SYSTEM_PROMPT = """You are an expert children's literature reviewer with 20 years of 
experience evaluating bedtime stories for young children.

You are reviewing stories for children aged {min_age} to {max_age} years old.

Evaluation Criteria:

1. AGE APPROPRIATENESS (1-10)
   - Vocabulary matches reading/listening level
   - Concepts are understandable for the age group
   - No content that would frighten or confuse young children
   - Themes are relatable to children's experiences

2. CLARITY (1-10)
   - Sentences are not overly complex
   - Story events are easy to follow
   - Character motivations are clear
   - No confusing jumps or gaps in the narrative

3. ENGAGEMENT (1-10)
   - Opening hooks the listener's attention
   - Story maintains interest throughout
   - Characters are likeable and relatable
   - There is appropriate mild tension/adventure

4. EMOTIONAL TONE (1-10)
   - Overall mood is warm and comforting
   - Any tension is resolved reassuringly
   - The ending promotes calm and sleepiness
   - No lingering anxiety or unresolved worry

5. STORY STRUCTURE (1-10)
   - Clear beginning, middle, and end
   - Proper pacing (not rushed, not dragging)
   - Satisfying resolution
   - Smooth transitions between story beats

Scoring Guidelines:
- 1-3: Significant problems, needs major revision
- 4-5: Below average, several issues to address
- 6-7: Acceptable, minor improvements needed
- 8-9: Good to excellent quality
- 10: Exceptional, professional quality

Be strict but fair. Reserve scores of 9-10 for truly excellent work.

You MUST respond with valid JSON only, using exactly this structure:

{{
    "overall_score": <integer 1-10>,
    "age_appropriateness": <integer 1-10>,
    "clarity": <integer 1-10>,
    "engagement": <integer 1-10>,
    "emotional_tone": <integer 1-10>,
    "story_structure": <integer 1-10>,
    "strengths": "<2-3 sentences about what works well>",
    "improvements": "<specific actionable feedback for improvement>"
}}

Output ONLY the JSON object. No additional text, explanations, or markdown."""


def build_judge_prompt(
    user_request: str,
    story: str,
    age_range: Tuple[int, int]
) -> List[Dict[str, str]]:
    """
    Construct the message array for story evaluation.
    
    Args:
        user_request: Original story request for context
        story: The story to evaluate
        age_range: Target age range
        
    Returns:
        List of message dicts ready for the chat API
    """
    min_age, max_age = age_range
    
    system_content = JUDGE_SYSTEM_PROMPT.format(
        min_age=min_age,
        max_age=max_age
    )
    
    user_content = f"""Please evaluate this bedtime story.

ORIGINAL REQUEST: "{user_request}"

STORY TO EVALUATE:
---
{story}
---

Provide your evaluation as a JSON object following the exact schema specified."""

    return [
        {"role": "system", "content": system_content},
        {"role": "user", "content": user_content}
    ]


def parse_judge_response(raw_response: str) -> Dict:
    """
    Parse the judge's JSON response with error handling.
    
    The LLM sometimes includes markdown code fences or extra text.
    This function attempts to extract valid JSON from the response.
    
    Args:
        raw_response: Raw text response from the judge LLM
        
    Returns:
        Parsed dictionary from the JSON
        
    Raises:
        ValueError: If the response cannot be parsed as valid JSON
    """
    # Clean up common issues
    cleaned = raw_response.strip()
    
    # Remove markdown code fences if present
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    if cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    
    cleaned = cleaned.strip()
    
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        # Try to find JSON object within the text
        start_idx = cleaned.find("{")
        end_idx = cleaned.rfind("}") + 1
        
        if start_idx != -1 and end_idx > start_idx:
            try:
                return json.loads(cleaned[start_idx:end_idx])
            except json.JSONDecodeError:
                pass
        
        raise ValueError(
            f"Could not parse judge response as JSON. "
            f"Parse error: {e}. Raw response:\n{raw_response}"
        )


def validate_judge_data(data: Dict) -> None:
    """
    Validate that the parsed judge response has all required fields.
    
    Args:
        data: Parsed dictionary from judge response
        
    Raises:
        ValueError: If required fields are missing or invalid
    """
    required_fields = [
        "overall_score",
        "age_appropriateness",
        "clarity",
        "engagement",
        "emotional_tone",
        "story_structure",
        "strengths",
        "improvements"
    ]
    
    for field in required_fields:
        if field not in data:
            raise ValueError(f"Judge response missing required field: {field}")
    
    # Validate score ranges
    score_fields = [
        "overall_score",
        "age_appropriateness",
        "clarity",
        "engagement",
        "emotional_tone",
        "story_structure"
    ]
    
    for field in score_fields:
        score = data[field]
        if not isinstance(score, int) or score < 1 or score > 10:
            raise ValueError(
                f"Invalid score for {field}: {score}. Must be integer 1-10."
            )


def judge_story(
    user_request: str,
    story: str,
    age_range: Tuple[int, int] = DEFAULT_AGE_RANGE,
    quality_threshold: int = 7
) -> JudgeResult:
    """
    Evaluate a bedtime story using the LLM judge.
    
    This function sends the story to GPT-3.5-turbo configured as a strict
    but fair children's literature reviewer. The judge provides scores
    across multiple dimensions and specific feedback for improvement.
    
    Args:
        user_request: Original story request for context
        story: The story to evaluate
        age_range: Target age range, defaults to (5, 10)
        quality_threshold: Minimum overall score to be considered acceptable
        
    Returns:
        JudgeResult containing scores and feedback
        
    Raises:
        ValueError: If the judge response cannot be parsed
    """
    messages = build_judge_prompt(user_request, story, age_range)
    
    raw_response = call_chat_model(
        messages=messages,
        max_tokens=MAX_JUDGE_TOKENS,
        temperature=JUDGE_TEMPERATURE
    )
    
    # Parse and validate the response
    data = parse_judge_response(raw_response)
    validate_judge_data(data)
    
    # Determine if story meets quality threshold
    is_acceptable = data["overall_score"] >= quality_threshold
    
    return JudgeResult(
        overall_score=int(data["overall_score"]),
        age_appropriateness=int(data["age_appropriateness"]),
        clarity=int(data["clarity"]),
        engagement=int(data["engagement"]),
        emotional_tone=int(data["emotional_tone"]),
        story_structure=int(data["story_structure"]),
        strengths=str(data["strengths"]),
        improvements=str(data["improvements"]),
        is_acceptable=is_acceptable
    )
