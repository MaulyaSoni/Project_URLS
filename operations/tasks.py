from datetime import date
from sqlalchemy.orm import Session
from fastapi.exceptions import HTTPException
from sqlalchemy.dialects.mysql import insert
from database.schema import URL, ClickLog, URLStats
from database.db import SessionLocal
import logging

def record_click_metrics(url_id: int, date_time: str , referer : str):
    
    db : Session = SessionLocal()
    # Log table updation
    try:
        new_log = ClickLog(url_id=url_id, clicked_at=date_time , referer = referer)
        db.add(new_log)

        logging.info(f"Click_log created {date_time}")

    # Click counter 
        db.query(URL).filter(URL.url_id == url_id).update({
            URL.total_clicks : URL.total_clicks + 1
        },synchronize_session = False)

        logging.info(f"Total Clicks Count updated for {url_id}")


        today = date.today()
        stmt = insert(URLStats).values(
            url_id=url_id,
            date=today,
            clicks_per_day=1
        )

        # If the combination of url_id and date exists, add 1 to clicks_per_day
        update_st = stmt.on_duplicate_key_update(
            clicks_per_day = URLStats.clicks_per_day + 1
        )

        db.execute(update_st)
        db.commit()

        logging.info(f"Upsert operation done for {url_id}")

    except Exception as e:
        db.rollback()
        logging.error("Click track handle the exception")
        raise HTTPException(status_code = 500 , detail = f"Click track failed :-{e}")

    finally:
        db.close()  
        logging.info(f"Background tasks run successfully {url_id}")
