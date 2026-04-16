import streamlit as st

st.title("🎯 AI Resume Tailor")
upload_file = st.file_uploader("Upload your resume (PDF only)", type=["pdf"])
job_description = st.text_area("Paste job description here...", height=200)

if st.button("Tailor my Resume"):
    st.write("Button clicked!")
