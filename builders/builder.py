from builders.interface import BuilderStatsInterface
from sqlalchemy.orm import Session
from models.url import URLResponse , ClickLogResponse ,AnalyticsResponse
from database.schema import URL , ClickLog 
from sqlalchemy import desc , func

class StatsBuilderClass:
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.urls: list[URLResponse] = []
        self.click_logs : list[ClickLogResponse] 
        self.daily_clicks_response : list[AnalyticsResponse]


    def add_urls(self, db: Session, owner_id: int):
        self.urls = (
            db.query(URL)
            .filter(URL.owner_id == owner_id)
            .order_by(desc(URL.url_id))
            .all()
        )
        return self


    def add_logs(self, db: Session, owner_id: int):
        self.click_logs = (
            db.query(ClickLog)
            .join(URL, ClickLog.url_id == URL.url_id)
            .filter(URL.owner_id == owner_id)
            .order_by(desc(ClickLog.clicked_at))
            .all()
        )
        return self


    def add_daily_clicks(self, db: Session, owner_id: int):
        daily_clicks = (
            db.query(
                ClickLog.url_id,
                func.date(ClickLog.clicked_at).label("date"),
                func.count(ClickLog.log_id).label("clicks")
            )
            .join(URL, ClickLog.url_id == URL.url_id)
            .filter(URL.owner_id == owner_id)
            .group_by(
                ClickLog.url_id,
                func.date(ClickLog.clicked_at)
            )
            .order_by(
                desc(func.date(ClickLog.clicked_at))
            )
            .all()
        )

        self.daily_clicks_response = [
            {
                "url_id": row.url_id,
                "date": row.date,
                "clicks_per_day": row.clicks
            }
            for row in daily_clicks
        ]

        return self
   
    def build(self) -> BuilderStatsInterface:
        details = BuilderStatsInterface(
          urls =  self.urls,
          click_logs = self.click_logs,
          daily_clicks_response = self.daily_clicks_response
        )
        
        self.reset()
        return details
