from dotenv import load_dotenv
load_dotenv()

from agent.prompts import planner_prompt
from langchain_groq import ChatGroq
from agent.states import Plan, File

llm = ChatGroq(model="openai/gpt-oss-120b")

user_prompt = "Create a simple calculator web application using HTML, CSS, and JavaScript."


#---------------------------------------

prompt = planner_prompt(user_prompt)


response = llm.with_structured_output(Plan).invoke(prompt)

print(response.model_dump_json(indent=1))