import csv
import os
from collections import defaultdict
from dotenv import load_dotenv
import psycopg2

# SETUP
load_dotenv()

DB_URL = os.getenv("DATABASE_URL")
DATA_DIR = "/Users/avnirastogi/Projects/SkillMatch2.0/backend/data/onet"

conn = psycopg2.connect(DB_URL)
cur = conn.cursor()


# FILTER IT ROLES
def is_it_role(title):
    keywords = [
        "developer", "engineer", "software",
        "data", "cloud", "security",
        "devops", "analyst", "programmer"
    ]
    return any(k in title.lower() for k in keywords)


# LOAD ROLES
def load_roles():
    print("Loading roles...")

    with open(f"{DATA_DIR}/occupation_titles.txt", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")

        for row in reader:
            code = row["O*NET-SOC Code"]
            title = row["Title"]
            desc = row.get("Description", "")

            if not is_it_role(title):
                continue

            cur.execute("""
                INSERT INTO roles (onet_code, title, description)
                VALUES (%s, %s, %s)
                ON CONFLICT (onet_code) DO NOTHING
            """, (code, title, desc))

    conn.commit()
    print("Roles loaded.")


# LOAD SKILLS + ROLE_SKILLS
def load_skills():
    print("Loading skills...")

    skill_map = {}
    role_map = {}

    # roles
    cur.execute("SELECT id, onet_code FROM roles")
    for r_id, code in cur.fetchall():
        role_map[code] = r_id

    skill_data = defaultdict(dict)

    with open(f"{DATA_DIR}/skills.txt", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")

        for row in reader:
            code = row["O*NET-SOC Code"]
            skill = row["Element Name"]
            scale = row["Scale ID"]
            value = float(row["Data Value"])

            if code not in role_map:
                continue

            # insert skill
            if skill not in skill_map:
                cur.execute("""
                    INSERT INTO skills (name)
                    VALUES (%s)
                    ON CONFLICT (name) DO NOTHING
                    RETURNING id
                """, (skill,))
                res = cur.fetchone()

                if res:
                    skill_map[skill] = res[0]
                else:
                    cur.execute("SELECT id FROM skills WHERE name=%s", (skill,))
                    skill_map[skill] = cur.fetchone()[0]

            key = (code, skill)

            if scale == "IM":
                skill_data[key]["importance"] = value
            elif scale == "LV":
                skill_data[key]["level"] = value

    # insert relations
    for (code, skill), vals in skill_data.items():
        cur.execute("""
            INSERT INTO role_skills (role_id, skill_id, importance, level)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        """, (
            role_map[code],
            skill_map[skill],
            vals.get("importance"),
            vals.get("level")
        ))

    conn.commit()
    print("Skills + role_skills loaded.")


# LOAD KNOWLEDGE
def load_knowledge():
    print("Loading knowledge...")

    knowledge_map = {}
    role_map = {}

    cur.execute("SELECT id, onet_code FROM roles")
    for r_id, code in cur.fetchall():
        role_map[code] = r_id

    knowledge_data = defaultdict(dict)

    with open(f"{DATA_DIR}/knowledge.txt", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")

        for row in reader:
            code = row["O*NET-SOC Code"]
            name = row["Element Name"]
            scale = row["Scale ID"]
            value = float(row["Data Value"])

            if code not in role_map:
                continue

            if name not in knowledge_map:
                cur.execute("""
                    INSERT INTO knowledge (name)
                    VALUES (%s)
                    ON CONFLICT (name) DO NOTHING
                    RETURNING id
                """, (name,))
                res = cur.fetchone()

                if res:
                    knowledge_map[name] = res[0]
                else:
                    cur.execute("SELECT id FROM knowledge WHERE name=%s", (name,))
                    knowledge_map[name] = cur.fetchone()[0]

            key = (code, name)

            if scale == "IM":
                knowledge_data[key]["importance"] = value
            elif scale == "LV":
                knowledge_data[key]["level"] = value

    for (code, name), vals in knowledge_data.items():
        cur.execute("""
            INSERT INTO role_knowledge (role_id, knowledge_id, importance, level)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        """, (
            role_map[code],
            knowledge_map[name],
            vals.get("importance"),
            vals.get("level")
        ))

    conn.commit()
    print("Knowledge loaded.")


# LOAD TECHNOLOGIES
def load_technologies():
    print("Loading technologies...")

    tech_map = {}
    role_map = {}

    cur.execute("SELECT id, onet_code FROM roles")
    for r_id, code in cur.fetchall():
        role_map[code] = r_id

    with open(f"{DATA_DIR}/technology_skills.txt", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")

        for row in reader:
            code = row["O*NET-SOC Code"]
            tech = row["Commodity Title"]
            demand = row["Hot Technology"] == "Y"

            if code not in role_map:
                continue

            if tech not in tech_map:
                cur.execute("""
                    INSERT INTO technologies (name)
                    VALUES (%s)
                    ON CONFLICT (name) DO NOTHING
                    RETURNING id
                """, (tech,))
                res = cur.fetchone()

                if res:
                    tech_map[tech] = res[0]
                else:
                    cur.execute("SELECT id FROM technologies WHERE name=%s", (tech,))
                    tech_map[tech] = cur.fetchone()[0]

            cur.execute("""
                INSERT INTO role_technologies (role_id, tech_id, demand)
                VALUES (%s, %s, %s)
                ON CONFLICT DO NOTHING
            """, (
                role_map[code],
                tech_map[tech],
                demand
            ))

    conn.commit()
    print("Technologies loaded.")


# LOAD ALTERNATE TITLES
def load_alternate_titles():
    print("Loading alternate titles...")

    role_map = {}

    cur.execute("SELECT id, onet_code FROM roles")
    for r_id, code in cur.fetchall():
        role_map[code] = r_id

    with open(f"{DATA_DIR}/alternate_titles.txt", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")

        for row in reader:
            code = row["O*NET-SOC Code"]
            alias = row["Alternate_Title"]

            if code not in role_map:
                continue

            cur.execute("""
                INSERT INTO role_aliases (role_id, alias)
                VALUES (%s, %s)
            """, (role_map[code], alias))

    conn.commit()
    print("Alternate titles loaded.")


# CLOSE CONNECTION
def close_connection():
    cur.close()
    conn.close()