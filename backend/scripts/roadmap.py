import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
from db import get_connection

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-1.5-flash")  # or gemini-pro

# GET USER SKILLS
def get_user_skills(user_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT so.option_text
        FROM user_responses ur
        JOIN survey_options so ON ur.option_id = so.id
        WHERE ur.user_id = %s
    """, (user_id,))

    skills = [row[0] for row in cur.fetchall()]
    conn.close()

    return skills


# CLEAN JSON RESPONSE
def clean_json(text):
    text = text.strip()

    if "```" in text:
        text = text.split("```")[1]
        text = text.replace("json", "").strip()

    return text


# LLM ROADMAP GENERATION
def generate_roadmap_llm(user_id, role, skill_gap):
    user_skills = get_user_skills(user_id)

    prompt = f"""
You are an expert software career mentor.

User Skills:
{user_skills}

Target Role:
{role['title']} ({role['track']})

Missing Skills:
{skill_gap.get('missing_skills', [])}

Missing Technologies:
{skill_gap.get('missing_technologies', [])}

TASK:
Create a structured roadmap.

RULES:
- Skip skills user already has
- Focus on missing skills/tech
- Organize into topics
- Each task must include duration
- Be practical and project-based

Return STRICT JSON ONLY:

[
  {{
    "topic": "Topic Name",
    "tasks": [
      {{
        "task": "Task name",
        "duration": "1-2 weeks"
      }}
    ]
  }}
]
"""

    try:
        response = model.generate_content(prompt)

        content = clean_json(response.text)

        roadmap = json.loads(content)

    except Exception as e:
        print("LLM ERROR:", e)

        # FALLBACK
        roadmap = [
            {
                "topic": "Basics",
                "tasks": [
                    {"task": "Learn fundamentals", "duration": "1 week"}
                ]
            }
        ]

    return roadmap


# SAVE ROADMAP
def save_roadmap(user_id, role, roadmap):
    conn = get_connection()
    cur = conn.cursor()

    # clear old
    cur.execute("DELETE FROM user_roadmap WHERE user_id = %s", (user_id,))

    for section in roadmap:
        topic = section["topic"]

        for task_obj in section["tasks"]:
            cur.execute("""
                INSERT INTO user_roadmap (user_id, role_id, track, topic, task, duration)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                user_id,
                role["role_id"],
                role["track"],
                topic,
                task_obj["task"],
                task_obj["duration"]
            ))

    conn.commit()
    conn.close()

    return {"message": "LLM roadmap generated"}


# MAIN PIPELINE
def generate_adaptive_roadmap(user_id, role, skill_gap):
    roadmap = generate_roadmap_llm(user_id, role, skill_gap)
    return save_roadmap(user_id, role, roadmap)


# FETCH ROADMAP
def get_user_roadmap(user_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT topic, task, duration, completed
        FROM user_roadmap
        WHERE user_id = %s
        ORDER BY topic
    """, (user_id,))

    rows = cur.fetchall()
    conn.close()

    roadmap = {}

    for topic, task, duration, completed in rows:
        if topic not in roadmap:
            roadmap[topic] = []

        roadmap[topic].append({
            "task": task,
            "duration": duration,
            "completed": completed
        })

    return roadmap


# MARK COMPLETE
# def mark_task_done(user_id, task):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE user_roadmap
        SET completed = TRUE
        WHERE user_id = %s AND task = %s
    """, (user_id, task))

    conn.commit()
    conn.close()

    return {"message": "Task completed"}

def mark_task_done(user_id, task):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE user_roadmap
        SET completed = TRUE
        WHERE user_id = %s AND task = %s
    """, (user_id, task))

    conn.commit()
    conn.close()

    return {"message": "Task completed"}