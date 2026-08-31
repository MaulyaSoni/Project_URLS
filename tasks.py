from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy.dialects.mysql import insert
from database.schema import URL, ClickLog, URLStats

def record_click_metrics(db: Session, url_id: int, date_time: str ):
    today = date.today()

    new_log = ClickLog(url_id=url_id, clicked_at=date_time)
    db.add(new_log)

    db.query(URL).filter(URL.url_id == url_id).update({
        URL.total_clicks: URL.total_clicks
    })

    # 3. Upsert Daily Metric Tracker 
    stmt = insert(URLStats).values(
        url_id=url_id,
        date=today,
        clicks_per_day=1
    )
    # If the combination of url_id and date exists, add 1 to clicks_per_day
    
    update_st = stmt.on_duplicate_key_update(
        clicks_per_day = URLStats.clicks_per_day + stmt.inserted.clicks_per_day
    )

    db.execute(update_st)
    db.commit()
