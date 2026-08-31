from pydantic import BaseModel ,Field , ConfigDict 
from datetime import datetime

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
    # clicks_per_day : int
    # clicked_at : datetime
    model_config = ConfigDict(from_attributes=True)

