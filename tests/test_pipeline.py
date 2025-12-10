"""
test_pipeline.py
----------------
Unit tests for the pipeline module.

These tests verify the pipeline result handling and properties.
Integration tests that make actual API calls are in a separate file.

Run tests with: pytest tests/test_pipeline.py
"""

import pytest
from src.pipeline import PipelineResult
from src.judge import JudgeResult


def create_mock_judge_result(score: int, acceptable: bool = None) -> JudgeResult:
    """Helper to create a JudgeResult for testing."""
    if acceptable is None:
        acceptable = score >= 7
    
    return JudgeResult(
        overall_score=score,
        age_appropriateness=score,
        clarity=score,
        engagement=score,
        emotional_tone=score,
        story_structure=score,
        strengths="Test strengths.",
        improvements="Test improvements.",
        is_acceptable=acceptable
    )


class TestPipelineResult:
    """Tests for the PipelineResult dataclass."""
    
    def test_was_refined_true_when_rounds_greater_than_zero(self):
        """was_refined should be True if refinement_rounds > 0."""
        judge = create_mock_judge_result(8)
        
        result = PipelineResult(
            story="Test story",
            judge_result=judge,
            refinement_rounds=1,
            generation_history=[("Test story", judge)]
        )
        
        assert result.was_refined is True
    
    def test_was_refined_false_when_zero_rounds(self):
        """was_refined should be False if refinement_rounds == 0."""
        judge = create_mock_judge_result(8)
        
        result = PipelineResult(
            story="Test story",
            judge_result=judge,
            refinement_rounds=0,
            generation_history=[("Test story", judge)]
        )
        
        assert result.was_refined is False
    
    def test_met_quality_threshold_true_when_acceptable(self):
        """met_quality_threshold should reflect judge's is_acceptable."""
        judge = create_mock_judge_result(8, acceptable=True)
        
        result = PipelineResult(
            story="Test story",
            judge_result=judge,
            refinement_rounds=0,
            generation_history=[("Test story", judge)]
        )
        
        assert result.met_quality_threshold is True
    
    def test_met_quality_threshold_false_when_not_acceptable(self):
        """met_quality_threshold should be False when judge says not acceptable."""
        judge = create_mock_judge_result(5, acceptable=False)
        
        result = PipelineResult(
            story="Test story",
            judge_result=judge,
            refinement_rounds=2,
            generation_history=[("Test story", judge)]
        )
        
        assert result.met_quality_threshold is False
    
    def test_improvement_summary_no_refinement(self):
        """Summary should note when story passed on first try."""
        judge = create_mock_judge_result(8)
        
        result = PipelineResult(
            story="Test story",
            judge_result=judge,
            refinement_rounds=0,
            generation_history=[("Test story", judge)]
        )
        
        summary = result.get_improvement_summary()
        
        assert "first generation" in summary.lower()
    
    def test_improvement_summary_with_refinement(self):
        """Summary should show score improvement when refined."""
        initial_judge = create_mock_judge_result(5)
        final_judge = create_mock_judge_result(8)
        
        result = PipelineResult(
            story="Refined story",
            judge_result=final_judge,
            refinement_rounds=2,
            generation_history=[
                ("Initial story", initial_judge),
                ("Refined story", final_judge)
            ]
        )
        
        summary = result.get_improvement_summary()
        
        assert "refined" in summary.lower()
        assert "5/10" in summary or "Initial score: 5" in summary
        assert "8/10" in summary or "Final score: 8" in summary
    
    def test_improvement_summary_shows_improvement_delta(self):
        """Summary should show the improvement amount."""
        initial_judge = create_mock_judge_result(4)
        final_judge = create_mock_judge_result(7)
        
        result = PipelineResult(
            story="Refined story",
            judge_result=final_judge,
            refinement_rounds=1,
            generation_history=[
                ("Initial story", initial_judge),
                ("Refined story", final_judge)
            ]
        )
        
        summary = result.get_improvement_summary()
        
        # Should mention +3 improvement
        assert "+3" in summary


class TestPipelineResultHistory:
    """Tests for generation history tracking."""
    
    def test_history_preserves_all_versions(self):
        """Generation history should contain all story versions."""
        judge1 = create_mock_judge_result(4)
        judge2 = create_mock_judge_result(6)
        judge3 = create_mock_judge_result(8)
        
        result = PipelineResult(
            story="Final story",
            judge_result=judge3,
            refinement_rounds=2,
            generation_history=[
                ("First story", judge1),
                ("Second story", judge2),
                ("Final story", judge3)
            ]
        )
        
        assert len(result.generation_history) == 3
        assert result.generation_history[0][0] == "First story"
        assert result.generation_history[0][1].overall_score == 4
        assert result.generation_history[2][0] == "Final story"
        assert result.generation_history[2][1].overall_score == 8
