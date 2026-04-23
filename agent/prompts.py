def planner_prompt(user_prompt: str) -> str:
    return f"""
You are the PLANNER agent.

Return ONLY valid JSON matching this schema:

{{
  "name": "string",
  "description": "string",
  "techstack": "string",
  "features": ["string"],
  "files": [
    {{
      "path": "string",
      "purpose": "string"
    }}
  ]
}}

User request:
{user_prompt}
"""


def architect_prompt(plan: str) -> str:
    return f"""
You are the ARCHITECT agent.

Return ONLY valid JSON.

Each step MUST include:
- filepath
- steps (>=3, concrete, implementation-level)
- dependencies

Rules:
- For JavaScript files → include functions and variables
- For HTML/CSS → functions and variables can be empty
- Use concrete identifiers (IDs, selectors, function names)
- Include integration details (DOM selectors, event flow)

Bad:
"Create UI"

Good:
"Create <input id='display'> and query it using document.getElementById('display') in script.js"

Schema:
{{
  "implementation_steps": [
    {{
      "filepath": "string",
      "functions": ["string"],
      "variables": ["string"],
      "steps": ["string"],
      "dependencies": ["string"]
    }}
  ]
}}

Project Plan:
{plan}
"""
