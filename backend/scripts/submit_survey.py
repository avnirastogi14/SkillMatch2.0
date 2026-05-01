from pydantic import BaseModel
from typing import List
from db import get_connection

# REQUEST MODEL
class SurveySubmission(BaseModel):
    user_id: int
    option_ids: List[int]

# SAVE RESPONSES FUNCTION
def save_user_responses(user_id: int, option_ids: List[int]):
    conn = get_connection()
    cur = conn.cursor()

    try:
        # Ensure user exists
        cur.execute("""
            INSERT INTO user_profiles (user_id)
            VALUES (%s)
            ON CONFLICT (user_id) DO NOTHING
        """, (user_id,))

        # Insert responses
        for option_id in option_ids:
            cur.execute("""
                INSERT INTO user_responses (user_id, option_id)
                VALUES (%s, %s)
                ON CONFLICT DO NOTHING
            """, (user_id, option_id))

        conn.commit()

    finally:
        conn.close()


def get_user_responses(user_id: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT so.option_text
        FROM user_responses ur
        JOIN survey_options so ON ur.option_id = so.id
        WHERE ur.user_id = %s
    """, (user_id,))

    data = [row[0] for row in cur.fetchall()]
    conn.close()

    return data