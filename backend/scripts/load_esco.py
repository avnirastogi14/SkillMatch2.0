import csv
from db import get_connection

def load_esco_skills():
    conn = get_connection()
    cur = conn.cursor()


    with open("backend/data/esco/skills_en.csv", newline='',encoding="utf-8") as f:
        reader = csv.DictReader(f)
        data = []

        for r in reader:
            data.append((
                row['preferredLabel'],"ESCO"
            ))

        cur.executemany("""
                        INSERT INTO skills (name, source)
                        VALUES (%s, %s) ON CONFLICT 
                        (name) DO NOTHING""", data)
        
        conn.commit()
        cur.close()
        conn.close()

def load_esco_roles():
    conn = get_connection()
    cur = conn.cursor()

    with open("backend/data/esco/occupations_en.csv", newline='',encoding="utf-8") as f:
        reader = csv.DictReader(f)
        data = []

        for row in reader:
            data.append((
                row["preferredLabel"],
                row["description"],
                "ESCO",
                row["id"]
            ))

        cur.executemany("""
                        INSERT INTO roles (name, source)
                        VALUES (%s, %s) ON CONFLICT 
                        (name) DO NOTHING""", data)
        
        conn.commit()
        cur.close()
        conn.close()

def load_esco_role_skills():
    conn = get_connection()
    cur = conn.cursor()

    with open("backend/data/esco/occupationSkillRelations_en.csv", newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            cur.execute("""
                INSERT INTO role_skills (role_id, skill_id, source)
                SELECT r.id, s.id, 'ESCO'
                FROM roles r, skills s
                WHERE r.esco_id = %s
                AND s.name = %s
                ON CONFLICT DO NOTHING
            """, (
                row["occupationUri"].split("/")[-1],
                row["skillLabel"]
            ))

    conn.commit()
    cur.close()
    conn.close()

def load_esco_skill_relations():
    conn = get_connection()
    cur = conn.cursor()

    with open("backend/data/esco/skillsHierarchy_en.csv", newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            cur.execute("""
                INSERT INTO skill_relations (parent_skill_id, child_skill_id)
                SELECT p.id, c.id
                FROM skills p, skills c
                WHERE p.name = %s
                AND c.name = %s
                ON CONFLICT DO NOTHING
            """, (
                row["broaderLabel"],
                row["narrowerLabel"]
            ))

    conn.commit()
    cur.close()
    conn.close()