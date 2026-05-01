import psycopg2
import os
from dotenv import load_dotenv
import json

load_dotenv()
conn = psycopg2.connect(os.getenv("DATABASE_URL"))
cur = conn.cursor()


# -------------------------
# HELPER FUNCTIONS
# -------------------------
def insert_question(text, category, weight=1.0):
    cur.execute("""
        INSERT INTO survey_questions (question, category, weight)
        VALUES (%s, %s, %s)
        RETURNING id
    """, (text, category, weight))
    return cur.fetchone()[0]


def insert_option(question_id, text, mapping):
    cur.execute("""
        INSERT INTO survey_options (question_id, option_text, weight_map)
        VALUES (%s, %s, %s)
    """, (question_id, text, json.dumps(mapping)))


# -------------------------
# SECTION 1 — SKILLS
# -------------------------
q1 = insert_question(
    "Which languages are you comfortable with?",
    "skills"
)

languages = ["C", "C++", "Java", "Python", "JavaScript"]

for lang in languages:
    insert_option(q1, lang, {
        "backend": 2,
        "systems": 2,
        "ai_ml": 2 if lang == "Python" else 1
    })


q2 = insert_question(
    "Rate your strongest language (1–5)",
    "skills"
)

# scale question (no options needed)


q3 = insert_question(
    "Which technologies have you used?",
    "skills"
)

insert_option(q3, "Git/GitHub", {"backend": 1, "frontend": 1})
insert_option(q3, "Docker", {"cloud_devops": 3, "backend": 2})
insert_option(q3, "Linux", {"systems": 3, "cloud_devops": 2})
insert_option(q3, "REST APIs", {"backend": 3})
insert_option(q3, "Databases", {"backend": 3, "data_engineering": 2})
insert_option(q3, "Cloud", {"cloud_devops": 3})


# -------------------------
# SECTION 2 — INTERESTS
# -------------------------
q4 = insert_question(
    "What type of work excites you most?",
    "interest",
    weight=2.0
)

insert_option(q4, "Building features", {"frontend": 3, "backend": 3})
insert_option(q4, "Optimizing systems", {"backend": 3, "cloud_devops": 3})
insert_option(q4, "Analyzing data", {"data_science": 3, "ai_ml": 3})
insert_option(q4, "Designing scalable systems", {"backend": 3, "systems": 3})


q5 = insert_question(
    "What kind of problems do you enjoy?",
    "interest",
    weight=2.0
)

insert_option(q5, "Logical/DSA", {"backend": 3})
insert_option(q5, "Real-world applications", {"fullstack": 3})
insert_option(q5, "Data-heavy problems", {"data_science": 3, "ai_ml": 3})
insert_option(q5, "System design", {"backend": 3, "cloud_devops": 2})


q6 = insert_question(
    "What impact do you want to create?",
    "interest",
    weight=2.0
)

insert_option(q6, "Build scalable systems", {"backend": 3})
insert_option(q6, "Improve UI/UX", {"frontend": 3})
insert_option(q6, "Work with data insights", {"data_science": 3})
insert_option(q6, "Ensure security", {"cybersecurity": 3})


# -------------------------
# SECTION 3 — WORK STYLE
# -------------------------
q7 = insert_question("Preferred work environment", "experience")

insert_option(q7, "Startup", {"fullstack": 2})
insert_option(q7, "Corporate", {"backend": 1})
insert_option(q7, "Research", {"ai_ml": 2})


q8 = insert_question("Learning preference", "experience")

insert_option(q8, "Build projects", {"fullstack": 2, "backend": 2})
insert_option(q8, "Read docs", {"systems": 2})
insert_option(q8, "Courses", {"data_science": 1})
insert_option(q8, "Tutorials", {"frontend": 1})


q9 = insert_question("Interest in learning new tools", "experience")

insert_option(q9, "Yes", {"cloud_devops": 2})
insert_option(q9, "Maybe", {"backend": 1})
insert_option(q9, "No", {})


# -------------------------
# SECTION 4 — EXPERIENCE
# -------------------------
q10 = insert_question("What have you built?", "experience", weight=2.0)

insert_option(q10, "Static websites", {"frontend": 2})
insert_option(q10, "Full-stack apps", {"fullstack": 3})
insert_option(q10, "APIs / Backend systems", {"backend": 3})
insert_option(q10, "AI/ML projects", {"ai_ml": 3})
insert_option(q10, "None", {})


q11 = insert_question("Have you worked with:", "experience")

insert_option(q11, "Databases", {"backend": 2})
insert_option(q11, "APIs", {"backend": 2})
insert_option(q11, "Deployment", {"cloud_devops": 2})
insert_option(q11, "Machine Learning models", {"ai_ml": 3})
insert_option(q11, "System Design concepts", {"systems": 2})


# -------------------------
# SECTION 5 — ABILITY
# -------------------------
q12 = insert_question("Learning speed", "skills")
q13 = insert_question("Deadline handling", "skills")
q14 = insert_question("Teamwork", "skills")
q15 = insert_question("Communication", "skills")
q16 = insert_question("Adaptability", "skills")


# -------------------------
# SECTION 6 — DOMAIN (CRITICAL)
# -------------------------
q17 = insert_question(
    "Which domain interests you most?",
    "interest",
    weight=3.0
)

insert_option(q17, "Web Development", {"frontend": 3, "backend": 3, "fullstack": 3})
insert_option(q17, "AI / Machine Learning", {"ai_ml": 4, "data_science": 3})
insert_option(q17, "Cloud / DevOps", {"cloud_devops": 4})
insert_option(q17, "Cybersecurity", {"cybersecurity": 4})
insert_option(q17, "Data Engineering", {"data_engineering": 4})


# -------------------------
# FINALIZE
# -------------------------
conn.commit()
cur.close()
conn.close()

print("✅ Survey seeded successfully")