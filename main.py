from sqlalchemy.orm import Session
from fastapi import FastAPI, HTTPException , Depends , BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from db import get_db , engine

app = FastAPI()

#---------------events-------------------------------------------------------------------

@app.on_event("startup")
def create_tables():
    # if targetted database not exist , then generates the all defined db and tables 
    Base.metadata.create_all(engine)   

#------------------------------------------- 
@app.post("/register" , response_model = UsersResponse , status_code=201)
def register_user(
    user_data: UsersRequest,
    db: Session = Depends(get_db)):
    return create_user(db , user_data)

@app.post("/admin" , response_model = UsersResponse , status_code = 201)
def register_admin(
    user_data: UsersRequest,
    admin_key = str,
    db: Session = Depends(get_db)):
    return create_admin(db ,user_data , admin_key)

@app.post("/token")
def token_generation(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)):
    return create_token(db , form_data)
