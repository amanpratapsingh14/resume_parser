import streamlit as st
import requests
import pandas as pd
import json

st.title("Resume Parser (LLM-based)")

st.write("Upload a resume (PDF or DOCX) to extract structured information. You can view the output as JSON or in a table.")

uploaded_file = st.file_uploader("Upload your resume", type=["pdf", "docx"])

view_mode = st.radio("View output as:", ("JSON", "Tabular"))

if uploaded_file is not None:
    with st.spinner("Parsing resume..."):
        files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
        try:
            response = requests.post(
                "http://localhost:8080/upload_resume",
                files=files,
                headers={"accept": "application/json"}
            )
            if response.status_code == 200:
                data = response.json()
                st.success("Resume parsed successfully!")
                if view_mode == "JSON":
                    st.json(data)
                else:
                    # Tabular view: flatten work_experience and education for display
                    tab_data = []
                    if "work_experience" in data and isinstance(data["work_experience"], list):
                        for job in data["work_experience"]:
                            row = {"Section": "Work Experience"}
                            row.update(job)
                            tab_data.append(row)
                    if "education" in data and isinstance(data["education"], list):
                        for edu in data["education"]:
                            row = {"Section": "Education"}
                            row.update(edu)
                            tab_data.append(row)
                    if tab_data:
                        df = pd.DataFrame(tab_data)
                        st.dataframe(df)
                    else:
                        st.info("No tabular data to display.")
            else:
                st.error(f"Error: {response.status_code} - {response.text}")
        except Exception as e:
            st.error(f"Failed to connect to backend: {e}") 