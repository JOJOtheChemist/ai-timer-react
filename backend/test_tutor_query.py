from core.database import SessionLocal
from sqlalchemy import text

def test_tutor_query():
    db = SessionLocal()
    try:
        query = """
        SELECT id, username, avatar
        FROM tutor
        WHERE id = :tutor_id
        """
        
        for tutor_id in [2, 3, 4]:
            result = db.execute(text(query), {"tutor_id": tutor_id}).fetchone()
            print(f"Tutor ID {tutor_id}: {result}")
    finally:
        db.close()

if __name__ == "__main__":
    test_tutor_query() 