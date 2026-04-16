import streamlit as st
import io
import pdfplumber
from agents import extract_resume_to_json, tailor_resume, audit_resume

# ── Session State Initialization ──────────────────────────────
if "stage" not in st.session_state:
    st.session_state.stage = 0
if "resume_text" not in st.session_state:
    st.session_state.resume_text = None
if "resume_json" not in st.session_state:
    st.session_state.resume_json = None
if "tailored_json" not in st.session_state:
    st.session_state.tailored_json = None
if "audit_json" not in st.session_state:
    st.session_state.audit_json = None

# ── PDF Extraction Function ────────────────────────────────────
def extract_text_from_pdf(uploaded_file):
    try:
        pdf_bytes = uploaded_file.read()
        pdf_buffer = io.BytesIO(pdf_bytes)
        with pdfplumber.open(pdf_buffer) as pdf:
            text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        if not text.strip():
            return None, "This PDF appears to be scanned or image-based."
        return text, None
    except Exception as e:
        return None, f"Could not read PDF: {str(e)}"

# ── UI ─────────────────────────────────────────────────────────
def run_pipeline(uploaded_file, job_description):
    """Runs the three-agent pipeline and stores results in session state."""
    
    # Stage 1: Extract PDF text
    with st.spinner("Extracting resume text..."):
        text, error = extract_text_from_pdf(uploaded_file)
    if error:
        st.error(error)
        return  # guard clause — stop here
    st.session_state.resume_text = text
    st.session_state.stage = 1

    # Stage 2: Parse to JSON
    with st.spinner("Agent 1: Parsing resume structure..."):
        resume_json, error = extract_resume_to_json(text)
    if error:
        st.error(error)
        return  # guard clause — stop here
    st.session_state.resume_json = resume_json
    st.session_state.stage = 2

    # Stage 3: Tailor resume
    with st.spinner("Agent 2: Tailoring for the job description..."):
        tailored_json, error = tailor_resume(resume_json, job_description)
    if error:
        st.error(error)
        return  # guard clause — stop here
    st.session_state.tailored_json = tailored_json
    st.session_state.stage = 3

    # Stage 4: Audit resume
    with st.spinner("Agent 3: Auditing ATS score..."):
        audit_json, error = audit_resume(tailored_json, job_description)
    if error:
        st.error(error)
        return  # guard clause — stop here
    st.session_state.audit_json = audit_json
    st.session_state.stage = 4

st.title("🎯 AI Resume Tailor")
upload_file = st.file_uploader("Upload your resume (PDF only)", type=["pdf"])
job_description = st.text_area("Paste job description here...", height=200)

if st.button("Tailor my Resume"):
   if upload_file is not None and job_description.strip():
       run_pipeline(upload_file, job_description)
   else:
       st.error("Please upload a resume and paste a job description.")

if st.session_state.stage >= 1:
    st.subheader("📄 Extracted Resume Text")
    st.text_area("Extracted Text", value=st.session_state.resume_text, height=200)

if st.session_state.stage >= 2:
    st.subheader("📋 Parsed Resume Structure")
    st.json(st.session_state.resume_json)

if st.session_state.stage >= 3:
    st.subheader("✍️ Tailored Resume")
    st.json(st.session_state.tailored_json)

if st.session_state.stage == 4:
    st.subheader("📊 ATS Audit Results")
    raw_score = st.session_state.audit_json["score"]
    
    # Handle both 0.85 and 85 formats
    if raw_score <= 1:
        score = int(raw_score * 100)  # 0.85 → 85
    else:
        score = int(raw_score)        # 85 → 85

    st.metric("ATS Score", f"{score}/100")
    st.json(st.session_state.audit_json)
