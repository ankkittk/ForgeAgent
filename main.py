import streamlit as st
import json
from agent.graph import agent

st.set_page_config(page_title="Coder Buddy", layout="wide")

st.title("🧠 Coder Buddy Agent")

user_input = st.text_area(
    "Enter your project request:",
    placeholder="e.g. Create a todo app using HTML, CSS, JS"
)

if st.button("Generate Project"):
    if not user_input.strip():
        st.warning("Please enter a prompt")
    else:
        with st.spinner("Generating..."):
            result = agent.invoke({"user_prompt": user_input})

        st.success("Project Generated!")

        # Show files
        for file in result["code"]:
            st.subheader(file["filepath"])
            st.code(file["code"], language="html")

        st.info("Files saved in: generated_project/")
