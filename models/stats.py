from pydantic import BaseModel ,Field , ConfigDict 

class StatsRequest(BaseModel):
    total_clicks : int
    clicks_per_day : int

