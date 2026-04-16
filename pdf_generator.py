from fpdf import FPDF
import os

def sanitize(text: str) -> str:
    """Replaces non-ASCII characters with ASCII equivalents."""
    return (text
        .replace("–", "-")   # en dash
        .replace("—", "-")   # em dash
        .replace("\u2019", "'")  # curly apostrophe
        .replace("\u2018", "'")  # curly open quote
        .replace("\u201c", '"')  # curly open double quote
        .replace("\u201d", '"')  # curly close double quote
        .replace("•", "-")   # bullet point
    )

def generate_resume_pdf(tailored_json: dict) -> str:
    """
    Generates an ATS-safe PDF from the tailored resume JSON.
    Returns the file path of the generated PDF.
    """
    pdf = FPDF()
    pdf.set_margins(15, 15, 15)
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_x(pdf.l_margin)
    
    # Calculate usable page width explicitly
    effective_width = pdf.w - 2 * pdf.l_margin 

    # ── Header: Name & Title ──────────────────────────────────
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 8, sanitize(tailored_json.get("name", "")), ln=True, align="C")

    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 6, sanitize(tailored_json.get("title", "")), ln=True, align="C")

    # ── Contact Info — all in one line ────────────────────────────
    pdf.set_font("Helvetica", "", 10)

    # Pre-calculate all widths
    separator = "  |  "
    sep_w = pdf.get_string_width(separator)

    plain_parts = []
    if tailored_json.get("address"):
        plain_parts.append(tailored_json["address"])
    if tailored_json.get("phone"):
        plain_parts.append(tailored_json["phone"])
    if tailored_json.get("email"):
        plain_parts.append(tailored_json["email"])

    plain_text = separator.join(plain_parts) + separator
    plain_w = pdf.get_string_width(plain_text)
    linkedin_w = pdf.get_string_width("LinkedIn")
    github_w = pdf.get_string_width("GitHub")
    total_w = plain_w + linkedin_w + sep_w + github_w

    # Center entire line
    pdf.set_x((pdf.w - total_w) / 2)

    # Plain text
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(plain_w, 5, sanitize(plain_text), ln=False)

    # LinkedIn
    pdf.set_text_color(0, 0, 255)
    pdf.set_font("Helvetica", "U", 10)
    pdf.cell(linkedin_w, 5, "LinkedIn", ln=False, link=tailored_json.get("linkedin", ""))

    # Separator
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(sep_w, 5, separator, ln=False)

    # GitHub
    pdf.set_text_color(0, 0, 255)
    pdf.set_font("Helvetica", "U", 10)
    pdf.cell(github_w, 5, "GitHub", ln=True, link=tailored_json.get("github", ""))

    # Reset
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", 10)
    pdf.ln(2)

    # ── Section Helper ────────────────────────────────────────
    def section_header(title: str):
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_fill_color(230, 230, 230)
        pdf.cell(0, 8, title.upper(), ln=True, fill=True)
        pdf.ln(2)

    # ── Summary ───────────────────────────────────────────────
    if tailored_json.get("summary"):
        section_header("Professional Summary")
        pdf.set_font("Helvetica", "", 10)
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(effective_width, 6, sanitize(tailored_json["summary"]))
        pdf.ln(4)

    # ── Skills ────────────────────────────────────────────────
    if tailored_json.get("skills"):
        section_header("Technical Skills")
        pdf.set_font("Helvetica", "", 10)
        skills_text = "  |  ".join(tailored_json["skills"])
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(effective_width, 6, sanitize(skills_text))
        pdf.ln(4)

    # ── Experience ────────────────────────────────────────────
    if tailored_json.get("experience"):
        section_header("Professional Experience")
        for job in tailored_json["experience"]:
            pdf.set_font("Helvetica", "B", 11)
            pdf.cell(0, 7, sanitize(job.get("role", "")), ln=True)
            pdf.set_font("Helvetica", "I", 10)
            pdf.cell(0, 6, sanitize(f"{job.get('company', '')}  |  {job.get('duration', '')}"), ln=True)
            pdf.set_font("Helvetica", "", 10)
            for achievement in job.get("achievements", []):
                pdf.set_x(pdf.l_margin)
                pdf.multi_cell(effective_width, 6, sanitize(f"  - {achievement}"))
    
    # ── Projects ──────────────────────────────────────────────────
    if tailored_json.get("projects"):
        pdf.ln(3)
        section_header("Projects")
        for project in tailored_json["projects"]:
            pdf.set_font("Helvetica", "B", 11)
            pdf.cell(0, 7, sanitize(project.get("name", "")), ln=True)
            pdf.set_font("Helvetica", "", 10)
            pdf.set_x(pdf.l_margin)
            pdf.multi_cell(effective_width, 6, sanitize(project.get("description", "")))
            if project.get("technologies"):
                tech_text = " | ".join(project["technologies"])
                pdf.set_font("Helvetica", "I", 10)
                pdf.set_x(pdf.l_margin)
                pdf.multi_cell(effective_width, 6, sanitize(f"Technologies: {tech_text}"))
            pdf.ln(3)

    # ── Education ─────────────────────────────────────────────
    if tailored_json.get("education"):
        pdf.ln(3)
        section_header("Education")
        for edu in tailored_json["education"]:
            pdf.set_font("Helvetica", "B", 11)
            pdf.cell(0, 7, sanitize(edu.get("degree", "")), ln=True)
            pdf.set_font("Helvetica", "", 10)
            pdf.cell(0, 6, sanitize(f"{edu.get('institution', '')}  |  {edu.get('year', '')}"), ln=True)
            pdf.ln(3)
    
    # ── Certifications ────────────────────────────────────────────
    if tailored_json.get("certifications"):
        pdf.ln(3)
        section_header("Certifications")
        for cert in tailored_json["certifications"]:
            pdf.set_font("Helvetica", "B", 11)
            pdf.cell(0, 7, sanitize(cert.get("name", "")), ln=True)
            pdf.set_font("Helvetica", "", 10)
            pdf.cell(0, 6, sanitize(f"{cert.get('issuer', '')}  |  {cert.get('year', '')}"), ln=True)
            pdf.ln(3)
            
    # ── Save ──────────────────────────────────────────────────
    output_path = "tailored_resume.pdf"
    pdf.output(output_path)
    return output_path