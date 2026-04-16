import anthropic
import json
import os
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def extract_resume_to_json(resume_text: str) -> tuple:
    """
    Agent 1: Extracts raw resume text into structured JSON.
    Uses Haiku — simple structured task, no need for Sonnet.
    Returns (json_data, error) tuple.
    """
    try:
        response = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=2048,
            system="""You are a resume parser. Extract the resume into JSON.
            Return ONLY valid JSON with these exact keys:
            {
                "name": "",
                "email": "",
                "phone": "",
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
                "education": [
                    {
                        "institution": "",
                        "degree": "",
                        "year": ""
                    }
                ]
            }
            Return ONLY the JSON object. No explanation. No markdown. No code blocks.""",
            messages=[
                {"role": "user", "content": f"Parse this resume:\n\n{resume_text}"}
            ]
        )

        raw = response.content[0].text

        # Parse the JSON string into a Python dictionary
        resume_json = json.loads(raw)
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
            max_tokens=4096,
            system="""You are an expert resume writer and ATS optimization specialist.
            
Your job is to rewrite a resume to better match a job description.

STRICT RULES:
1. Return ONLY valid JSON in the exact same structure as the input
2. Never invent experience, skills, or qualifications that don't exist
3. Never change company names, job titles, or employment dates
4. DO rewrite achievement bullets to mirror keywords from the job description
5. DO add relevant technical skills that are mentioned in the job description IF the resume implies familiarity
6. DO quantify achievements where possible
7. DO use the exact terminology and keywords from the job description
8. Never add explanations or text outside the JSON structure""",
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
        tailored_json = json.loads(raw)
        return tailored_json, None

    except json.JSONDecodeError:
        return None, "Tailor returned invalid JSON. Please try again."
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
        audit_json = json.loads(raw)
        return audit_json, None
    
    except json.JSONDecodeError:
        return None, "Audit returned invalid JSON. Please try again."
    except Exception as e:
        return None, f"Audit failed: {str(e)}"