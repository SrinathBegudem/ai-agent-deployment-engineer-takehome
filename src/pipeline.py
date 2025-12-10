"""
pipeline.py
-----------
Story generation pipeline with iterative refinement.

This module orchestrates the interaction between the storyteller and judge
components. It implements a feedback loop where stories are generated,
evaluated, and refined until they meet quality standards.

Pipeline Flow:
1. Generate initial story from user request
2. Judge evaluates the story
3. If quality threshold met, return the story
4. Otherwise, refine the story using judge feedback
5. Repeat evaluation/refinement up to max iterations
6. Return the best version produced

This architecture allows us to leverage the creativity of higher temperature
story generation while maintaining quality through structured evaluation.

Author: Srinath Begudem
"""

from dataclasses import dataclass
from typing import Tuple, List, Optional
from src.storyteller import generate_story, generate_refined_story
from src.judge import judge_story, JudgeResult
from src.config import (
    DEFAULT_AGE_RANGE,
    QUALITY_THRESHOLD,
    MAX_REFINEMENT_ROUNDS,
)


@dataclass
class PipelineResult:
    """
    Complete result from the story generation pipeline.
    
    Contains the final story, evaluation results, and metadata about
    the generation process.
    
    Attributes:
        story: The final story text
        judge_result: Evaluation scores and feedback for the final story
        refinement_rounds: How many refinement iterations were performed
        generation_history: List of (story, judge_result) tuples showing progression
    """
    story: str
    judge_result: JudgeResult
    refinement_rounds: int
    generation_history: List[Tuple[str, JudgeResult]]
    
    @property
    def was_refined(self) -> bool:
        """Returns True if the story went through any refinement."""
        return self.refinement_rounds > 0
    
    @property
    def met_quality_threshold(self) -> bool:
        """Returns True if the final story met quality standards."""
        return self.judge_result.is_acceptable
    
    def get_improvement_summary(self) -> str:
        """
        Generate a summary of how the story improved through refinement.
        
        Returns:
            Human-readable summary of the refinement process
        """
        if not self.was_refined:
            return "Story met quality standards on first generation."
        
        initial_score = self.generation_history[0][1].overall_score
        final_score = self.judge_result.overall_score
        improvement = final_score - initial_score
        
        summary_parts = [
            f"Story was refined {self.refinement_rounds} time(s).",
            f"Initial score: {initial_score}/10",
            f"Final score: {final_score}/10",
        ]
        
        if improvement > 0:
            summary_parts.append(f"Improvement: +{improvement} points")
        elif improvement < 0:
            summary_parts.append(f"Score change: {improvement} points")
        else:
            summary_parts.append("Score maintained through refinement")
            
        return "\n".join(summary_parts)


def run_pipeline(
    user_request: str,
    age_range: Tuple[int, int] = DEFAULT_AGE_RANGE,
    quality_threshold: int = QUALITY_THRESHOLD,
    max_rounds: int = MAX_REFINEMENT_ROUNDS,
    verbose: bool = False
) -> PipelineResult:
    """
    Execute the full story generation pipeline.
    
    This is the main entry point for story generation. It handles the
    complete flow from user request to polished final story.
    
    The pipeline works as follows:
    1. Generate an initial story using the storyteller
    2. Have the judge evaluate the story
    3. If the story meets quality threshold, we're done
    4. Otherwise, send the story and feedback back to the storyteller
    5. The storyteller produces an improved version
    6. Repeat until quality threshold is met or max rounds exhausted
    
    Args:
        user_request: Description of the desired story
        age_range: Target age range for the audience
        quality_threshold: Minimum overall score to accept (1-10)
        max_rounds: Maximum refinement iterations allowed
        verbose: If True, print progress information
        
    Returns:
        PipelineResult containing the final story and all metadata
        
    Example:
        >>> result = run_pipeline("A story about a friendly dragon")
        >>> print(result.story[:100])
        'Once upon a time, in a valley filled with flowers...'
        >>> print(result.judge_result.overall_score)
        8
    """
    generation_history: List[Tuple[str, JudgeResult]] = []
    
    if verbose:
        print("Generating initial story...")
    
    # Step 1: Generate initial story
    current_story = generate_story(user_request, age_range)
    
    if verbose:
        print("Evaluating story...")
    
    # Step 2: Initial evaluation
    current_judgment = judge_story(
        user_request=user_request,
        story=current_story,
        age_range=age_range,
        quality_threshold=quality_threshold
    )
    
    generation_history.append((current_story, current_judgment))
    
    if verbose:
        print(f"Initial score: {current_judgment.overall_score}/10")
    
    # Step 3: Refinement loop
    rounds_completed = 0
    
    while not current_judgment.is_acceptable and rounds_completed < max_rounds:
        rounds_completed += 1
        
        if verbose:
            print(f"\nRefinement round {rounds_completed}...")
            print(f"Feedback: {current_judgment.improvements}")
        
        # Generate refined story using judge feedback
        current_story = generate_refined_story(
            user_request=user_request,
            previous_story=current_story,
            feedback=current_judgment.improvements,
            age_range=age_range
        )
        
        if verbose:
            print("Re-evaluating refined story...")
        
        # Evaluate the refined story
        current_judgment = judge_story(
            user_request=user_request,
            story=current_story,
            age_range=age_range,
            quality_threshold=quality_threshold
        )
        
        generation_history.append((current_story, current_judgment))
        
        if verbose:
            print(f"New score: {current_judgment.overall_score}/10")
    
    if verbose:
        if current_judgment.is_acceptable:
            print("\nStory meets quality threshold!")
        else:
            print(f"\nMax refinement rounds ({max_rounds}) reached.")
    
    return PipelineResult(
        story=current_story,
        judge_result=current_judgment,
        refinement_rounds=rounds_completed,
        generation_history=generation_history
    )


def generate_with_feedback(
    user_request: str,
    user_feedback: Optional[str] = None,
    previous_story: Optional[str] = None,
    age_range: Tuple[int, int] = DEFAULT_AGE_RANGE
) -> PipelineResult:
    """
    Generate a story incorporating optional user feedback.
    
    This function allows users to provide their own feedback on a story,
    enabling an interactive refinement process beyond the automated judge.
    
    Args:
        user_request: Original story request
        user_feedback: Optional user-provided feedback for improvement
        previous_story: Optional previous version to improve upon
        age_range: Target age range
        
    Returns:
        PipelineResult with the generated/refined story
    """
    if user_feedback and previous_story:
        # User is providing feedback on a previous story
        refined_story = generate_refined_story(
            user_request=user_request,
            previous_story=previous_story,
            feedback=user_feedback,
            age_range=age_range
        )
        
        judge_result = judge_story(
            user_request=user_request,
            story=refined_story,
            age_range=age_range
        )
        
        return PipelineResult(
            story=refined_story,
            judge_result=judge_result,
            refinement_rounds=1,
            generation_history=[(refined_story, judge_result)]
        )
    else:
        # No user feedback, run normal pipeline
        return run_pipeline(user_request, age_range)
