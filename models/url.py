from pydantic import BaseModel ,Field , ConfigDict 

class URLRequest(BaseModel):
    url : str = Field(min_length = 4)

class URLResponse(BaseModel):
    url_id : int
    url : str
    owner : str 
    short_link : str 
 
    model_config = ConfigDict(from_attributes=True)

