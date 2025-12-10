"""
storyteller.py
--------------
Core story generation module.

This module handles the creation of bedtime stories tailored for children
aged 5-10. It uses carefully crafted prompts that guide GPT-3.5-turbo to
produce age-appropriate, engaging, and comforting narratives.

The storytelling approach follows classic story arc principles:
1. Setup - Introduce characters and setting
2. Rising Action - Present a gentle challenge or adventure
3. Climax - The moment of resolution
4. Falling Action - Wind down the excitement
5. Resolution - Calm, reassuring ending suitable for bedtime

Author: Srinath Begudem
"""

from typing import Dict, List, Tuple, Optional
from src.llm_client import call_chat_model
from src.config import (
    STORY_TEMPERATURE,
    MAX_STORY_TOKENS,
    DEFAULT_AGE_RANGE,
)


# Story generation system prompt designed for bedtime storytelling
STORYTELLER_SYSTEM_PROMPT = """You are a warm and experienced children's storyteller, 
similar to a kind grandparent who has told thousands of bedtime stories.

Your audience is children between {min_age} and {max_age} years old.

Writing Guidelines:
- Use simple vocabulary that young children can understand
- Keep sentences short and rhythmic, easy to read aloud
- Create vivid but gentle imagery that sparks imagination
- Include sensory details (soft blankets, warm sunshine, gentle breezes)
- Give characters relatable emotions and clear motivations

Story Structure (follow this arc):
1. Opening: Set a cozy scene and introduce the main character
2. Adventure: Present a small challenge or exciting discovery
3. Journey: Show the character working through the situation
4. Resolution: Solve the problem in a satisfying, kind way
5. Bedtime Ending: Wind down with calm imagery, perfect for sleep

Content Rules:
- No violence, scary monsters, or threatening situations
- No death, serious illness, or permanent loss
- No complex adult themes or moral ambiguity
- Characters should be kind to each other
- Problems are solved through friendship, creativity, or kindness
- The world is fundamentally safe and good

Tone:
- Gentle and reassuring throughout
- Sprinkle in light humor appropriate for young children
- End on a peaceful, sleepy note

Write in flowing prose paragraphs. Do not use bullet points or headers in the story itself."""


def build_story_prompt(user_request: str, age_range: Tuple[int, int]) -> List[Dict[str, str]]:
    """
    Construct the message array for story generation.
    
    We use a system prompt to establish the storyteller persona and guidelines,
    then pass the user's request as the user message.
    
    Args:
        user_request: What kind of story the user wants
        age_range: Tuple of (min_age, max_age) for the target audience
        
    Returns:
        List of message dicts ready for the chat API
    """
    min_age, max_age = age_range
    
    system_content = STORYTELLER_SYSTEM_PROMPT.format(
        min_age=min_age,
        max_age=max_age
    )
    
    user_content = f"""Please write a bedtime story based on this request:

"{user_request}"

Remember to follow the story arc structure and end with calming imagery suitable for helping a child fall asleep."""
    
    return [
        {"role": "system", "content": system_content},
        {"role": "user", "content": user_content}
    ]


def generate_story(
    user_request: str,
    age_range: Tuple[int, int] = DEFAULT_AGE_RANGE
) -> str:
    """
    Generate an initial bedtime story based on the user's request.
    
    This function creates the first draft of the story. It may be refined
    later based on judge feedback through the refinement pipeline.
    
    Args:
        user_request: Description of what story the user wants
        age_range: Target age range, defaults to (5, 10)
        
    Returns:
        The generated story as a string
        
    Example:
        >>> story = generate_story("A story about a brave little mouse")
        >>> print(story[:50])
        'Once upon a time, in a cozy little hole beneath...'
    """
    messages = build_story_prompt(user_request, age_range)
    
    story = call_chat_model(
        messages=messages,
        max_tokens=MAX_STORY_TOKENS,
        temperature=STORY_TEMPERATURE
    )
    
    return story.strip()


def generate_refined_story(
    user_request: str,
    previous_story: str,
    feedback: str,
    age_range: Tuple[int, int] = DEFAULT_AGE_RANGE
) -> str:
    """
    Generate an improved version of a story based on judge feedback.
    
    This is called when the initial story didn't meet quality thresholds.
    The storyteller receives the original story and specific improvement
    suggestions from the judge.
    
    Args:
        user_request: Original user request for context
        previous_story: The story that needs improvement
        feedback: Specific suggestions from the judge
        age_range: Target age range
        
    Returns:
        An improved version of the story
    """
    min_age, max_age = age_range
    
    system_content = STORYTELLER_SYSTEM_PROMPT.format(
        min_age=min_age,
        max_age=max_age
    )
    
    user_content = f"""I previously wrote this bedtime story based on the request: "{user_request}"

Here is the story I wrote:

---
{previous_story}
---

A reviewer provided this feedback for improvement:

{feedback}

Please rewrite the story incorporating this feedback. Keep everything that was working well, but address the specific issues mentioned. The story should still follow proper story arc structure and end peacefully.

Output only the improved story, no explanations."""

    messages = [
        {"role": "system", "content": system_content},
        {"role": "user", "content": user_content}
    ]
    
    refined_story = call_chat_model(
        messages=messages,
        max_tokens=MAX_STORY_TOKENS,
        temperature=STORY_TEMPERATURE
    )
    
    return refined_story.strip()
