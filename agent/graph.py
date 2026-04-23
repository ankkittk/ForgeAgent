from dotenv import load_dotenv
load_dotenv()

import json
from prompts import architect_prompt, planner_prompt, coder_system_prompt
from langchain_groq import ChatGroq
from states import Plan, TaskPlan, validate_taskplan
from langgraph.constants import START, END
from langgraph.graph import StateGraph

#----------------------------------------------------------------------------------------------------------------------------------

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
)

#----------------------------------------------------------------------------------------------------------------------------------

def clean_code(code: str) -> str:
    code = code.strip()

    if code.startswith("```"):
        parts = code.split("```")
        if len(parts) >= 2:
            code = parts[1]
            if code.startswith(("html", "javascript", "css")):
                code = code.split("\n", 1)[1]

    return code.strip()

#----------------------------------------------------------------------------------------------------------------------------------

def planner_agent(state: dict) -> dict:
    users_prompt = state["user_prompt"]
    resp = llm.with_structured_output(Plan).invoke(planner_prompt(users_prompt))
    return {"plan": resp}

def architect_agent(state: dict) -> dict:
    plan = state["plan"]

    for _ in range(3):
        resp = llm.with_structured_output(TaskPlan).invoke(architect_prompt(plan))
        try:
            validate_taskplan(resp)
            resp.plan = plan
            return {"task_plan": resp}
        except Exception:
            continue

    raise ValueError("Architect failed after retries")

def coder_agent(state: dict) -> dict:
    steps = state["task_plan"].implementation_steps
    system_prompt = coder_system_prompt()

    outputs = []

    for task in steps:
        steps_text = "\n".join(task.steps)

        user_prompt = f"""You are implementing ONE file.

Target file: {task.filepath}

Requirements:
{steps_text}

Constraints:
- Only write code for this file
- Code must be COMPLETE and usable
- Do NOT leave unused functions
- Ensure logic is connected (e.g., UI → JS via events)
"""

        resp = llm.invoke(system_prompt + "\n\n" + user_prompt)

        cleaned = clean_code(resp.content)

        outputs.append({
            "filepath": task.filepath,
            "code": cleaned
        })

    return {"code": outputs}

#----------------------------------------------------------------------------------------------------------------------------------

graph = StateGraph(dict)
graph.add_node("planner", planner_agent)
graph.add_node("architect", architect_agent)
graph.add_node("coder", coder_agent)

graph.add_edge(START, "planner")
graph.add_edge("planner", "architect")
graph.add_edge("architect", "coder")
graph.add_edge("coder", END)

agent = graph.compile()

#----------------------------------------------------------------------------------------------------------------------------------

user_prompt = "Create a simple calculator web application using HTML, CSS, and JavaScript."

result = agent.invoke({"user_prompt": user_prompt})

print(json.dumps(result, default=lambda o: o.model_dump(), indent=2, ensure_ascii=False))
