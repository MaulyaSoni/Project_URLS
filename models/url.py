from pydantic import BaseModel ,Field , ConfigDict 

class URLRequest(BaseModel):
    url : str = Field(min_length = 4)

class URLResponse(BaseModel):
    url_id : int
    url : str
    owner_id : int 
    short_link : str 
    # secret_key : str
 
    model_config = ConfigDict(from_attributes=True)

class URLUserResponse(URLResponse):
    # url_id: int
    # url : str 
    # short_link : str
    # owner_id :int 
    secret_key : str

    model_config = ConfigDict(from_attributes=True)
    
class URLStatsResponse(URLResponse):
    total_clicks : int
    # clicks_per_day : int

    model_config = ConfigDict(from_attributes=True)
