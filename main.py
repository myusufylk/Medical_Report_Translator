from fastapi import FastAPI
from sqlalchemy import text
from database import engine, Base, SessionLocal
import models

app = FastAPI()


Base.metadata.create_all(bind=engine)


@app.get("/")
def read_root():
    return {"message": "Backend çalışıyor"}


@app.get("/test-db")
def test_db():
    try:
        db = SessionLocal()
        result = db.execute(text("SELECT version();"))
        version = result.fetchone()[0]
        db.close()

        return {
            "database": "connected",
            "version": version
        }
    except Exception as e:
        return {
            "database": "error",
            "detail": str(e)
        }


@app.get("/tables")
def check_tables():
    try:
        db = SessionLocal()

        result = db.execute(text("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """))

        tables = [row[0] for row in result.fetchall()]
        db.close()

        return {"tables": tables}
    except Exception as e:
        return {"error": str(e)}