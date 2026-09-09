"""Run the non-destructive FAOS SQLite schema upgrade manually."""

from ai_agent.modules.database import init_db


if __name__ == "__main__":
    applied = init_db()
    if applied:
        print("Applied additive migrations:")
        for migration in applied:
            print(f" - {migration}")
    else:
        print("Database schema is already current.")
