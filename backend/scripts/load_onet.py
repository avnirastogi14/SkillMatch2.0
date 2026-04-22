import csv
import os
from db import get_connection

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_onet_roles():
    conn = get_connection()
    cur = conn.cursor()

    path = os.path.join(BASE_DIR, "data/onet/Occupation Titles.txt")

    with open(path, newline='', encoding="utf-8") as f:
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

    path = os.path.join(BASE_DIR, "data/onet/Skills.txt")

    with open(path, newline='', encoding="utf-8") as f:
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

    path = os.path.join(BASE_DIR, "data/onet/Technology Skills.txt")

    with open(path, newline='', encoding="utf-8") as f:
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

    path = os.path.join(BASE_DIR, "data/onet/Alternate Titles.txt")

    with open(path, newline='', encoding="utf-8") as f:
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