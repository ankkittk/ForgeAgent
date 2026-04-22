from dotenv import load_dotenv
load_dotenv()

#---------------------------------------

import json
from prompts import architect_prompt, planner_prompt
from langchain_groq import ChatGroq
from states import Plan, File, TaskPlan
from langgraph.constants import START, END
from langgraph.graph import StateGraph

#---------------------------------------

llm = ChatGroq(model="llama-3.3-70b-versatile")

#---------------------------------------

def planner_agent(state: dict) -> dict:
    users_prompt = state["user_prompt"]
    resp = llm.with_structured_output(Plan).invoke(planner_prompt(users_prompt))
    return {"plan": resp}

def architect_agent(state: dict) -> dict:
    plan = state["plan"]
    resp = llm.with_structured_output(TaskPlan).invoke(architect_prompt(plan))
    resp.plan = plan  # Carry forward the original plan for context in later steps
    return {"task_plan": resp}

#---------------------------------------

graph = StateGraph(dict)
graph.add_node("planner", planner_agent)
graph.add_node("architect", architect_agent)  # Assuming architect_agent is defined similarly to planner_agent

graph.add_edge(START, "planner")
graph.add_edge("planner", "architect")
graph.add_edge("architect", END)

#---------------------------------------

agent = graph.compile()

user_prompt = "Create a simple calculator web application using HTML, CSS, and JavaScript."

result = agent.invoke({"user_prompt": user_prompt})

print(json.dumps(result, default=lambda o: o.model_dump(), indent=2, ensure_ascii=False))
