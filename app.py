import streamlit as st
import io
import pdfplumber
from agents import extract_resume_to_json, tailor_resume, audit_resume, write_cover_letter
from pdf_generator import generate_resume_pdf, generate_cover_letter_pdf  # ← fix 1

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
if "cover_letter_json" not in st.session_state:
    st.session_state.cover_letter_json = None
if "candidate_name" not in st.session_state:
    st.session_state.candidate_name = ""


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

# ── Pipeline ───────────────────────────────────────────────────
def run_pipeline(uploaded_file, job_description):
    """Runs the four-agent pipeline and stores results in session state."""

    with st.spinner("Extracting resume text..."):
        text, error = extract_text_from_pdf(uploaded_file)
    if error:
        st.error(error)
        return
    st.session_state.resume_text = text
    st.session_state.stage = 1

    with st.spinner("Agent 1: Parsing resume structure..."):
        resume_json, error = extract_resume_to_json(text)
    if error:
        st.error(error)
        return
    st.session_state.resume_json = resume_json
    st.session_state.candidate_name = resume_json.get("name", "")
    print(f"=== SAVED NAME: '{st.session_state.candidate_name}' ===")
    st.session_state.stage = 2

    with st.spinner("Agent 2: Tailoring for the job description..."):
        tailored_json, error = tailor_resume(resume_json, job_description)
    if error:
        st.error(error)
        return
    st.session_state.tailored_json = tailored_json
    st.session_state.stage = 3

    with st.spinner("Agent 3: Auditing ATS score..."):
        audit_json, error = audit_resume(tailored_json, job_description)
    if error:
        st.error(error)
        return
    st.session_state.audit_json = audit_json
    st.session_state.stage = 4

# ── UI ─────────────────────────────────────────────────────────
st.title("🎯 AI Resume Tailor")
upload_file = st.file_uploader("Upload your resume (PDF only)", type=["pdf"])
job_description = st.text_area("Paste job description here...", height=200)

if st.button("Reset"):
    st.session_state.stage = 0
    st.session_state.resume_text = None
    st.session_state.resume_json = None
    st.session_state.tailored_json = None
    st.session_state.audit_json = None
    st.session_state.cover_letter_json = None  # ← fix 2
    st.session_state.candidate_name = ""
    st.rerun()

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

    if raw_score <= 1:
        score = int(raw_score * 100)
    else:
        score = int(raw_score)

    st.metric("ATS Score", f"{score}/100")
    st.json(st.session_state.audit_json)

    # ── Resume PDF ─────────────────────────────────────────────
    if st.button("Generate Resume PDF"):
        output_path = generate_resume_pdf(st.session_state.tailored_json)
        with open(output_path, "rb") as f:
            st.download_button(
                label="📥 Download ATS Resume",
                data=f,
                file_name="tailored_resume.pdf",
                mime="application/pdf"
            )
        st.success("PDF generated successfully!")

    # ── Cover Letter ───────────────────────────────────────────
    tone = st.selectbox(
        "Cover Letter Tone",
        ["Professional", "Enthusiastic", "Concise"]
    )

    if st.button("Generate Cover Letter"):
        with st.spinner("Agent 4: Writing your cover letter..."):
            cover_letter_json, error = write_cover_letter(
                st.session_state.tailored_json,
                job_description,
                tone
            )

        if error:
            st.error(error)
        else:
            st.session_state.cover_letter_json = cover_letter_json
            st.subheader("📝 Your Cover Letter")
            st.write(cover_letter_json["salutation"])
            st.write(cover_letter_json["opening_paragraph"])
            for paragraph in cover_letter_json["body_paragraphs"]:
                st.write(paragraph)
            st.write(cover_letter_json["closing_paragraph"])
            st.write(cover_letter_json["sign_off"])

    # ── Cover Letter PDF ───────────────────────────────────────
    if st.session_state.cover_letter_json:                        # ← fix 3
        if st.button("Generate Cover Letter PDF"):
            candidate_name = (
                st.session_state.tailored_json.get("name") or
                st.session_state.resume_json.get("name") or
                    "Candidate"
                    )
            output_path = generate_cover_letter_pdf(
                st.session_state.cover_letter_json,
                candidate_name
            )
            with open(output_path, "rb") as f:
                st.download_button(
                    label="📥 Download Cover Letter",
                    data=f,
                    file_name="cover_letter.pdf",
                    mime="application/pdf"
                )