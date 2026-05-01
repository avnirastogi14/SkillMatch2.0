import numpy as np

TRACKS = [
    "backend", "frontend", "fullstack", "data_engineering",
    "data_science", "ai_ml", "cloud_devops",
    "cybersecurity", "networking", "systems"
]


def build_context_vector(user, role):
    skill_match = len(set(user["skills"]) & set(role["skills"]))
    tech_match = len(set(user["technologies"]) & set(role["technologies"]))

    skill_score = skill_match / (len(role["skills"]) + 1)
    tech_score = tech_match / (len(role["technologies"]) + 1)

    track_vector = [1 if role["track"] == t else 0 for t in TRACKS]

    return np.array([skill_score, tech_score] + track_vector, dtype=float)