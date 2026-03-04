import os
import psycopg2


def get_db_connection():
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL must be set for database access")
    return psycopg2.connect(url)
