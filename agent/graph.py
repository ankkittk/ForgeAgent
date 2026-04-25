from dotenv import load_dotenv
from langgraph.prebuilt import create_react_agent
load_dotenv()

import json
from agent.prompts import architect_prompt, planner_prompt, coder_system_prompt
from langchain_groq import ChatGroq
from agent.states import Plan, TaskPlan, validate_taskplan
from langgraph.constants import START, END
from langgraph.graph import StateGraph
from agent.tools import write_file, read_file, get_current_directory, list_files, init_project_root

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
)

# ------------------------

def clean_code(code: str) -> str:
    code = code.strip()

    if code.startswith("```"):
        parts = code.split("```")
        if len(parts) >= 2:
            code = parts[1]
            if code.startswith(("html", "javascript", "css")):
                code = code.split("\n", 1)[1]

    return code.strip()

# ------------------------

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
    shared = state["task_plan"].shared
    system_prompt = coder_system_prompt()

    outputs = []

    init_project_root()

    for task in steps:
        steps_text = "\n".join(task.steps)

        user_prompt = f"""You are implementing ONE file.

Target file: {task.filepath}

Shared Contract:
{shared}

Requirements:
{steps_text}

Constraints:
- Use ONLY ids from shared.ids
- Follow shared.events
- Do NOT invent new ids
- Ensure JS matches HTML exactly
- Code must be complete
"""

        resp = llm.invoke(system_prompt + "\n\n" + user_prompt)

        cleaned = clean_code(resp.content)

        # 🔥 ACTUAL EXECUTION
        write_file.invoke({
            "path": task.filepath,
            "content": cleaned
        })

        outputs.append({
            "filepath": task.filepath,
            "code": cleaned
        })

    return {"code": outputs}

# ------------------------

graph = StateGraph(dict)
graph.add_node("planner", planner_agent)
graph.add_node("architect", architect_agent)
graph.add_node("coder", coder_agent)

graph.add_edge(START, "planner")
graph.add_edge("planner", "architect")
graph.add_edge("architect", "coder")
graph.add_edge("coder", END)

agent = graph.compile()

#------------------------

user_prompt = "Create a simple calculator web application using HTML, CSS, and JavaScript."

result = agent.invoke({"user_prompt": user_prompt})

print(json.dumps(result, default=lambda o: o.model_dump(), indent=2, ensure_ascii=False))
