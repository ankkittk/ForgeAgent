from dotenv import load_dotenv
load_dotenv()

#---------------------------------------

from prompts import planner_prompt
from langchain_groq import ChatGroq
from states import Plan, File
from langgraph.constants import START, END
from langgraph.graph import StateGraph

#---------------------------------------

llm = ChatGroq(model="openai/gpt-oss-120b")

user_prompt = "Create a simple calculator web application using HTML, CSS, and JavaScript."


#---------------------------------------

def planner_agent(state: dict) -> dict:
    users_prompt = state["user_prompt"]
    resp = llm.with_structured_output(Plan).invoke(planner_prompt(users_prompt))
    return {"plan": resp}

state = {
    "user_prompt": user_prompt,
    "plan": None
}

graph = StateGraph(dict)
graph.add_node("planner", planner_agent)
graph.add_edge(START, "planner")
graph.add_edge("planner", END)

agent = graph.compile()

user_prompt = "Create a simple calculator web application using HTML, CSS, and JavaScript."

result = agent.invoke({"user_prompt": user_prompt})

print(result)