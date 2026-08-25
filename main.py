from sqlalchemy.orm import Session
from fastapi import FastAPI, HTTPException , Depends , BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from db import get_db , engine
from schema import Base, Users
from models.message import MessageResponse
from models.user import UsersResponse , UsersRequest 
from routes.user import create_admin , create_user , fetch_all_user
from routes.token import create_token
from dependencies.context import get_admin_context
from security.user import get_current_user

app = FastAPI()

#---------------events-------------------------------------------------------------------

@app.on_event("startup")
def create_tables():
    # if targetted database not exist , then generates the all defined db and tables 
    Base.metadata.create_all(engine)   

#------------------------------------------- 
@app.post("/user" , response_model = UsersResponse , status_code=201)
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

#------------------------------------------

@app.get("/users/me" , response_model= UsersResponse)
def get_my_info(
    current_user: Users = Depends(get_current_user)):
    return current_user


@app.get("/users/all" , response_model = list[UsersResponse])
def get_all_users(
    context = Depends(get_admin_context)
    ):
 
    return fetch_all_user(context["db"],context["current_user"])


#---------------------------delete-------------------------
@app.delete("/users/delete/{userid}" , response_model = MessageResponse , status_code = 200)
def delete_user_func(
    userid : str,
    context = Depends(get_admin_context)):
    # db : Session = Depends(get_db),
    # user_log : Users = Depends(get_current_user),
    # current_user : dict = Depends(verify_admin)):
    return delete_user(context["db"] , userid , context["current_user"])
 