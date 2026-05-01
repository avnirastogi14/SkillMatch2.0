import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


# GEMINI EXPLANATION + ROADMAP
def generate_explanation_llm(user_skills, role, skill_gap):

    prompt = f"""
You are an expert career advisor.

User Skills:
{list(user_skills)}

Recommended Role:
{role['title']} ({role['track']})

Missing Skills:
{skill_gap.get('missing_skills', [])}

Missing Technologies:
{skill_gap.get('missing_technologies', [])}

TASK:
1. Explain WHY this role fits the user (2–3 lines)
2. Give 3–5 actionable learning steps

Return ONLY JSON in this format:

{{
  "why": "...",
  "roadmap": ["...", "..."]
}}
"""

    try:
        model = genai.GenerativeModel("gemini-pro")

        response = model.generate_content(prompt)

        content = response.text.strip()

        # Gemini sometimes returns ```json blocks → clean it
        if "```" in content:
            content = content.split("```")[1]
            content = content.replace("json", "").strip()

        return json.loads(content)

    except Exception as e:
        # -------------------------
        # FALLBACK
        # -------------------------
        return {
            "why": f"You are a good fit for {role['title']} based on your skills.",
            "roadmap": [
                f"Learn {tech}" for tech in skill_gap.get("missing_technologies", [])[:3]
            ]
        }