from db import get_connection

def get_skill_gap(role_id, user_skills):
    conn = get_connection()
    cur = conn.cursor()

    try:
        # ROLE SKILLS
        cur.execute("""
            SELECT s.name
            FROM role_skills rs
            JOIN skills s ON rs.skill_id = s.id
            WHERE rs.role_id = %s
        """, (role_id,))

        role_skills = {row[0].strip().lower() for row in cur.fetchall()}

        # ROLE TECHNOLOGIES
        cur.execute("""
            SELECT t.name
            FROM role_technologies rt
            JOIN technologies t ON rt.tech_id = t.id
            WHERE rt.role_id = %s
        """, (role_id,))

        role_tech = {row[0].strip().lower() for row in cur.fetchall()}

    finally:
        conn.close()

    # USER NORMALIZATION
    user_skills_set = {s.strip().lower() for s in user_skills}

    # GAP CALCULATION
    missing_skills = sorted(role_skills - user_skills_set)
    missing_tech = sorted(role_tech - user_skills_set)

    return {
        "missing_skills": missing_skills[:5],
        "missing_technologies": missing_tech[:5]
    }