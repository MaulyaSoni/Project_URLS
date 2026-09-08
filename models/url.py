from pydantic import BaseModel ,Field , ConfigDict 
from datetime import datetime , date

class URLRequest(BaseModel):
    url : str = Field(min_length = 4)

class URLResponse(BaseModel):
    url_id : int
    url : str
    owner_id : int 
    short_link : str 
 
    model_config = ConfigDict(from_attributes=True)

class URLStatsResponse(URLResponse):
    total_clicks : int

    model_config = ConfigDict(from_attributes=True)

class AnalyticsResponse(BaseModel):
    stats_id : int
    url_id : int
    date : date
    clicks_per_day : int

    model_config = ConfigDict(from_attributes=True)

class ClickLogResponse(BaseModel):
    log_id : int
    url_id : int
    clicked_at : datetime
    referer : str
    # ip : str | None

    model_config = ConfigDict(from_attributes=True)

class DashboardResponse(BaseModel):
    urls: list[URLStatsResponse]
    click_logs : list[ClickLogResponse]
    analytics : list[AnalyticsResponse]

    model_config = ConfigDict(from_attributes=True)

class URLDetailsResponse(BaseModel):
    url : URLStatsResponse
    logs : list[ClickLogResponse]
    stats : list[AnalyticsResponse]