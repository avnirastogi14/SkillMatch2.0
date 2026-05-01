from fastapi import FastAPI
from contextlib import asynccontextmanager

from scripts.submit_survey import SurveySubmission, save_user_responses
from scripts.recommendation_engine import recommend_user
from scripts.roadmap import generate_adaptive_roadmap
from db import get_connection

from scripts.services.rl_service import init_model


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🧠 Initializing RL Model (LinUCB)...")
    init_model(n_features=12)
    yield


app = FastAPI(lifespan=lifespan)


@app.post("/submit-survey")
def submit_survey(data: SurveySubmission):
    save_user_responses(data.user_id, data.option_ids)
    return {"message": "Survey responses saved successfully", "user_id": data.user_id}


@app.get("/recommend/{user_id}")
def recommend(user_id: int):
    return recommend_user(user_id)


@app.get("/debug/{user_id}")
def debug_user(user_id: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT so.option_text, so.weight_map
        FROM user_responses ur
        JOIN survey_options so ON ur.option_id = so.id
        WHERE ur.user_id = %s
    """, (user_id,))

    data = cur.fetchall()
    conn.close()

    return [{"option": row[0], "weight_map": row[1]} for row in data]


@app.post("/roadmap/generate/{user_id}")
def create_roadmap(user_id: int):
    recs = recommend_user(user_id)

    if "recommendations" not in recs:
        return recs

    top_role = recs["recommendations"][0]

    return generate_adaptive_roadmap(
        user_id,
        {
            "role_id": 1,
            "title": top_role["role"],
            "track": top_role["track"]
        },
        top_role["skill_gap"]
    )