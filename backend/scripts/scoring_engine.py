import psycopg2
import os
from dotenv import load_dotenv
from collections import defaultdict

load_dotenv()
DB_URL = os.getenv("DATABASE_URL")


def get_connection():
    return psycopg2.connect(DB_URL)


def compute_role_scores(user_id):
    conn = get_connection()
    cur = conn.cursor()

    # fetch responses + weight_map
    cur.execute("""
        SELECT so.weight_map
        FROM user_responses ur
        JOIN survey_options so ON ur.option_id = so.id
        WHERE ur.user_id = %s
    """, (user_id,))

    rows = cur.fetchall()

    role_scores = defaultdict(float)

    for (weight_map,) in rows:
        if not weight_map:
            continue

        for role, weight in weight_map.items():
            role_scores[role] += weight

    conn.close()

    # sort roles
    sorted_roles = sorted(role_scores.items(), key=lambda x: x[1], reverse=True)

    return sorted_roles[:5]

def get_top_roles(tracks):
    conn = get_connection()
    cur = conn.cursor()

    role_results = []

    for track, score in tracks:
        cur.execute("""
            SELECT role_id, title
            FROM dynamic_it_roles
            WHERE track = %s
            LIMIT 2
        """, (track,))

        roles = cur.fetchall()

        for r in roles:
            role_results.append({
                "role_id": r[0],
                "title": r[1],
                "track": track,
                "score": score
            })

    conn.close()
    return role_results