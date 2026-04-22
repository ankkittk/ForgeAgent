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

STRICT RULE:
You MUST return ONLY valid JSON matching this schema:

{{
  "implementation_steps": [
    {{
      "filepath": "string",
      "task_description": "string"
    }}
  ]
}}

DO NOT:
- add markdown
- add explanations
- add headings
- add text outside JSON

Project Plan:
{plan}
"""
