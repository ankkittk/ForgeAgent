from dotenv import load_dotenv
load_dotenv()

import json
from prompts import architect_prompt, planner_prompt
from langchain_groq import ChatGroq
from states import Plan, TaskPlan, validate_taskplan
from langgraph.constants import START, END
from langgraph.graph import StateGraph

#---------------------------------------

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
)

#---------------------------------------

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

#---------------------------------------

graph = StateGraph(dict)
graph.add_node("planner", planner_agent)
graph.add_node("architect", architect_agent)

graph.add_edge(START, "planner")
graph.add_edge("planner", "architect")
graph.add_edge("architect", END)

#---------------------------------------

agent = graph.compile()

user_prompt = "Create a simple calculator web application using HTML, CSS, and JavaScript."

result = agent.invoke({"user_prompt": user_prompt})

print(json.dumps(result, default=lambda o: o.model_dump(), indent=2, ensure_ascii=False))
