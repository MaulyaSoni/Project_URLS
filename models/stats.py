from pydantic import BaseModel ,Field , ConfigDict 
from datetime import datetime , date

class StatsResponse(BaseModel):
    url_id : str
    owner_id : str
    url : str
    short_link : str
    total_clicks : int
    clicks_per_day : int
    log_id : int
    clicked_at : datetime
    date : date
    model_config = ConfigDict(from_attributes=True)
