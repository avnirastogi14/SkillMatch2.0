import csv
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
conn = psycopg2.connect(os.getenv("DATABASE_URL"))
cur = conn.cursor()


# LOAD VALID ROLE IDS (dynamic layer)

cur.execute("SELECT role_id, title FROM dynamic_it_roles")
valid_roles = {rid: title for rid, title in cur.fetchall()}


# LOAD TECHNOLOGIES

cur.execute("SELECT id, name FROM technologies")
tech_map = {name.lower(): tid for tid, name in cur.fetchall()}


# SIMPLE CACHE (VERY IMPORTANT)

llm_cache = {}


# MOCK LLM FUNCTION (replace later)

def llm_match_technology(role_title, raw_tech):
    key = (role_title, raw_tech)

    if key in llm_cache:
        return llm_cache[key]

    # Replace with real API call
    # Prompt idea:
    # "Is '{raw_tech}' relevant for a {role_title} in software engineering? 
    # Return cleaned technology name or NONE"

    cleaned = raw_tech.strip().lower()

    # simple fallback logic
    if len(cleaned) < 2:
        return None

    llm_cache[key] = cleaned
    return cleaned



# GET OR CREATE TECHNOLOGY

def get_or_create_tech(name):
    name = name.strip().lower()

    if name in tech_map:
        return tech_map[name]

    cur.execute("""
        INSERT INTO technologies (name)
        VALUES (%s)
        RETURNING id
    """, (name,))
    
    tid = cur.fetchone()[0]
    tech_map[name] = tid
    return tid

# MAIN INGESTION
with open("/Users/avnirastogi/Projects/SkillMatch2.0/backend/data/onet/technology_skills.txt", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f, delimiter="\t")

    for row in reader:
        onet_code = row.get("O*NET-SOC Code")
        raw_tech = row.get("Example")

        if not raw_tech or not onet_code:
            continue

        # STEP 1: MAP ROLE

        cur.execute("SELECT role_id, title FROM roles WHERE onet_code = %s", (onet_code,))
        res = cur.fetchone()

        if not res:
            continue

        role_id, role_title = res


        # STEP 2: FILTER ONLY IT ROLES

        if role_id not in valid_roles:
            continue


        # STEP 3: LLM CLEANING (SAFE)

        clean_tech = llm_match_technology(role_title, raw_tech)

        if not clean_tech:
            continue


        # STEP 4: INSERT

        id = get_or_create_tech(clean_tech)

        cur.execute("""
            INSERT INTO role_technologies (role_id,tech_id)
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING
        """, (role_id, id))



# FINALIZE

conn.commit()
cur.close()
conn.close()