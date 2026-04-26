from pathlib import Path

import streamlit as st

from agent.graph import run_generation

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
            result = run_generation(user_input)

        st.success("Project Generated!")

        files = result.get("code", [])
        st.write(f"Generated {len(files)} file(s).")

        for file in files:
            suffix = Path(file["filepath"]).suffix.lower()
            language = {
                ".html": "html",
                ".css": "css",
                ".js": "javascript",
                ".json": "json",
                ".py": "python",
                ".txt": "text",
            }.get(suffix, "text")

            with st.expander(file["filepath"], expanded=False):
                st.code(file["code"], language=language)

        st.info("Files saved in: generated_project/")
