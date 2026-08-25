from pydantic import BaseModel ,Field , ConfigDict 

class StatsRequest(BaseModel):
    url : str = Field(min_length = 4)
    # total_clicks: int = Field(ge = 0)

class StatsResponse(BaseModel):
    url : str
    total_clicks : int
    clicks_per_day : int 
    short_link : str  

    model_config = ConfigDict(from_attributes=True)
