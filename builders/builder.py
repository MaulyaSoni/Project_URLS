from builders.interface import BuilderStatsInterface
from sqlalchemy.orm import Session
from models.url import URLResponse , ClickLogResponse ,AnalyticsResponse
from database.schema import URL , ClickLog 
from sqlalchemy import desc , func

class DynamicBuilder:
    def __init__(self , userBuilder : dict):
        for key , value in userBuilder.items():
            setattr(self , key , value)
    
    def __repr__(self):
        return {self.__dict__
        }
class StatsBuilderClass:
    
    def __init__(self):
        self.reset()
    
    def reset(self):
       self.userBuilder = {}


    def add_urls(self, db: Session, owner_id: int):
        urls = (
            db.query(URL)
            .filter(URL.owner_id == owner_id)
            .order_by(desc(URL.url_id))
            .all()
        )
        self.userBuilder["urls"] = urls
        return self


    def add_logs(self, db: Session, owner_id: int):
        click_logs = (
            db.query(ClickLog)
            .join(URL, ClickLog.url_id == URL.url_id)
            .filter(URL.owner_id == owner_id)
            .order_by(desc(ClickLog.clicked_at))
            .all()
        )
        self.userBuilder["click_logs"]= click_logs
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

        daily_clicks_response = [
            {
                "url_id": row.url_id,
                "date": row.date,
                "clicks_per_day": row.clicks
            }
            for row in daily_clicks
        ]
        self.userBuilder["daily_clicks_response"] = daily_clicks_response
        return self
   
    def build(self) -> BuilderStatsInterface:
        # details = BuilderStatsInterface(
        #   urls =  self.urls,
        #   click_logs = self.click_logs,
        #   daily_clicks_response = self.daily_clicks_response
        # )
        details = DynamicBuilder(self.userBuilder)
        self.reset()
        return details
