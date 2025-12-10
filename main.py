"""
main.py
-------
Bedtime Story Generator - Main Entry Point

This script provides an interactive command-line interface for generating
bedtime stories. It demonstrates the full capability of the storytelling
pipeline including story generation, LLM-based quality evaluation, and
iterative refinement.

Author: Srinath Begudem

-------------------------------------------------------------------------------
WHAT I WOULD BUILD NEXT (2 MORE HOURS):

1. Web Interface: Build a simple Streamlit or Gradio interface so non-technical
   users (parents, teachers) can generate stories through a browser. Would 
   include story history, favorites, and easy sharing options.

2. Story Categories: Add automatic categorization of user requests (adventure,
   animal stories, friendship tales, etc.) with specialized prompts for each
   category to improve story quality and variety.

3. Personalization Memory: Store child's name, favorite characters, and 
   preferences across sessions. This would let the system generate stories
   featuring "your child" and reference their interests.

4. Safety Filter: Add a dedicated content safety judge that runs after the
   quality judge to double-check for any inappropriate content before 
   presenting the final story to the user.

5. Audio Generation: Integrate with a text-to-speech API to generate audio
   versions of stories with calm, soothing narration suitable for bedtime.
-------------------------------------------------------------------------------
"""

import os
import sys
from pathlib import Path

# Load environment variables FIRST, before any other imports
from dotenv import load_dotenv

# Get the directory where main.py is located
BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / '.env'

# Load .env with explicit path and override
load_dotenv(dotenv_path=ENV_PATH, override=True)

# Now import project modules
from src.pipeline import run_pipeline, generate_with_feedback
from src.config import DEFAULT_AGE_RANGE, DISPLAY_WIDTH, SEPARATOR_CHAR


def print_header() -> None:
    """Print the application header."""
    print()
    print(SEPARATOR_CHAR * DISPLAY_WIDTH)
    print("BEDTIME STORY GENERATOR".center(DISPLAY_WIDTH))
    print("Stories for children ages 5-10".center(DISPLAY_WIDTH))
    print(SEPARATOR_CHAR * DISPLAY_WIDTH)
    print()


def print_separator() -> None:
    """Print a visual separator line."""
    print(SEPARATOR_CHAR * DISPLAY_WIDTH)


def get_story_request() -> str:
    """
    Prompt the user for their story request.
    
    Returns:
        The user's story request string, or empty if they want to quit
    """
    print("What kind of bedtime story would you like?")
    print("(Examples: 'A story about a friendly dragon', 'A tale about a")
    print(" little star who wanted to explore', 'An adventure with a brave bunny')")
    print()
    
    try:
        request = input("Your story idea: ").strip()
        return request
    except (KeyboardInterrupt, EOFError):
        print("\n")
        return ""


def display_story(story: str) -> None:
    """
    Display the generated story with nice formatting.
    
    Args:
        story: The story text to display
    """
    print()
    print_separator()
    print("YOUR BEDTIME STORY".center(DISPLAY_WIDTH))
    print_separator()
    print()
    print(story)
    print()


def display_quality_report(result) -> None:
    """
    Display the quality evaluation summary.
    
    Args:
        result: PipelineResult containing judge evaluation
    """
    judge = result.judge_result
    
    print_separator()
    print("STORY QUALITY REPORT".center(DISPLAY_WIDTH))
    print_separator()
    print()
    print(f"Overall Score:        {judge.overall_score}/10")
    print(f"Age Appropriateness:  {judge.age_appropriateness}/10")
    print(f"Clarity:              {judge.clarity}/10")
    print(f"Engagement:           {judge.engagement}/10")
    print(f"Emotional Tone:       {judge.emotional_tone}/10")
    print(f"Story Structure:      {judge.story_structure}/10")
    print()
    print(f"Refinement Rounds:    {result.refinement_rounds}")
    print()
    
    if judge.strengths:
        print("Strengths:")
        print(f"  {judge.strengths}")
        print()


def ask_for_feedback() -> str:
    """
    Ask the user if they want to provide feedback for story refinement.
    
    Returns:
        User's feedback string, or empty if no feedback
    """
    print("Would you like to request any changes to the story?")
    print("(Press Enter to skip, or type your feedback)")
    print()
    
    try:
        feedback = input("Your feedback: ").strip()
        return feedback
    except (KeyboardInterrupt, EOFError):
        print("\n")
        return ""


def ask_for_another() -> bool:
    """
    Ask if the user wants to generate another story.
    
    Returns:
        True if user wants another story, False otherwise
    """
    print()
    try:
        response = input("Generate another story? (y/n): ").strip().lower()
        return response in ("y", "yes")
    except (KeyboardInterrupt, EOFError):
        return False


def main() -> None:
    """
    Main application entry point.
    
    Runs the interactive story generation loop:
    1. Get story request from user
    2. Generate story with quality evaluation
    3. Display story and quality report
    4. Optionally collect user feedback for refinement
    5. Repeat for additional feedback or new stories
    """
    print_header()
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable is not set.")
        print()
        print("Please set your OpenAI API key using one of these methods:")
        print()
        print("  Method 1 - Create .env file:")
        print("    echo 'OPENAI_API_KEY=your-key-here' > .env")
        print()
        print("  Method 2 - Export in terminal:")
        print("    export OPENAI_API_KEY='your-key-here'")
        print()
        sys.exit(1)
    
    while True:
        # Get story request
        user_request = get_story_request()
        
        if not user_request:
            print("No story request provided. Goodbye!")
            break
        
        print()
        print("Generating your bedtime story...")
        print("(This may take a moment as we ensure quality)")
        print()
        
        try:
            # Run the generation pipeline
            result = run_pipeline(
                user_request=user_request,
                age_range=DEFAULT_AGE_RANGE,
                verbose=False
            )
            
            # Display the story
            display_story(result.story)
            
            # Show quality metrics
            display_quality_report(result)
            
            # Feedback loop
            current_story = result.story
            while True:
                feedback = ask_for_feedback()
                
                if not feedback:
                    break
                
                print()
                print("Refining story based on your feedback...")
                print()
                
                # Generate refined version with user feedback
                result = generate_with_feedback(
                    user_request=user_request,
                    user_feedback=feedback,
                    previous_story=current_story,
                    age_range=DEFAULT_AGE_RANGE
                )
                
                current_story = result.story
                display_story(result.story)
                display_quality_report(result)
        
        except Exception as e:
            print(f"\nError generating story: {e}")
            print("Please try again with a different request.")
        
        # Ask about another story
        if not ask_for_another():
            print()
            print("Sweet dreams! Goodbye.")
            break
        
        print()
        print_separator()
        print()


if __name__ == "__main__":
    main()
