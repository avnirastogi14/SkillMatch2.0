from collections import defaultdict
from db import get_connection
from scripts.explanation import generate_explanation_llm

from scripts.algorithms.context_builder import build_context_vector
from scripts.services.rl_service import rank_roles_with_rl


def normalize(text):
    return text.lower().replace("apis", "api").strip()


# ✅ STRONG FILTER
TECH_KEYWORDS = [
    "python", "java", "c", "c++", "sql", "javascript",
    "api", "cloud", "docker", "kubernetes",
    "machine learning", "data", "network",
    "security", "linux", "git", "database"
]


def is_relevant_skill(skill):
    return any(k in skill for k in TECH_KEYWORDS)


# -------------------------
# USER SIGNALS
# -------------------------
def get_user_signals(user_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT so.option_text, so.weight_map
        FROM user_responses ur
        JOIN survey_options so ON ur.option_id = so.id
        WHERE ur.user_id = %s
    """, (user_id,))

    skills = set()
    role_scores = defaultdict(float)

    for option_text, weight_map in cur.fetchall():
        skills.add(normalize(option_text))

        if weight_map:
            for role, weight in weight_map.items():
                role_scores[role] += weight

    conn.close()
    return skills, role_scores


# -------------------------
# ROLE SELECTION
# -------------------------
def get_top_roles(role_scores):
    conn = get_connection()
    cur = conn.cursor()

    max_score = max(role_scores.values()) if role_scores else 1

    normalized = {k: round(v / max_score, 2) for k, v in role_scores.items()}

    results = []
    seen_tracks = set()

    for track, score in sorted(normalized.items(), key=lambda x: x[1], reverse=True):
        if track in seen_tracks:
            continue

        cur.execute("""
            SELECT role_id, title
            FROM dynamic_it_roles
            WHERE track = %s
            LIMIT 1
        """, (track,))

        role = cur.fetchone()
        if role:
            results.append({
                "role_id": role[0],
                "title": role[1],
                "track": track,
                "confidence": score
            })

        seen_tracks.add(track)

    conn.close()
    return results[:10]


# -------------------------
# ENRICH
# -------------------------
def enrich_roles_with_data(roles):
    conn = get_connection()
    cur = conn.cursor()

    enriched = []

    for role in roles:
        role_id = role["role_id"]

        cur.execute("""
            SELECT s.name
            FROM role_skills rs
            JOIN skills s ON rs.skill_id = s.id
            WHERE rs.role_id = %s
        """, (role_id,))
        skills = [normalize(r[0]) for r in cur.fetchall()]

        cur.execute("""
            SELECT t.name
            FROM role_technologies rt
            JOIN technologies t ON rt.tech_id = t.id
            WHERE rt.role_id = %s
        """, (role_id,))
        tech = [normalize(r[0]) for r in cur.fetchall()]

        enriched.append({**role, "skills": skills, "technologies": tech})

    conn.close()
    return enriched


# -------------------------
# SKILL GAP
# -------------------------
def get_skill_gap(role_id, user_skills):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT s.name
        FROM role_skills rs
        JOIN skills s ON rs.skill_id = s.id
        WHERE rs.role_id = %s
    """, (role_id,))
    role_skills = {normalize(r[0]) for r in cur.fetchall()}

    cur.execute("""
        SELECT t.name
        FROM role_technologies rt
        JOIN technologies t ON rt.tech_id = t.id
        WHERE rt.role_id = %s
    """, (role_id,))
    role_tech = {normalize(r[0]) for r in cur.fetchall()}

    conn.close()

    user_skills = {normalize(s) for s in user_skills}

    missing_skills = [s for s in role_skills - user_skills if is_relevant_skill(s)]
    missing_tech = list(role_tech - user_skills)

    if not missing_tech:
        missing_tech = ["system design", "advanced projects"]

    return {
        "missing_skills": missing_skills[:5],
        "missing_technologies": missing_tech[:5]
    }


# -------------------------
# MAIN PIPELINE
# -------------------------
def recommend_user(user_id):
    user_skills, role_scores = get_user_signals(user_id)

    if not role_scores:
        return {"error": "No survey data found"}

    roles = get_top_roles(role_scores)
    enriched = enrich_roles_with_data(roles)

    user_profile = {
        "skills": list(user_skills),
        "technologies": list(user_skills)
    }

    ranked = rank_roles_with_rl(
        user=user_profile,
        roles=enriched,
        context_builder=build_context_vector
    )

    final_roles = ranked[:5]

    results = []

    for role in final_roles:
        gap = get_skill_gap(role["role_id"], user_skills)
        llm_output = generate_explanation_llm(user_skills, role, gap)

        results.append({
            "role": role["title"],
            "track": role["track"],
            "confidence": role["confidence"],
            "why": llm_output["why"],
            "skill_gap": gap,
            "roadmap": llm_output["roadmap"]
        })

    return {"recommendations": results}