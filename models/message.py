from pydantic import BaseModel ,Field , ConfigDict 

class MessageResponse(BaseModel):
    mesasage  : str

    model_config = ConfigDict(from_attributes=True)