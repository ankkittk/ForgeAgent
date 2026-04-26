# ForgeAgent 🧠

## Overview
ForgeAgent is a multi-agent AI system that autonomously generates fully functional applications from natural language prompts. It goes beyond simple code generation by enforcing structured planning, architectural consistency, and iterative refinement.

## Key Features
- Multi-agent pipeline (Planner → Architect → Coder → Verifier)
- End-to-end project generation (HTML, CSS, JS, Python, etc.)
- Automatic file structuring and writing
- Built-in code validation and correction
- Streamlit-based interactive UI

## Architecture

### 1. Planner
Transforms user prompt into a structured project plan.

### 2. Architect
Designs system-level implementation with:
- Shared contract (IDs, events, operations)
- File-wise execution steps

### 3. Coder
Generates code per file with strict separation:
- HTML → structure
- CSS → styling
- JS → logic

### 4. Verifier
Reviews and fixes code to ensure:
- UI interactions work
- Logic is complete
- No broken connections

## Tech Stack
- LangGraph
- LangChain
- Groq LLM API (Model: openai/gpt-oss-120b)
- Streamlit
- Python

## Workflow
User Prompt → Planner → Architect → Coder → Verifier → Output Files

## Example Use Cases
- Web apps (Todo, Calculator)
- Browser games (Tic Tac Toe)
- UI-based tools

## Project Structure
- agent/graph.py → pipeline logic
- agent/prompts.py → prompt engineering
- agent/states.py → schemas & validation
- agent/tools.py → file operations
- main.py → Streamlit interface

## Strengths
- Structured reasoning over raw generation
- Handles real-world constraints (rate limits, token limits)
- Modular and extensible design

## Future Improvements
- Runtime verification (Playwright)
- Token optimization layer
- Failure recovery loop
- Metrics tracking

## Run Locally
```bash
pip install -r requirements.txt
streamlit run main.py
```

## Output
Generated projects are saved in:
```
generated_project/
```

## Author
Built as an advanced agentic AI system project for demonstrating system design, LLM orchestration, and reliability improvements.
