from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy.dialects.mysql import insert
from database.schema import URL, ClickLog, URLStats

def record_click_metrics(db: Session, url_id: int, date_time: str , referer : str):
    today = date.today()

    # Log table updation
    try:
        new_log = ClickLog(url_id=url_id, clicked_at=date_time , referer = referer)
        db.add(new_log)
        db.commit()
    
    # Click counter 
        db.query(URL).filter(URL.url_id == url_id).update({
            URL.total_clicks: URL.total_clicks + 1
        })
        db.commit()
        
    except Exception as e:
        raise e 
    # Upsert Daily Click Tracker 
    stmt = insert(URLStats).values(
        url_id=url_id,
        date=today,
        clicks_per_day=1
    )
    # If the combination of url_id and date exists, add 1 to clicks_per_day
    
    update_st = stmt.on_duplicate_key_update(
        clicks_per_day = URLStats.clicks_per_day + 1
    )
    # print(update_st)
    db.execute(update_st)
    db.commit()
