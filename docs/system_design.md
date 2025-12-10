# System Design Document

## Overview

This document describes the architecture and design of the Bedtime Story Generator, a system that creates age-appropriate bedtime stories for children aged 5-10 using GPT-3.5-turbo with an LLM-based quality judge for iterative improvement.

## Design Goals

1. Generate engaging, age-appropriate bedtime stories from simple user requests
2. Ensure consistent quality through automated LLM-based evaluation
3. Improve stories iteratively based on structured feedback
4. Provide a clean, maintainable codebase with clear separation of concerns
5. Create a system that can be extended with additional features

## System Architecture

### High-Level Flow

```
                                    BEDTIME STORY GENERATOR
                                    =======================

    +--------+         +-------------+         +-----------+         +--------+
    |  User  |  --->   |  Pipeline   |  --->   |   Story   |  --->   | Output |
    | Request|         | Orchestrator|         |  + Score  |         |        |
    +--------+         +-------------+         +-----------+         +--------+
                              |
                              |
              +---------------+---------------+
              |                               |
              v                               v
       +-------------+                 +-------------+
       | Storyteller |                 |    Judge    |
       |   Module    |                 |   Module    |
       +-------------+                 +-------------+
              |                               |
              +---------------+---------------+
                              |
                              v
                       +-------------+
                       |  LLM Client |
                       | (GPT-3.5)   |
                       +-------------+
```

### Component Diagram

```
    src/
     |
     +-- config.py          Configuration constants
     |
     +-- llm_client.py      OpenAI API wrapper
     |
     +-- storyteller.py     Story generation logic
     |
     +-- judge.py           Story evaluation logic
     |
     +-- pipeline.py        Orchestration and refinement loop
     |
    main.py                 CLI entry point
```

## Detailed Component Design

### 1. LLM Client (llm_client.py)

**Purpose**: Provides a clean interface for all OpenAI API interactions.

**Responsibilities**:
- API key validation
- Request formatting
- Error handling and clear error messages
- Consistent interface for both simple prompts and chat completions

**Key Functions**:
- `call_chat_model()`: Main function for chat-based interactions with system prompts
- `call_model()`: Backwards-compatible simple prompt interface

### 2. Storyteller Module (storyteller.py)

**Purpose**: Generates bedtime stories tailored for young children.

**Prompting Strategy**:

The storyteller uses a carefully crafted system prompt that establishes:
- Persona: Warm, experienced children's storyteller (like a kind grandparent)
- Audience awareness: Stories targeted at 5-10 year old children
- Content guidelines: What to include and avoid
- Structure requirements: Classic five-act story arc

**Story Arc Structure**:
```
    1. Opening     -->  Set cozy scene, introduce character
           |
    2. Adventure   -->  Present small challenge or discovery
           |
    3. Journey     -->  Character works through situation
           |
    4. Resolution  -->  Problem solved through kindness
           |
    5. Bedtime End -->  Calm, sleepy imagery
```

**Key Functions**:
- `generate_story()`: Creates initial story from user request
- `generate_refined_story()`: Improves story based on feedback

### 3. Judge Module (judge.py)

**Purpose**: Evaluates story quality across multiple dimensions.

**Evaluation Criteria**:

| Criterion | What It Measures | Weight |
|-----------|------------------|--------|
| Age Appropriateness | Vocabulary, concepts, themes | High |
| Clarity | Sentence structure, narrative flow | High |
| Engagement | Interest level, character appeal | Medium |
| Emotional Tone | Warmth, comfort, bedtime suitability | High |
| Story Structure | Pacing, arc, resolution | Medium |

**Scoring Guidelines**:
- 1-3: Significant problems, needs major work
- 4-5: Below average, several issues
- 6-7: Acceptable, minor improvements needed
- 8-9: Good to excellent
- 10: Exceptional, professional quality

**Output Structure**:
```
JudgeResult:
    - overall_score (1-10)
    - age_appropriateness (1-10)
    - clarity (1-10)
    - engagement (1-10)
    - emotional_tone (1-10)
    - story_structure (1-10)
    - strengths (text)
    - improvements (text)
```

### 4. Pipeline Module (pipeline.py)

**Purpose**: Orchestrates the generation and refinement loop.

**Pipeline Flow**:

```
                         START
                           |
                           v
                  +------------------+
                  | Generate Initial |
                  |      Story       |
                  +------------------+
                           |
                           v
                  +------------------+
                  |  Judge Evaluates |
                  |      Story       |
                  +------------------+
                           |
                           v
                   /---------------\
                  /  Score >= 7?    \
                  \  (threshold)    /
                   \---------------/
                    |            |
                   YES           NO
                    |            |
                    v            v
               +--------+   +-----------------+
               | Return |   | Rounds < Max?   |
               | Story  |   +-----------------+
               +--------+        |         |
                                YES        NO
                                 |         |
                                 v         v
                         +----------+  +--------+
                         | Refine   |  | Return |
                         | Story    |  | Best   |
                         +----------+  +--------+
                              |
                              |
                    (loop back to Judge)
```

**Key Configuration**:
- Quality threshold: 7/10 (stories scoring below this are refined)
- Maximum refinement rounds: 2 (balances quality vs API costs)
- Refinement uses judge feedback to guide improvements

### 5. Main CLI (main.py)

**Purpose**: Provides interactive user interface.

**User Flow**:
```
    1. Display welcome header
           |
    2. Prompt for story request
           |
    3. Generate story (with progress indication)
           |
    4. Display story
           |
    5. Display quality metrics
           |
    6. Offer feedback option  <--+
           |                     |
    7. If feedback provided -----+
           |
    8. Ask for another story
           |
    9. Loop or exit
```

## Prompting Strategies

### Storyteller System Prompt Design

The storyteller prompt employs several key techniques:

**1. Persona Establishment**
```
"You are a warm and experienced children's storyteller, 
similar to a kind grandparent who has told thousands of bedtime stories."
```
This creates a consistent voice and approach.

**2. Audience Specification**
```
"Your audience is children between 5 and 10 years old."
```
Grounds all decisions in the target audience.

**3. Positive Guidance (What TO Do)**
- Use simple vocabulary
- Keep sentences short and rhythmic
- Create vivid but gentle imagery
- Include sensory details
- Give characters relatable emotions

**4. Negative Guidance (What NOT To Do)**
- No violence or scary content
- No death or permanent loss
- No complex adult themes
- No moral ambiguity

**5. Structural Requirements**
The five-act story arc ensures narrative coherence.

### Judge System Prompt Design

**1. Expert Persona**
```
"You are an expert children's literature reviewer with 20 years of 
experience evaluating bedtime stories for young children."
```

**2. Detailed Rubric**
Each evaluation dimension includes:
- Definition of what's being measured
- Specific criteria for scoring
- Score anchors (what 1-3, 4-5, etc. mean)

**3. Output Format Enforcement**
```
"You MUST respond with valid JSON only, using exactly this structure..."
```
Strict formatting ensures reliable parsing.

## Error Handling

The system handles errors at multiple levels:

1. **API Key Validation**: Clear messages if key is missing or invalid
2. **API Errors**: Catches rate limits, auth failures, general API errors
3. **JSON Parsing**: Fallback parsing if judge output has formatting issues
4. **User Input**: Graceful handling of empty input, keyboard interrupts

## Configuration Management

All tunable parameters are centralized in `config.py`:

```python
OPENAI_MODEL = "gpt-3.5-turbo"    # Locked per requirements
STORY_TEMPERATURE = 0.7           # Creativity level
JUDGE_TEMPERATURE = 0.2           # Consistency level
QUALITY_THRESHOLD = 7             # Minimum acceptable score
MAX_REFINEMENT_ROUNDS = 2         # Cost/quality balance
```

## Extensibility

The modular design supports easy extension:

**Adding New Evaluation Criteria**:
1. Add field to JudgeResult dataclass
2. Add criteria description to judge system prompt
3. Update JSON schema in prompt
4. Add field validation in parse function

**Adding Story Categories**:
1. Create category detection function
2. Create category-specific system prompts
3. Route requests to appropriate prompt

**Adding Safety Filters**:
1. Create new safety_judge.py module
2. Add safety check step after quality judge
3. Block or flag inappropriate content

## Performance Considerations

**API Calls per Story**:
- Best case (first story is good): 2 calls (1 generate + 1 judge)
- Worst case (max refinement): 6 calls (1 generate + 2 judge + 2 refine + final judge)
- Average expected: 3-4 calls

**Token Usage**:
- Story generation: ~900 tokens max
- Judge response: ~500 tokens max
- Total per story: ~2000-4000 tokens depending on refinement

## Testing Strategy

The codebase supports testing at multiple levels:

1. **Unit Tests**: Test individual functions (parsing, validation)
2. **Integration Tests**: Test component interactions
3. **End-to-End Tests**: Full pipeline with mocked API

See `tests/` directory for test implementations.
