from pydantic import BaseModel ,Field , ConfigDict 

class StatsResponse(BaseModel):
    url_id : str
    total_clicks : int
    clicks_per_day : int

    model_config = ConfigDict(from_attributes=True)
