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