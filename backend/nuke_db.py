from app.database import SessionLocal, engine
from app import models
from sqlalchemy import text

def nuke_database():
    db = SessionLocal()
    try:
        print("💥 Nuking Database...")
        
        # 1. Blocked Domains
        deleted_blocked = db.query(models.BlockedDomain).delete()
        print(f"   - Deleted {deleted_blocked} blocked domains.")
        
        # 2. Scan Results
        deleted_scans = db.query(models.ScanResult).delete()
        print(f"   - Deleted {deleted_scans} scan results.")
        
        # 3. Commit
        db.commit()
        print("✅ Commit Successful.")
        
        # 4. Verify
        count_scans = db.query(models.ScanResult).count()
        count_blocked = db.query(models.BlockedDomain).count()
        print(f"👀 Verification:")
        print(f"   - Scans remaining: {count_scans}")
        print(f"   - Blocked remaining: {count_blocked}")
        
    except Exception as e:
        print(f"❌ Error Nuking DB: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    nuke_database()
