from sqlalchemy import text

from db import engine


with engine.connect() as conn:
    name, user = conn.execute(
        text("SELECT current_database(), current_user")
    ).one()

    version = conn.execute(
        text("SHOW server_version")
    ).scalar_one()

print(f"Connected to {name} as {user}, PostgreSQL {version}")