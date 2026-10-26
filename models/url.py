from pydantic import BaseModel ,Field , ConfigDict 
from datetime import datetime , date

class URLRequest(BaseModel):
    url : str = Field(min_length = 4)

class URLResponse(BaseModel):
    url_id : int
    url : str
    owner_id : int 
    short_link : str 
    total_clicks : int

    model_config = ConfigDict(from_attributes=True)

class URLResponseActive(URLResponse):
    is_active : bool

    model_config = ConfigDict(from_attributes=True)

class ClickLogResponse(BaseModel):
    log_id : int
    url_id : int
    clicked_at : datetime
    referer : str
    ip : str | None

    model_config = ConfigDict(from_attributes=True)

class AnalyticsResponse(BaseModel):
    url_id : int | None
    date : date | None
    clicks_per_day : int | None 
    
    model_config = ConfigDict(from_attributes=True)

class DashboardResponse(BaseModel):
    urls: list[URLResponseActive] | None
    click_logs : list[ClickLogResponse] | None
    analytics : list[AnalyticsResponse] | None

    model_config = ConfigDict(from_attributes=True)

class PaginationMetadataReposne(BaseModel):
    page : int
    limit : int 
    total : int
    total_pages : int 
    
    model_config = ConfigDict(from_attributes = True)

class URLPageResponse(PaginationMetadataReposne):
    items: list[URLResponseActive]

    model_config = ConfigDict(from_attributes = True)

class ReferAnalyticsResponse(BaseModel):
    referer_domain : str
    clicks : int

    model_config = ConfigDict(from_attributes=True)

class URLDetailsResponse(BaseModel):
    url : URLResponse | None
    click_logs : list[ClickLogResponse] | None
    analytics : list[AnalyticsResponse]| None
    referer_analytics : list[ReferAnalyticsResponse] | None
    page : int
    limit : int 
    total : int
    total_pages : int 

    model_config = ConfigDict(from_attributes=True)

class ClickStatsResponse(BaseModel):
    click_logs : list[ClickLogResponse]
    analytics : list[AnalyticsResponse]
    referer_analytics : list[ReferAnalyticsResponse] | None
    page : int
    limit : int 
    total : int
    total_pages : int 
    
    model_config = ConfigDict(from_attributes=True)