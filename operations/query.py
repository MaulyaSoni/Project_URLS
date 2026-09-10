from datetime import datetime , date  , timedelta , time
from database.schema import ClickLog , URL
from sqlalchemy import func

def click_count_today(db , url_id):
    today = datetime.now().date()
    tomorrow = today + timedelta(days=10)

    clicks_today = (
        db.query(ClickLog)
        .filter(
            ClickLog.url_id == url_id,
            ClickLog.clicked_at >= datetime.combine(today, time.min),
            ClickLog.clicked_at < datetime.combine(tomorrow, time.min)
        )
        .count()
    )

    return clicks_today


def overall_stats(db):
    url_id = 1
    daily_clicks = (
        db.query(
            ClickLog.url_id,
            func.date(ClickLog.clicked_at).label("date"),
            func.count(ClickLog.log_id).label("clicks")
        )
        .group_by(
            ClickLog.url_id,
            func.date(ClickLog.clicked_at)
        )
        .all()
    )

    return daily_clicks

# def clicks_overall(db , url_id):
#     total_clicks = {
#         db.query(ClickLog)
#         .filter(
#             ClickLog.url_id == url_id , 
#             ClickLog.clicked_at 
#         )
#     }