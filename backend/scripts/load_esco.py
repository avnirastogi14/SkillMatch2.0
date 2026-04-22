import csv
import os
from db import get_connection

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_esco_skills():
    conn = get_connection()
    cur = conn.cursor()

    path = os.path.join(BASE_DIR, "data/esco/skills_en.csv")

    with open(path, newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            cur.execute("""
                INSERT INTO skills (name, source)
                VALUES (%s, 'ESCO')
                ON CONFLICT (name) DO NOTHING
            """, (row["preferredLabel"],))

    conn.commit()
    cur.close()
    conn.close()


def load_esco_roles():
    conn = get_connection()
    cur = conn.cursor()

    path = os.path.join(BASE_DIR, "data/esco/occupations_en.csv")

    with open(path, newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            cur.execute("""
                INSERT INTO roles (name, description, source, esco_id)
                VALUES (%s, %s, 'ESCO', %s)
                ON CONFLICT (name) DO NOTHING
            """, (
                row["preferredLabel"],
                row.get("description", ""),
                row["id"]
            ))

    conn.commit()
    cur.close()
    conn.close()


def load_esco_role_skills():
    conn = get_connection()
    cur = conn.cursor()

    path = os.path.join(BASE_DIR, "data/esco/occupationSkillRelations_en.csv")

    with open(path, newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            skill_name = row["skillLabel"]
            role_id = row["occupationUri"].split("/")[-1]

            cur.execute("""
                INSERT INTO role_skills (role_id, skill_id, source)
                SELECT r.id, s.id, 'ESCO'
                FROM roles r, skills s
                WHERE r.esco_id = %s AND s.name = %s
                ON CONFLICT DO NOTHING
            """, (role_id, skill_name))

    conn.commit()
    cur.close()
    conn.close()


def load_esco_skill_relations():
    conn = get_connection()
    cur = conn.cursor()

    path = os.path.join(BASE_DIR, "data/esco/skillsHierarchy_en.csv")

    with open(path, newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            cur.execute("""
                INSERT INTO skill_relations (parent_skill_id, child_skill_id)
                SELECT p.id, c.id
                FROM skills p, skills c
                WHERE p.name = %s AND c.name = %s
                ON CONFLICT DO NOTHING
            """, (
                row["broaderLabel"],
                row["narrowerLabel"]
            ))

    conn.commit()
    cur.close()
    conn.close()