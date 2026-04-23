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
- MUST include integration (event listeners, DOM usage)

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


def coder_system_prompt() -> str:
    return """
You are a senior software engineer.

Rules:
1. Output ONLY raw code. No markdown, no explanations.
2. Generate code ONLY for the target file.
3. STRICT separation:
   - HTML: structure only (NO <style>, NO JS)
   - CSS: styling only
   - JS: logic only
4. HTML MUST link external CSS and JS.
5. Code must be complete and functional.
6. Do NOT leave unused functions.
7. Prefer reusable logic but ensure it is actually used.
"""
