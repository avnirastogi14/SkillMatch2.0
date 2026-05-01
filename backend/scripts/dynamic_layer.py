import psycopg2
from dotenv import load_dotenv
import os
import json
import time
import random
from google import genai

load_dotenv()

DB_URL = os.getenv("DATABASE_URL")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-pro")

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

CACHE_FILE = "classification_cache.json"

VALID_TRACKS = [
    "backend",
    "frontend",
    "fullstack",
    "data_engineering",
    "data_science",
    "ai_ml",
    "cloud_devops",
    "cybersecurity",
    "networking",
    "systems",
]

TRACK_DEFINITIONS = {
    "backend": "Server-side development, APIs, databases, backend frameworks",
    "frontend": "UI, browser technologies, React, Vue, Angular, frontend frameworks",
    "fullstack": "Both frontend and backend development",
    "data_engineering": "Data pipelines, ETL, Spark, Kafka, data infrastructure",
    "data_science": "Data analysis, statistics, BI, experimentation",
    "ai_ml": "Machine learning, AI engineering, LLMs, NLP, CV",
    "cloud_devops": "Cloud platforms, DevOps, CI/CD, Kubernetes, Docker",
    "cybersecurity": "Security, pentesting, compliance, threat detection",
    "networking": "Networks, routing, infrastructure, telecom",
    "systems": "Low-level systems, OS, embedded, performance engineering",
}

# ───────────────── CONNECTION ─────────────────
def get_connection():
    return psycopg2.connect(DB_URL)

# ───────────────── CACHE ─────────────────
def load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_cache(cache):
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)

# ───────────────── FETCH ROLES ─────────────────
def fetch_roles_data(conn):
    query = """
    SELECT
        r.id,
        r.title,
        COALESCE(array_agg(DISTINCT s.name) FILTER (WHERE s.name IS NOT NULL), '{}'),
        COALESCE(array_agg(DISTINCT k.name) FILTER (WHERE k.name IS NOT NULL), '{}'),
        COALESCE(array_agg(DISTINCT t.name) FILTER (WHERE t.name IS NOT NULL), '{}')
    FROM roles r
    LEFT JOIN role_skills rs ON r.id = rs.role_id
    LEFT JOIN skills s ON rs.skill_id = s.id
    LEFT JOIN role_knowledge rk ON r.id = rk.role_id
    LEFT JOIN knowledge k ON rk.knowledge_id = k.id
    LEFT JOIN role_technologies rt ON r.id = rt.role_id
    LEFT JOIN technologies t ON rt.tech_id = t.id
    WHERE EXISTS (SELECT 1 FROM role_technologies rt2 WHERE rt2.role_id = r.id)
      AND r.title IS NOT NULL
    GROUP BY r.id, r.title;
    """
    with conn.cursor() as cur:
        cur.execute(query)
        rows = cur.fetchall()

    return [
        {
            "id": row[0],
            "title": row[1],
            "skills": row[2] or [],
            "knowledge": row[3] or [],
            "technologies": row[4] or [],
        }
        for row in rows
    ]

# ───────────────── STRONG PRE-CLASSIFIER ─────────────────
def pre_classify(title: str, technologies: list) -> str | None:
    t = title.lower()
    tech_str = " ".join(technologies).lower()

    # High-confidence rules
    if any(x in t for x in ["full stack", "fullstack", "full-stack"]):
        return "fullstack"
    if any(x in t for x in ["frontend", "front end", "front-end", "ui developer", "web developer", "react", "angular", "vue"]):
        return "frontend"
    if any(x in t for x in ["backend", "back end", "back-end", "api developer"]):
        return "backend"
    if "data engineer" in t or any(x in tech_str for x in ["spark", "kafka", "airflow", "etl", "snowflake", "dbt"]):
        return "data_engineering"
    if "data scientist" in t:
        return "data_science"
    if any(x in t for x in ["machine learning", "ml engineer", "ai engineer", "deep learning"]):
        return "ai_ml"
    if any(x in t for x in ["devops", "sre", "site reliability", "cloud engineer", "platform engineer"]):
        return "cloud_devops"
    if any(x in t for x in ["cyber", "security", "infosec", "penetration", "soc", "threat"]):
        return "cybersecurity"
    if "network" in t or any(x in tech_str for x in ["cisco", "routing", "firewall", "sdn"]):
        return "networking"
    if any(x in t for x in ["embedded", "firmware", "kernel", "systems programmer", "os developer"]):
        return "systems"

    return None

# ───────────────── LLM CLASSIFIER with Retry ─────────────────
def classify_role(role):
    pre = pre_classify(role["title"], role["technologies"])
    if pre:
        return pre

    prompt = f"""
Classify this job role into EXACTLY ONE track from the list below.

Tracks:
{chr(10).join(f"- {k}: {v}" for k, v in TRACK_DEFINITIONS.items())}

Title: {role['title']}
Skills: {', '.join(role['skills'][:15])}
Technologies: {', '.join(role['technologies'][:15])}

Rules:
- Use title as the strongest signal.
- Return ONLY the exact track name in lowercase (e.g. "backend", "ai_ml").
- Never return "other", "mixed", or anything outside the list.
"""

    for attempt in range(7):
        try:
            res = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
            )
            result = res.text.strip().lower().replace("-", "_").replace(" ", "_")

            if result in VALID_TRACKS:
                return result
            for track in VALID_TRACKS:
                if track in result:
                    return track

            return fallback(role)

        except Exception as e:
            error_str = str(e).lower()
            if "503" in error_str or "unavailable" in error_str or "high demand" in error_str:
                wait = (2 ** attempt) * 4 + random.uniform(2, 5)
                print(f"   503 High demand → retrying in {wait:.1f}s (attempt {attempt+1}/7)")
            elif "429" in error_str or "quota" in error_str or "resource_exhausted" in error_str:
                wait = (2 ** attempt) * 8 + random.uniform(5, 10)
                print(f"   Rate limit → waiting {wait:.1f}s")
            else:
                print(f"   LLM error: {e}")
                break

            time.sleep(wait)

    print(f"   → Fallback used for: {role['title']}")
    return fallback(role)

# ───────────────── FALLBACK ─────────────────
def fallback(role):
    t = role["title"].lower()
    tech = " ".join(role["technologies"]).lower()

    if any(x in tech for x in ["react", "angular", "vue", "html", "css", "javascript", "typescript"]):
        return "frontend"
    if any(x in tech for x in ["node", "django", "spring", "express", "laravel", "postgresql", "mysql"]):
        return "backend"
    if any(x in tech for x in ["aws", "azure", "gcp", "docker", "kubernetes", "terraform", "jenkins", "ansible"]):
        return "cloud_devops"
    if any(x in tech for x in ["spark", "kafka", "airflow", "hadoop"]):
        return "data_engineering"
    if any(x in tech for x in ["tensorflow", "pytorch", "scikit", "llm"]):
        return "ai_ml"
    if any(x in t for x in ["security", "cyber", "penetration"]):
        return "cybersecurity"

    # Default for most engineering / unknown roles
    return "systems"

# ───────────────── CLASSIFY ALL ─────────────────
def classify_all_roles(roles, cache):
    results = []
    total = len(roles)

    for i, role in enumerate(roles, 1):
        key = json.dumps({
            "title": role["title"],
            "skills": sorted(role["skills"]),
            "technologies": sorted(role["technologies"]),
        }, sort_keys=True)

        if key in cache:
            track = cache[key]
        else:
            print(f"[{i}/{total}] {role['title']}")
            track = classify_role(role)
            cache[key] = track
            if i % 20 == 0:
                save_cache(cache)

        print(f"   → {track}")
        results.append({
            **role,
            "track": track,
            "cluster": track   # Simple cluster = track for now
        })

    return results

# ───────────────── SAVE TO DB ─────────────────
def save_to_db(conn, roles):
    with conn.cursor() as cur:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS dynamic_it_roles (
            role_id INT PRIMARY KEY,
            title TEXT NOT NULL,
            cluster TEXT,
            track TEXT NOT NULL
        );
        """)

        cur.executemany(
            """
            INSERT INTO dynamic_it_roles (role_id, title, cluster, track)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (role_id)
            DO UPDATE SET 
                title = EXCLUDED.title,
                cluster = EXCLUDED.cluster,
                track = EXCLUDED.track;
            """,
            [(r["id"], r["title"], r["cluster"], r["track"]) for r in roles]
        )
    conn.commit()
    print(f"\nSaved {len(roles)} roles to dynamic_it_roles table.")

# ───────────────── MAIN ─────────────────
def build_dynamic_layer():
    print("🚀 Building dynamic IT classification layer...\n")

    conn = get_connection()
    cache = load_cache()

    roles = fetch_roles_data(conn)
    print(f"Fetched {len(roles)} roles.\n")

    classified = classify_all_roles(roles, cache)

    save_cache(cache)
    save_to_db(conn, classified)

    conn.close()
    print("\n✅ Dynamic IT layer built successfully!")

if __name__ == "__main__":
    build_dynamic_layer()