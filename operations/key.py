import secrets
import string
from sqlalchemy.orm import Session
from database.schema import URL

def check_short_link(db : Session , short_link = str):
    return db.query(URL).filter(URL.short_link == short_link).first() 

def create_unique_random_short_link(db: Session) -> str:
    short_link = create_random_key()

    while check_short_link (db,short_link):
        short_link = create_random_key()
        
    return short_link

