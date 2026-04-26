from dotenv import load_dotenv
load_dotenv()

import json
from typing import Type, TypeVar

from agent.prompts import architect_prompt, planner_prompt, coder_system_prompt
from langchain_groq import ChatGroq
from agent.states import Plan, TaskPlan, validate_taskplan
from langgraph.constants import START, END
from langgraph.graph import StateGraph
from agent.tools import write_file, init_project_root

#---------------------------------

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
)

T = TypeVar("T")

#---------------------------------

def clean_code(code: str) -> str:
    cleaned = code.strip()

    if cleaned.startswith("```"):
        lines = cleaned.splitlines()

        if lines and lines[0].startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        cleaned = "\n".join(lines).strip()

        if cleaned and cleaned.splitlines():
            first_line = cleaned.splitlines()[0].strip().lower()
            if first_line in {"html", "javascript", "js", "css", "json", "python"}:
                cleaned = "\n".join(cleaned.splitlines()[1:]).strip()

    return cleaned


def extract_json_object(text: str) -> str:
    cleaned = text.strip()

    if cleaned.startswith("```"):
        lines = cleaned.splitlines()

        if lines and lines[0].startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        cleaned = "\n".join(lines).strip()

    start = cleaned.find("{")
    end = cleaned.rfind("}")

    if start == -1 or end == -1 or end <= start:
        raise ValueError(f"No JSON object found in model output:\n{text}")

    return cleaned[start : end + 1]


def parse_model(model_cls: Type[T], text: str) -> T:
    payload = extract_json_object(text)
    data = json.loads(payload)
    return model_cls.model_validate(data)

#---------------------------------

def planner_agent(state: dict) -> dict:
    users_prompt = state["user_prompt"]
    raw = llm.invoke(planner_prompt(users_prompt)).content
    plan = parse_model(Plan, raw)
    return {"plan": plan}


def architect_agent(state: dict) -> dict:
    plan = state["plan"]
    plan_text = json.dumps(plan.model_dump(), indent=2, ensure_ascii=False)

    last_error = None
    last_raw = ""

    for _ in range(3):
        last_raw = llm.invoke(architect_prompt(plan_text)).content
        try:
            task_plan = parse_model(TaskPlan, last_raw)
            validate_taskplan(task_plan)
            task_plan.plan = plan
            return {"task_plan": task_plan}
        except Exception as e:
            last_error = e

    raise ValueError(f"Architect failed after retries: {last_error}\nLast output:\n{last_raw}")


def coder_agent(state: dict) -> dict:
    steps = state["task_plan"].implementation_steps
    shared = state["task_plan"].shared
    system_prompt = coder_system_prompt()
    shared_text = json.dumps(shared, indent=2, ensure_ascii=False)

    outputs = []
    init_project_root()

    for task in steps:
        steps_text = "\n".join(task.steps)

        user_prompt = f"""Target file: {task.filepath}

Shared Contract:
{shared_text}

Requirements:
{steps_text}

Constraints:
- Use ONLY ids from shared contract
- Ensure all logic is connected to UI
- Do NOT leave unused functions or elements
- Ensure implementation is complete and interactive
"""

        raw = llm.invoke(system_prompt + "\n\n" + user_prompt).content
        cleaned = clean_code(raw)

        write_file.invoke({
            "path": task.filepath,
            "content": cleaned
        })

        outputs.append({
            "filepath": task.filepath,
            "code": cleaned
        })

    return {"code": outputs}

#---------------------------------

def build_agent():
    graph = StateGraph(dict)
    graph.add_node("planner", planner_agent)
    graph.add_node("architect", architect_agent)
    graph.add_node("coder", coder_agent)

    graph.add_edge(START, "planner")
    graph.add_edge("planner", "architect")
    graph.add_edge("architect", "coder")
    graph.add_edge("coder", END)

    return graph.compile()


agent = build_agent()


def run_generation(user_prompt: str) -> dict:
    return agent.invoke({"user_prompt": user_prompt})
