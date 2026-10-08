from datetime import date
from sqlalchemy.orm import Session
from fastapi.exceptions import HTTPException
from sqlalchemy.dialects.mysql import insert
from database.schema import URL, ClickLog
from database.db import SessionLocal
import logging

def record_click_metrics(url_id: int, date_time: str , referer : str , client_ip : str):
    
    db : Session = SessionLocal()
    # Log table updation
    try:
        new_log = ClickLog(url_id=url_id, clicked_at=date_time , referer = referer , ip = client_ip)
        db.add(new_log)

        logging.info(f"Click_log created {date_time}")

    # Click counter 
        db.query(URL).filter(URL.url_id == url_id).update({
            URL.total_clicks : URL.total_clicks + 1
        },synchronize_session = False)

        logging.info(f"Total Clicks Count updated for {url_id}")
        db.commit()

        logging.info(f"Upsert operation done for {url_id}")

    except Exception:
        db.rollback()
        logging.exception("Click track handle the exception")
        raise 
        
    finally:
        db.close()  
        logging.info(f"Background tasks run successfully {url_id}")
