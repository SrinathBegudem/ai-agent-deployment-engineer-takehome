# Architecture Documentation

## Component Overview

This document provides a detailed look at each component in the Bedtime Story Generator system and how they interact.

## Module Dependency Graph

```
                    main.py
                       |
                       v
                  pipeline.py
                   /       \
                  v         v
          storyteller.py  judge.py
                  \         /
                   \       /
                    v     v
                 llm_client.py
                       |
                       v
                  config.py
```

## Data Flow

### Request to Story Flow

```
User Request: "A story about a brave little mouse"
                    |
                    v
            +---------------+
            |   main.py     |
            | Validates     |
            | input         |
            +---------------+
                    |
                    v
            +---------------+
            | pipeline.py   |
            | run_pipeline()|
            +---------------+
                    |
                    v
            +------------------+
            | storyteller.py   |
            | generate_story() |
            +------------------+
                    |
                    v
            +------------------+
            | llm_client.py    |
            | call_chat_model()|
            +------------------+
                    |
                    v
            +------------------+
            | OpenAI API       |
            | gpt-3.5-turbo    |
            +------------------+
                    |
                    v
            Story Text (700+ words)
```

### Evaluation Flow

```
Generated Story
       |
       v
+---------------+
| judge.py      |
| judge_story() |
+---------------+
       |
       v
+---------------+
| llm_client.py |
+---------------+
       |
       v
+---------------+
| OpenAI API    |
+---------------+
       |
       v
JSON Response
       |
       v
+-------------------+
| parse_judge_json()|
+-------------------+
       |
       v
JudgeResult Object
```

### Refinement Loop

```
                 +---> Generate Story
                 |            |
                 |            v
                 |      Judge Story
                 |            |
                 |            v
                 |      Score < 7?
                 |       /      \
                 |     YES       NO
                 |      |         \
                 |      v          v
                 +-- Refine    Return Story
                    Story
```

## Key Data Structures

### JudgeResult

```
JudgeResult
    |
    +-- overall_score: int (1-10)
    |
    +-- age_appropriateness: int (1-10)
    |
    +-- clarity: int (1-10)
    |
    +-- engagement: int (1-10)
    |
    +-- emotional_tone: int (1-10)
    |
    +-- story_structure: int (1-10)
    |
    +-- strengths: str
    |
    +-- improvements: str
    |
    +-- is_acceptable: bool
```

### PipelineResult

```
PipelineResult
    |
    +-- story: str (final story text)
    |
    +-- judge_result: JudgeResult
    |
    +-- refinement_rounds: int
    |
    +-- generation_history: List[(story, JudgeResult)]
```

## Message Format for LLM Calls

### Story Generation Messages

```
[
    {
        "role": "system",
        "content": "<storyteller persona and guidelines>"
    },
    {
        "role": "user", 
        "content": "Please write a bedtime story based on: <user_request>"
    }
]
```

### Judge Evaluation Messages

```
[
    {
        "role": "system",
        "content": "<judge persona and rubric>"
    },
    {
        "role": "user",
        "content": "ORIGINAL REQUEST: <request>\n\nSTORY TO EVALUATE:\n<story>"
    }
]
```

### Refinement Messages

```
[
    {
        "role": "system",
        "content": "<storyteller persona and guidelines>"
    },
    {
        "role": "user",
        "content": "I previously wrote: <story>\n\nFeedback: <improvements>\n\nPlease rewrite..."
    }
]
```

## Temperature Settings Rationale

### Story Generation: 0.7

Higher temperature for creativity:
- Produces varied and imaginative content
- Avoids repetitive patterns
- Allows for surprising story elements
- Still coherent at 0.7 level

### Judge Evaluation: 0.2

Lower temperature for consistency:
- Reproducible evaluations
- Reliable JSON formatting
- Consistent scoring standards
- Focused, objective feedback

## Token Budget Allocation

```
Total Available per Call: ~4096 tokens

Story Generation:
    System Prompt:  ~500 tokens
    User Prompt:    ~100 tokens
    Response:       ~900 tokens max
    Safety Buffer:  ~2500 tokens

Judge Evaluation:
    System Prompt:  ~800 tokens
    User Prompt:    ~1000 tokens (includes story)
    Response:       ~500 tokens max
    Safety Buffer:  ~1800 tokens
```

## Error Recovery Strategies

### JSON Parse Failures

```
Raw Response from Judge
         |
         v
    Try: json.loads()
         |
    FAIL |
         v
    Strip markdown fences
         |
         v
    Try: json.loads() again
         |
    FAIL |
         v
    Find { } boundaries
         |
         v
    Try: parse substring
         |
    FAIL |
         v
    Raise ValueError with details
```

### API Error Handling

```
API Call
    |
    +-- AuthenticationError --> "Check API key"
    |
    +-- RateLimitError ------> "Wait and retry"
    |
    +-- APIError ------------> "OpenAI service issue"
    |
    +-- Other ---------------> "Unexpected error"
```

## Extensibility Points

### Adding a New Evaluation Dimension

1. Update `JudgeResult` dataclass:
```python
@dataclass
class JudgeResult:
    # ... existing fields ...
    new_dimension: int  # Add new field
```

2. Update judge system prompt with new criteria

3. Update JSON schema in prompt

4. Update validation in `validate_judge_data()`

### Adding Story Categories

1. Create category detection:
```python
def detect_category(request: str) -> str:
    # Analyze request and return category
    pass
```

2. Create category-specific prompts:
```python
ADVENTURE_PROMPT = "..."
ANIMAL_PROMPT = "..."
FRIENDSHIP_PROMPT = "..."
```

3. Route in storyteller:
```python
def generate_story(request, ...):
    category = detect_category(request)
    prompt = CATEGORY_PROMPTS[category]
    # ...
```

### Adding User Feedback Loop

The pipeline already supports this through `generate_with_feedback()`:

```python
result = generate_with_feedback(
    user_request="...",
    user_feedback="Make it funnier",
    previous_story=result.story
)
```

## Scaling Considerations

### For Higher Volume

1. Add caching for similar requests
2. Implement request queuing
3. Add multiple API key rotation
4. Consider async/await for concurrent requests

### For Production Deployment

1. Add structured logging
2. Implement metrics collection
3. Add rate limiting
4. Set up monitoring and alerting
5. Consider model output caching

## Security Notes

1. API key stored in environment variable, not in code
2. API key excluded via .gitignore
3. No user data persistence (stateless design)
4. Input sanitization through prompt structure
