import psycopg2
from psycopg2.extras import execute_batch

def get_connection():
    return psycopg2.connect(
        dbname="skillmatch2",
        user="avnirastogi",
        password="",
        host="localhost",
        port="5432"
    )