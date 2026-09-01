from pydantic import BaseModel ,Field , ConfigDict , EmailStr

class UsersRequest(BaseModel):
    username : str = Field(min_length = 2)
    email : EmailStr = Field(min_length= 5)
    password : str = Field(min_length = 6)
  
class UsersResponse(BaseModel):
    userid : int
    username : str
    email : EmailStr
    user_role : str

    #allow pydantic models to read data from regular class instance and db objects like sqlalchemy.orm 
    model_config = ConfigDict(from_attributes = True)