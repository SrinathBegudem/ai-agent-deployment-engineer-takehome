# Bedtime Story Generator

A Python application that generates age-appropriate bedtime stories for children aged 5-10, using GPT-3.5-turbo with an LLM-based quality judge for iterative improvement.

## Quick Start (Copy-Paste Ready)

### Step 1: Clone and Navigate
```bash
git clone https://github.com/SrinathBegudem/ai-agent-deployment-engineer-takehome.git
cd ai-agent-deployment-engineer-takehome
```

### Step 2: Create Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Set Up API Key

**Option A: Create .env file**
```bash
echo 'OPENAI_API_KEY=your-openai-api-key-here' > .env
```

**Option B: Export directly (if .env doesn't work)**
```bash
export OPENAI_API_KEY='your-openai-api-key-here'
```

### Step 5: Run
```bash
python main.py
```

That's it! Enter a story idea when prompted.

---

## Project Overview

This project was built for the Hippocratic AI coding assignment. It takes simple story requests and produces engaging, gentle bedtime stories suitable for young children.

### Key Features

- Generates bedtime stories tailored for ages 5-10
- LLM judge evaluates stories across 6 quality dimensions
- Automatic refinement loop improves stories until they meet quality thresholds
- Interactive CLI with optional user feedback for further customization
- Modular architecture with clean separation of concerns

## Architecture
```
User Request
     |
     v
+--------------------+
|  Story Generator   |  <-- Crafted prompts for bedtime storytelling
+--------------------+
     |
     v
+--------------------+
|    LLM Judge       |  <-- Evaluates quality across 6 dimensions
+--------------------+
     |
     v
  Score >= 7?
   /      \
 YES       NO
  |         |
  v         v
Return   Refine Story (up to 2 rounds)
```

See [docs/system_design.md](docs/system_design.md) for complete architectural documentation.

## File Structure
```
.
├── main.py                 # CLI entry point
├── src/
│   ├── __init__.py         # Package exports
│   ├── config.py           # Configuration constants
│   ├── llm_client.py       # OpenAI API wrapper
│   ├── storyteller.py      # Story generation module
│   ├── judge.py            # Story evaluation module
│   └── pipeline.py         # Orchestration and refinement
├── docs/
│   ├── system_design.md    # System design documentation
│   ├── architecture.md     # Component architecture
│   └── prompting_strategy.md # Prompting techniques explained
├── tests/
│   ├── test_judge.py       # Judge module tests
│   └── test_pipeline.py    # Pipeline tests
├── requirements.txt        # Python dependencies
├── .env.example            # Example environment file
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

## How It Works

### 1. Story Generation

The storyteller module uses a carefully crafted system prompt that establishes:
- A warm, grandparent-like storyteller persona
- Age-appropriate vocabulary and concepts
- A five-act story arc structure
- Content guidelines (no scary content, positive resolution)
- Calm bedtime ending

### 2. Quality Evaluation

The judge evaluates stories across six dimensions:

| Dimension | What It Measures |
|-----------|------------------|
| Age Appropriateness | Vocabulary and concepts match target age |
| Clarity | Story is easy to follow |
| Engagement | Story captures interest |
| Emotional Tone | Mood is warm and comforting |
| Story Structure | Proper narrative arc with satisfying resolution |

### 3. Iterative Refinement

If a story scores below the quality threshold (7/10), the system:
1. Extracts specific improvement suggestions from the judge
2. Sends the story and feedback back to the storyteller
3. Generates an improved version
4. Re-evaluates until quality threshold is met or max rounds reached

### 4. User Feedback Loop

After receiving a story, users can optionally provide their own feedback:
- "Make it funnier"
- "Add more about the bunny's friends"
- "Make the ending calmer"

The system will refine the story based on this feedback.

## Configuration

Key parameters can be adjusted in `src/config.py`:

| Parameter | Default | Description |
|-----------|---------|-------------|
| STORY_TEMPERATURE | 0.7 | Creativity level for story generation |
| JUDGE_TEMPERATURE | 0.2 | Consistency level for evaluation |
| QUALITY_THRESHOLD | 7 | Minimum score to accept (1-10) |
| MAX_REFINEMENT_ROUNDS | 2 | Maximum improvement iterations |
| MAX_STORY_TOKENS | 900 | Maximum story length (~700 words) |

## Example Output
```
----------------------------------------------------------------------
                       YOUR BEDTIME STORY
----------------------------------------------------------------------

Once upon a time, in a cozy valley where the clouds touched the 
hilltops, there lived a small dragon named Ember. Unlike other 
dragons who breathed fire, Ember's breath came out in warm, gentle 
puffs that smelled like cinnamon and vanilla...

[story continues...]

...As the moon rose high above the valley, Ember curled up in her 
cozy nest of soft blankets. She smiled, thinking about tomorrow's 
baking adventures. The stars twinkled through her window like 
little nightlights, and soon Ember's eyes grew heavy with sweet, 
peaceful dreams.

----------------------------------------------------------------------
                       STORY QUALITY REPORT
----------------------------------------------------------------------

Overall Score:        8/10
Age Appropriateness:  9/10
Clarity:              8/10
Engagement:           8/10
Emotional Tone:       9/10
Story Structure:      7/10

Refinement Rounds:    1

Strengths:
  The story has a warm, gentle tone perfect for bedtime. The sensory 
  details (cinnamon, vanilla, soft blankets) create a cozy atmosphere.
```

## Troubleshooting

### API Key Not Found

If you see "OPENAI_API_KEY environment variable is not set", try:
```bash
# Export directly in terminal
export OPENAI_API_KEY='your-key-here'
python main.py
```

### SSL Warning

The urllib3 SSL warning can be ignored - it doesn't affect functionality.

## Documentation

- [System Design](docs/system_design.md) - Complete system architecture and flow diagrams
- [Architecture](docs/architecture.md) - Component details and data structures
- [Prompting Strategy](docs/prompting_strategy.md) - Explanation of prompting techniques

## Future Improvements

If given additional time, the following enhancements would be valuable:

1. **Web Interface**: Streamlit or Gradio app for non-technical users
2. **Story Categories**: Automatic categorization with specialized prompts
3. **Personalization**: Remember child's name and preferences across sessions
4. **Safety Filter**: Additional content safety check before output
5. **Audio Generation**: Text-to-speech for spoken story delivery

## Technical Notes

- Uses `openai==0.28.1` for compatibility with ChatCompletion API format
- Model is locked to `gpt-3.5-turbo` per assignment requirements
- API key must be set via environment variable (never committed to repo)

## Author

Srinath Begudem
