from observers.interface import StatsObserver
from database.db import SessionLocal
from datetime import date
from sqlalchemy.orm import Session
from fastapi.exceptions import HTTPException
from sqlalchemy.dialects.mysql import insert
from database.schema import URL, ClickLog
import logging

class ClickLogObserver(StatsObserver):
    
    def update(self , url_id: int, date_time: str , referer : str , client_ip : str):
        db : Session = SessionLocal()
        new_log = ClickLog(url_id=url_id, clicked_at=date_time , referer = referer , ip = client_ip)
        db.add(new_log)
        db.commit()
        logging.info(f"Click_log created {date_time}")

class ClickCountObserver(StatsObserver):
    def update(self , url_id :int , date_time : str ,referer : str , client_ip : str):
        db : Session = SessionLocal()
        db.query(URL).filter(URL.url_id == url_id).update({
            URL.total_clicks : URL.total_clicks + 1
        },synchronize_session = False)

        logging.info(f"Total Clicks Count updated for {url_id}")
        db.commit()
        logging.info(f"Upsert operation done for {url_id}")

