from builders.interface import BuilderStatsInterface
from sqlalchemy.orm import Session
from models.url import URLResponse , ClickLogResponse ,AnalyticsResponse
from database.schema import URL , ClickLog 
from sqlalchemy import desc , func

class DynamicBuilder:
    def __init__(self , userBuilder : dict):
        for key , value in userBuilder.items():
            setattr(self , key , value)
    
class StatsBuilderClass:
    
    def __init__(self):
        self.reset()
    
    def reset(self):
       self.userBuilder = {}

    @staticmethod
    def paginate(query , page = None , limit = None):
        if page is None and limit is None:
            return query.all(), None

        if page is None or limit is None:
            raise ValueError("Both (page and limit ) can't be null")
    
        if page < 1 and limit < 1:
            raise ValueError("Page and Limit should be positive integers")

        total = query.order_by(None).count()

        items = (
            query
            .offset((page - 1) * limit)
            .limit(limit)
            .all()
        )    
        pages = (total + limit - 1)
        pagination = {
            "page":page,
            "limit":limit,
            "total":total,
            "total_pages":pages
        }

        return items , pagination

    def add_urls(self, 
        db: Session, 
        all_urls: bool = False,
        owner_id: int | None = None,
        page: int | None = None,
        limit: int | None = None,
        is_active : bool | None = None
    ):
        if owner_id is None and not all_urls:
            raise ValueError(
                "owner_id is required unless all_urls=True"
            )

        if is_active is None:
            query = db.query(URL)

        else:
            query = db.query(URL).filter(URL.active == is_active)

        if not all_urls:
            query = query.filter(URL.owner_id == owner_id)

        query = query.order_by(desc(URL.url_id))

        urls, pagination = self.paginate(query,page,limit)

        self.userBuilder["urls"] = urls

        if pagination is not None:
            self.userBuilder["url_pagination"] = pagination

        return self

    def add_logs(self,
        db: Session,
        owner_id: int,
        page: int | None = None,
        limit: int | None = None,
        is_active : bool | None = None
    ):
        if is_active is None:
            query = (
                db.query(ClickLog)
                .join(URL, ClickLog.url_id == URL.url_id)
                .filter(URL.owner_id == owner_id)
                .order_by(
                    desc(ClickLog.clicked_at),
                    desc(ClickLog.log_id)
                )
            )

        else:
            query = (
                db.query(ClickLog)
                .join(URL, ClickLog.url_id == URL.url_id)
                .filter(URL.owner_id == owner_id , URL.active == is_active)
                .order_by(
                    desc(ClickLog.clicked_at),
                    desc(ClickLog.log_id)
                )
            )

        click_logs, pagination = self.paginate(query,page,limit)

        self.userBuilder["click_logs"] = click_logs

        if pagination is not None:
            self.userBuilder["logs_pagination"] = pagination

        return self


    def add_daily_clicks(self,
        db: Session, 
        owner_id: int,
        is_active : bool | None = None
    ):

        if is_active is None:
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

        else:
            daily_clicks = (
                db.query(
                    ClickLog.url_id,
                    func.date(ClickLog.clicked_at).label("date"),
                    func.count(ClickLog.log_id).label("clicks")
                )
                .join(URL, ClickLog.url_id == URL.url_id)
                .filter(URL.owner_id == owner_id, URL.active == is_active)
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
        self.userBuilder["analytics"] = daily_clicks_response
        return self
   
    def build(self) -> BuilderStatsInterface:

        details = DynamicBuilder(self.userBuilder)
        self.reset()
        return details
