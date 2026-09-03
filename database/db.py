import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

connect_args = {
    "check_same_thread": False
}

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind = engine , autocommit = False)

def get_db():
    db = SessionLocal()
    try:
        yield db
<<<<<<< HEAD
        db.commit() 
=======
>>>>>>> work
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()                          