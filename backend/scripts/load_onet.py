import csv
from db import get_connection

def load_onet_roles():
    conn = get_connection()
    cur = conn.cursor()

    with open("backend/data/onet/Occupation Titles.txt", newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="|")

        for row in reader:
            cur.execute("""
                INSERT INTO roles (name, source, onet_code)
                VALUES (%s, 'ONET', %s)
                ON CONFLICT (name) DO NOTHING
            """, (
                row["Title"],
                row["O*NET-SOC Code"]
            ))

    conn.commit()
    cur.close()
    conn.close()

def load_onet_skills():
    conn = get_connection()
    cur = conn.cursor()

    with open("backend/data/onet/Skills.txt", newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="|")

        for row in reader:
            cur.execute("""
                INSERT INTO skills (name, source)
                VALUES (%s, 'ONET')
                ON CONFLICT (name) DO NOTHING
            """, (row["Element Name"],))

    conn.commit()
    cur.close()
    conn.close()

def load_onet_tech_skills():
    conn = get_connection()
    cur = conn.cursor()

    with open("backend/data/onet/Technology Skills.txt", newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="|")

        for row in reader:
            cur.execute("""
                INSERT INTO skills (name, source, skill_type)
                VALUES (%s, 'ONET', 'tool')
                ON CONFLICT (name) DO NOTHING
            """, (row["Example"],))

    conn.commit()
    cur.close()
    conn.close()

def load_onet_aliases():
    conn = get_connection()
    cur = conn.cursor()

    with open("backend/data/onet/Alternate Titles.txt", newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="|")

        for row in reader:
            cur.execute("""
                INSERT INTO role_aliases (role_id, alias)
                SELECT id, %s FROM roles
                WHERE onet_code = %s
            """, (
                row["Alternate Title"],
                row["O*NET-SOC Code"]
            ))

    conn.commit()
    cur.close()
    conn.close()