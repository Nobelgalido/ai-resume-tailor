import streamlit as st
import io
import pdfplumber
from agents import extract_resume_to_json, tailor_resume, audit_resume


# Function to extract text from a PDF

def extract_text_from_pdf(uploaded_file):
    """ Extracts text from an uploaded PDF file.
        Returns (text, error_message) tuple.
    """
    try:
        # Convert Streamlit's file buffer to bytes
        pdf_bytes = uploaded_file.read()
        
        # Wrap bytes in a file-like object pdfplumber can read
        pdf_buffer = io.BytesIO(pdf_bytes)
        
        with pdfplumber.open(pdf_buffer) as pdf:
            text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text: # some pages might be empty
                    text += page_text + "\n"
        
        # Check if we actually got any text
        if not text.strip():
            return None, "This PDF appears to be scanned or image-based. Please use a text-based PDF."
        
        return text, None # None means no error
    except Exception as e:
        return None, f"Could not read PDF: {str(e)}"


# Streamlit UI
st.title("🎯 AI Resume Tailor")
upload_file = st.file_uploader("Upload your resume (PDF only)", type=["pdf"])
job_description = st.text_area("Paste job description here...", height=200)

if st.button("Tailor my Resume"):
    if upload_file is not None and job_description.strip():
        text, error = extract_text_from_pdf(upload_file)
        if error:
            st.error(error)
        else:
            st.success("Resume extracted successfully!")
            st.text_area("Extracted Resume Text", value = text, height=200)
            resume_json, error = extract_resume_to_json(text)
            if error:
                st.error(error)
            else:
                st.success("Resume parsed successfully!")
                st.json(resume_json)
                tailored_json, error = tailor_resume(resume_json, job_description)
                if error:
                    st.error(error)
                else:
                    st.success("Resume tailored successfully!")
                    st.json(tailored_json)
                    audit_json, error = audit_resume(tailored_json, job_description)
                    if error:
                        st.error(error)
                    else:
                        st.success("Resume audited successfully!")
                        st.json(audit_json)
    else:
        st.error("Please upload a resume and paste a job description.")
        





                    