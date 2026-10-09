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

        # self.shipping_address: str = ""
        # self.delivery_notes: str = ""
        # self.discount: int = 0             
        # self.gift_wrap_colour: str = "None"  
        # self.priority_flag: bool = False  

    def add_urls(self , db : Session , url_id : str):
        print("-->",url_id)
        self.urls = (
            db.query(URL)
            .filter(
                URL.url_id == url_id
            )
            .order_by(desc(URL.url_id))
            .all()
            )
        return self
    
    def add_logs(self , db : Session , url_id : str):
        print("-->",url_id)
        self.click_logs = (
            db.query(ClickLog)
            .filter(
                URL.url_id == url_id
            )
            .order_by(
                desc(ClickLog.clicked_at))
            .all()
            ) 
        return self

    def add_daily_clicks(self , db : Session , url_id :     str):
        print("-->",url_id)
        
        daily_clicks = (
            db.query(
                ClickLog.url_id,
                func.date(ClickLog.clicked_at).label("date"), 
                func.count(ClickLog.log_id).label("clicks")
            )
            .filter(
                URL.url_id == url_id
            )
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

    # def add_order(self, items : int, shipping_address : str):
    #     self.items =  items
    #     self.shipping_address = shipping_address

    #     return self

    # def add_delivery_notes(self  , delivery_notes : str):
    #     self.delivery_notes = delivery_notes

    #     return self
        
    # def add_discount(self , discount : int):
    #     self.discount = discount

    #     return self
    
    # def add_gift_wrap(self , gift_wrap_colour : str ):
    #     self.gift_wrap_colour= gift_wrap_colour

    #     return self 

    # def add_priority(self , priority_flag : bool):
    #     self.priority_flag = priority_flag

    #     return self

    def build(self) -> BuilderStatsInterface:
        details = BuilderStatsInterface(
          urls =  self.urls,
          click_logs = self.click_logs,
          daily_clicks_response = self.daily_clicks_response
        )
        
        self.reset()
        return details
