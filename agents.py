import anthropic
import json
import os
import re
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def parse_json_response(raw: str) -> dict:
    """Extracts and parses JSON from Claude's response regardless of wrapping."""
    clean = raw.strip()
    start = clean.find("{")
    if start == -1:
        raise ValueError("No JSON object found in response")

    depth = 0
    for i, char in enumerate(clean[start:], start):
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
        if depth == 0:
            extracted = clean[start:i + 1]
            # Remove trailing commas before ] or } — json.loads rejects them
            extracted = re.sub(r",\s*([}\]])", r"\1", extracted)
            return json.loads(extracted)

    raise ValueError("No closing brace found")


def extract_resume_to_json(resume_text: str) -> tuple:
    """
    Agent 1: Extracts raw resume text into structured JSON.
    Uses Haiku — simple structured task, no need for Sonnet.
    Returns (json_data, error) tuple.
    """
    try:
        response = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=3000,
            system="""You are a resume parser. Extract the resume into JSON.
            Return ONLY valid JSON with these exact keys:
            {
                "name": "candidate full name — largest text at the top of the resume",
                "email": "",
                "phone": "",
                "address": "",
                "linkedin": "",
                "github": "",
                "title": "",
                "summary": "",
                "skills": [],
                "experience": [
                    {
                        "company": "",
                        "role": "",
                        "duration": "",
                        "achievements": []
                    }
                ],
                "projects": [
                    {
                        "name": "",
                        "description": "",
                        "technologies": []
                    }
                ],
                "education": [
                    {
                        "institution": "",
                        "degree": "",
                        "year": ""
                    }
                ],
                "certifications": [
                    {
                        "name": "",
                        "issuer": "",
                        "year": ""
                    }
                ],
            }
            Return ONLY the JSON object. No explanation. No markdown. No code blocks.""",
            messages=[
                {"role": "user", "content": f"Parse this resume:\n\n{resume_text}"}
            ]
        )

        raw = response.content[0].text
        resume_json = parse_json_response(raw)  # ← done, it's already a dict
        return resume_json, None

    except json.JSONDecodeError:
        return None, "AI returned invalid JSON. Please try again."
    except Exception as e:
        return None, f"Extraction failed: {str(e)}"

def tailor_resume(resume_json: dict, job_description: str) -> tuple:
    """
    Agent 2: Rewrites the resume JSON to align with the job description.
    Uses Sonnet — complex rewriting task requiring nuance and intelligence.
    Returns (tailored_json, error) tuple.
    """
    try:
        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=6000,
            system="""You are an expert resume writer and ATS optimization specialist.
Your goal is to maximize ATS compatibility while keeping everything honest and realistic.

STRICT RULES:
1. Return ONLY valid JSON in the exact same structure as the input
2. Never invent experience, skills, or qualifications that don't exist
3. Never change company names, job titles, or employment dates
4. Never add skills the candidate has not demonstrated in their resume
5. Never exaggerate achievements — keep metrics and claims realistic
6. Never use corporate buzzwords that don't reflect actual work done
7. Never upgrade an internship to sound like a senior role

KEYWORD ALIGNMENT:
8. Rewrite achievement bullets using exact keywords from the job description
9. Rewrite project descriptions to mirror keywords from the job description
10. Rephrase existing experience using the job description's exact language
11. Only add skills explicitly present OR strongly implied by existing experience
    Example: React experience implies JavaScript knowledge ✅
    Example: No cloud experience → don't add AWS ❌
12. Rewrite the summary to reflect the job description's terminology
13. Quantify achievements ONLY if realistic numbers can be inferred from context
    Example: "reduced load time" → "reduced load time by 20%" only if plausible ✅
    Example: Never invent percentages out of thin air ❌

TONE:
14. Keep language confident but grounded
15. Match the seniority level of the candidate — fresh graduate should sound like one
16. Never make an intern sound like a tech lead
17. Never add explanations or text outside the JSON structure""",
            messages=[
                {
                    "role": "user",
                    "content": f"""Tailor this resume to match the job description.

CURRENT RESUME (JSON):
{json.dumps(resume_json, indent=2)}

JOB DESCRIPTION:
{job_description}

Return the tailored resume in the exact same JSON structure."""
                }
            ]
        )

        raw = response.content[0].text
        result = parse_json_response(raw)  # ← one line, returns dict
        return result, None     

    except json.JSONDecodeError as e:
        return None, f"Extraction JSON error: {str(e)}"
    except Exception as e:
        return None, f"Tailoring failed: {str(e)}"
    
def audit_resume(tailored_json: dict, job_description: str) -> tuple:
    """
    Agent 3: Audits the tailored resume against the job description.
    Uses Haiku — simple structured task, no need for Sonnet.
    Returns (audit_json, error) tuple.
    """
    try:
        response = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=2048,
            system= """ You are a resume auditor.
            - Compare the tailored resume against the job description
            - Return ONLY valid JSON with these exact keys:
            {
                "score": 0-100,
                "matched_keywords": [],
                "missing_keywords": [],
                "suggestions": []}
            - "score" MUST be a whole number integer between 0 and 100. Never use decimals.
            - No explanation, No markdown, no code blocks""",
            messages=[
                {
                    "role": "user",
                    "content": f"""Audit this resume against the job description.
CURRENT TAILORED RESUME (JSON):
{json.dumps(tailored_json, indent=2)}

JOB DESCRIPTION:
{job_description}"""      
                }
            ]
        )
        
        raw = response.content[0].text
        audit_json = parse_json_response(raw)
        return audit_json, None
    
    except json.JSONDecodeError as e:
        return None, f"Audit JSON error: {str(e)}"
    except Exception as e:
        return None, f"Audit failed: {str(e)}"
    
def write_cover_letter(tailored_json: dict, job_description: str, tone: str = "Professional") -> tuple:
    """
    Agent 4: The Narrator — writes a tailored cover letter.
    Uses Sonnet — creative, long-form prose task.
    Returns (cover_letter_json, error) tuple.
    """
    try:
        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=2048,
            system=f"""You are an expert career coach writing a cover letter in first person.

TONE: {tone}

STRICT RULES:
1. Return ONLY valid JSON — no markdown, no explanation, no code blocks
2. Never invent experience, skills, or companies not present in the resume
3. Mirror high-frequency keywords from the job description naturally — do not stuff them
4. Identify the company's pain points from the job description and frame achievements as solutions
5. Match seniority tone to the verbs used in the job description (e.g., "drive", "lead", "support")
6. Be specific — reference actual achievements from the resume JSON, not generic statements
7. HARD LIMIT: Total word count MUST NOT exceed 300 words
8. opening_paragraph: EXACTLY 2 sentences
9. body_paragraphs: EXACTLY 2 paragraphs, EXACTLY 2 sentences each
10. closing_paragraph: EXACTLY 1 sentence

Return this exact JSON structure:
{{
    "salutation": "Dear Hiring Manager,",
    "opening_paragraph": "...",
    "body_paragraphs": ["...", "..."],
    "closing_paragraph": "...",
    "sign_off": "Sincerely,"
}}""",
            messages=[
                {
                    "role": "user",
                    "content": f"""Write a tailored cover letter using this data.

TAILORED RESUME (JSON):
{json.dumps(tailored_json, indent=2)}

JOB DESCRIPTION:
{job_description}"""
                }
            ]
        )

        raw = response.content[0].text
        cover_letter_json = parse_json_response(raw)
        return cover_letter_json, None

    except json.JSONDecodeError as e:
        return None, f"Cover letter JSON error: {str(e)}"
    except Exception as e:
        return None, f"Cover letter generation failed: {str(e)}"