# Prompting Strategy Documentation

## Overview

This document explains the prompting strategies used in the Bedtime Story Generator. Good prompts are the foundation of good LLM outputs, and significant effort went into crafting prompts that produce consistent, high-quality results.

## Core Prompting Principles

### 1. Persona Establishment

We give the LLM a clear identity to adopt. This creates consistency and appropriate tone.

**Storyteller Persona:**
```
"You are a warm and experienced children's storyteller, 
similar to a kind grandparent who has told thousands of bedtime stories."
```

**Why it works:**
- "Warm" sets the emotional tone
- "Experienced" implies competence
- "Kind grandparent" is a relatable archetype
- "Thousands of bedtime stories" suggests expertise

**Judge Persona:**
```
"You are an expert children's literature reviewer with 20 years of 
experience evaluating bedtime stories for young children."
```

**Why it works:**
- "Expert" establishes authority
- "20 years" implies deep knowledge
- "Children's literature" focuses the domain
- "Young children" specifies the audience

### 2. Audience Specification

Both prompts explicitly state the target audience:

```
"Your audience is children between 5 and 10 years old."
```

**Why this matters:**
- Vocabulary choices are calibrated to reading level
- Concepts are simplified appropriately
- Themes remain relatable to children
- Length and complexity are adjusted

### 3. Positive Guidance (Do's)

We tell the LLM what TO do, not just what to avoid. This is more effective than purely negative constraints.

**Storyteller Do's:**
```
- Use simple vocabulary that young children can understand
- Keep sentences short and rhythmic, easy to read aloud
- Create vivid but gentle imagery that sparks imagination
- Include sensory details (soft blankets, warm sunshine, gentle breezes)
- Give characters relatable emotions and clear motivations
```

**Why this approach:**
- Specific, actionable guidance
- Sensory details add quality without complexity
- "Rhythmic" encourages read-aloud quality
- Examples make abstract guidance concrete

### 4. Negative Constraints (Don'ts)

We also specify what to avoid, with specific examples:

**Storyteller Don'ts:**
```
- No violence, scary monsters, or threatening situations
- No death, serious illness, or permanent loss
- No complex political or adult topics
- No moral ambiguity
```

**Why this matters:**
- Explicit boundaries prevent edge cases
- "Scary monsters" addresses common failure mode
- "Permanent loss" prevents sad endings
- "Moral ambiguity" keeps stories clear for young minds

### 5. Structural Requirements

The story arc provides a reliable template:

```
Story Structure (follow this arc):
1. Opening: Set a cozy scene and introduce the main character
2. Adventure: Present a small challenge or exciting discovery
3. Journey: Show the character working through the situation
4. Resolution: Solve the problem in a satisfying, kind way
5. Bedtime Ending: Wind down with calm imagery, perfect for sleep
```

**Why structure matters:**
- Prevents rambling or unfocused narratives
- Ensures proper pacing
- Guarantees a calm ending (crucial for bedtime)
- Makes stories feel complete

## Judge Prompting Strategy

### Detailed Rubric Design

Each evaluation criterion includes:

**1. Clear Definition**
```
CLARITY (1-10)
- Sentences are not overly complex
- Story events are easy to follow
- Character motivations are clear
- No confusing jumps or gaps in the narrative
```

**2. Score Anchors**
```
Scoring Guidelines:
- 1-3: Significant problems, needs major revision
- 4-5: Below average, several issues to address
- 6-7: Acceptable, minor improvements needed
- 8-9: Good to excellent quality
- 10: Exceptional, professional quality
```

**Why anchors matter:**
- Calibrates expectations
- Creates consistent scoring across runs
- Prevents score inflation or deflation

### Strict Output Format

We enforce JSON output with explicit schema:

```
You MUST respond with valid JSON only, using exactly this structure:

{
    "overall_score": <integer 1-10>,
    "age_appropriateness": <integer 1-10>,
    ...
}

Output ONLY the JSON object. No additional text, explanations, or markdown.
```

**Why strict formatting:**
- Enables reliable parsing
- Reduces post-processing complexity
- Catches format errors early
- Makes automation possible

### Strictness Calibration

```
"Be strict but fair. Reserve scores of 9-10 for truly excellent work."
```

**Why this matters:**
- Prevents all stories getting 10/10
- Creates room for improvement feedback
- Makes scores meaningful
- Maintains quality standards

## Refinement Prompting Strategy

When refining a story, we provide rich context:

```
I previously wrote this bedtime story based on the request: "{user_request}"

Here is the story I wrote:
---
{previous_story}
---

A reviewer provided this feedback for improvement:
{feedback}

Please rewrite the story incorporating this feedback...
```

**Key elements:**
1. Original request (maintains user intent)
2. Previous story (shows what was written)
3. Specific feedback (guides improvements)
4. Clear instruction (what to do next)

**Why this structure:**
- Preserves context across the feedback loop
- Targeted improvements, not complete rewrites
- Maintains story continuity
- Focuses on specific issues

## Temperature Selection Rationale

### Story Generation: 0.7

```python
STORY_TEMPERATURE = 0.7
```

**Trade-offs at different values:**
- 0.0-0.3: Too repetitive, formulaic stories
- 0.4-0.6: Good consistency, limited creativity
- 0.7-0.8: Good balance of creativity and coherence
- 0.9-1.0: Too random, may lose coherence

**Why 0.7:**
- Allows creative imagery and plot choices
- Maintains narrative coherence
- Produces varied stories for similar requests
- Sweet spot for creative writing

### Judge Evaluation: 0.2

```python
JUDGE_TEMPERATURE = 0.2
```

**Why low temperature:**
- Consistent scoring across runs
- Reliable JSON formatting
- Focused, objective feedback
- Reproducible evaluations

**Why not 0.0:**
- Some variation in feedback phrasing is fine
- Completely deterministic can feel robotic
- 0.2 provides slight natural variation

## Prompt Length Considerations

### Storyteller System Prompt

Approximately 500 tokens covering:
- Persona (50 tokens)
- Writing guidelines (150 tokens)
- Story structure (100 tokens)
- Content rules (100 tokens)
- Tone guidance (50 tokens)
- Format instruction (50 tokens)

**Why this length:**
- Comprehensive enough to guide behavior
- Short enough to leave room for output
- Balanced coverage of all aspects

### Judge System Prompt

Approximately 800 tokens covering:
- Persona (50 tokens)
- Five evaluation criteria (400 tokens)
- Scoring guidelines (150 tokens)
- JSON schema (150 tokens)
- Format enforcement (50 tokens)

**Why longer:**
- Detailed rubric needed for consistent evaluation
- JSON schema must be exact
- Each criterion needs clear definition

## Common Failure Modes and Mitigations

### Failure: Story too scary

**Mitigation in prompt:**
```
- No violence, scary monsters, or threatening situations
- The world is fundamentally safe and good
```

### Failure: Ending not calm

**Mitigation in prompt:**
```
- End on a peaceful, sleepy note
- Bedtime Ending: Wind down with calm imagery, perfect for sleep
```

### Failure: Vocabulary too advanced

**Mitigation in prompt:**
```
- Use simple vocabulary that young children can understand
- Keep sentences short and rhythmic
```

### Failure: Judge returns invalid JSON

**Mitigations:**
1. Explicit JSON schema in prompt
2. "Output ONLY the JSON object"
3. "No additional text, explanations, or markdown"
4. Fallback parsing in code

### Failure: Score inflation (everything is 10/10)

**Mitigation in prompt:**
```
Be strict but fair. Reserve scores of 9-10 for truly excellent work.
```

## Iterating on Prompts

When improving prompts, follow this process:

1. **Identify failure mode**: What's going wrong?
2. **Analyze cause**: Why is the LLM doing this?
3. **Draft fix**: What instruction would prevent this?
4. **Test**: Run multiple examples
5. **Refine**: Adjust based on results

**Example iteration:**

Problem: Stories sometimes end abruptly without wind-down

Draft fix: Added "End on a peaceful, sleepy note"

Still happening: Stories end peacefully but suddenly

Better fix: Added explicit "Bedtime Ending" to story arc with description "Wind down with calm imagery, perfect for sleep"

Result: Stories now have proper gentle wind-down

## Summary

Effective prompts for this system combine:

1. Clear persona establishment
2. Explicit audience specification  
3. Positive guidance (what to do)
4. Negative constraints (what to avoid)
5. Structural requirements (how to organize)
6. Output format enforcement (for judge)
7. Appropriate temperature selection

These elements work together to produce consistent, high-quality bedtime stories that meet the needs of the target audience.
