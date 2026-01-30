from app.database import SessionLocal, engine
from app import models
from sqlalchemy import text

def reset_database():
    db = SessionLocal()
    try:
        # Delete all entries from ScanResult
        num_deleted = db.query(models.ScanResult).delete()
        print(f"Deleted {num_deleted} scan records.")
        
        # Option: Keep blocked domains? Or delete them too?
        # Only deleting scans logs as per 'old data' context.
        
        db.commit()
        print("Database cleaned successfully.")
    except Exception as e:
        print(f"Error resetting DB: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    # Ensure tables exist (just in case)
    models.Base.metadata.create_all(bind=engine)
    reset_database()
