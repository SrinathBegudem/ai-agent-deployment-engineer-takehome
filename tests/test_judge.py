"""
test_judge.py
-------------
Unit tests for the judge module.

These tests verify the JSON parsing and validation logic without
making actual API calls. We use mock data to test edge cases.

Run tests with: pytest tests/test_judge.py
"""

import pytest
from src.judge import parse_judge_response, validate_judge_data, JudgeResult


class TestParseJudgeResponse:
    """Tests for the JSON parsing function."""
    
    def test_valid_json_parses_correctly(self):
        """Clean JSON should parse without issues."""
        raw = '''{
            "overall_score": 8,
            "age_appropriateness": 9,
            "clarity": 7,
            "engagement": 8,
            "emotional_tone": 9,
            "story_structure": 7,
            "strengths": "Good story.",
            "improvements": "Could be longer."
        }'''
        
        result = parse_judge_response(raw)
        
        assert result["overall_score"] == 8
        assert result["strengths"] == "Good story."
    
    def test_json_with_markdown_fences(self):
        """JSON wrapped in markdown code fences should parse."""
        raw = '''```json
        {
            "overall_score": 7,
            "age_appropriateness": 8,
            "clarity": 7,
            "engagement": 7,
            "emotional_tone": 8,
            "story_structure": 7,
            "strengths": "Nice tone.",
            "improvements": "Add more detail."
        }
        ```'''
        
        result = parse_judge_response(raw)
        
        assert result["overall_score"] == 7
    
    def test_json_with_leading_text(self):
        """JSON with extra text before it should still parse."""
        raw = '''Here is my evaluation:
        {
            "overall_score": 6,
            "age_appropriateness": 7,
            "clarity": 6,
            "engagement": 6,
            "emotional_tone": 7,
            "story_structure": 6,
            "strengths": "Basic structure.",
            "improvements": "Needs work."
        }'''
        
        result = parse_judge_response(raw)
        
        assert result["overall_score"] == 6
    
    def test_invalid_json_raises_error(self):
        """Completely invalid JSON should raise ValueError."""
        raw = "This is not JSON at all."
        
        with pytest.raises(ValueError) as exc_info:
            parse_judge_response(raw)
        
        assert "Could not parse" in str(exc_info.value)


class TestValidateJudgeData:
    """Tests for the validation function."""
    
    def test_valid_data_passes(self):
        """Complete valid data should not raise."""
        data = {
            "overall_score": 8,
            "age_appropriateness": 9,
            "clarity": 7,
            "engagement": 8,
            "emotional_tone": 9,
            "story_structure": 7,
            "strengths": "Good.",
            "improvements": "Minor issues."
        }
        
        # Should not raise
        validate_judge_data(data)
    
    def test_missing_field_raises_error(self):
        """Missing required field should raise ValueError."""
        data = {
            "overall_score": 8,
            "age_appropriateness": 9,
            # Missing "clarity"
            "engagement": 8,
            "emotional_tone": 9,
            "story_structure": 7,
            "strengths": "Good.",
            "improvements": "Minor issues."
        }
        
        with pytest.raises(ValueError) as exc_info:
            validate_judge_data(data)
        
        assert "clarity" in str(exc_info.value)
    
    def test_score_out_of_range_raises_error(self):
        """Score outside 1-10 should raise ValueError."""
        data = {
            "overall_score": 11,  # Invalid: > 10
            "age_appropriateness": 9,
            "clarity": 7,
            "engagement": 8,
            "emotional_tone": 9,
            "story_structure": 7,
            "strengths": "Good.",
            "improvements": "Minor issues."
        }
        
        with pytest.raises(ValueError) as exc_info:
            validate_judge_data(data)
        
        assert "overall_score" in str(exc_info.value)
    
    def test_zero_score_raises_error(self):
        """Score of 0 should raise ValueError (valid range is 1-10)."""
        data = {
            "overall_score": 0,  # Invalid: < 1
            "age_appropriateness": 9,
            "clarity": 7,
            "engagement": 8,
            "emotional_tone": 9,
            "story_structure": 7,
            "strengths": "Good.",
            "improvements": "Minor issues."
        }
        
        with pytest.raises(ValueError) as exc_info:
            validate_judge_data(data)
        
        assert "overall_score" in str(exc_info.value)


class TestJudgeResult:
    """Tests for the JudgeResult dataclass."""
    
    def test_str_representation(self):
        """String representation should be readable."""
        result = JudgeResult(
            overall_score=8,
            age_appropriateness=9,
            clarity=7,
            engagement=8,
            emotional_tone=9,
            story_structure=7,
            strengths="Good warm tone.",
            improvements="Could add more sensory details.",
            is_acceptable=True
        )
        
        output = str(result)
        
        assert "Overall Score: 8/10" in output
        assert "Good warm tone" in output
