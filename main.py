from sqlalchemy.orm import Session
from fastapi import FastAPI, HTTPException , Request, Depends , BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm , OAuth2PasswordBearer
from database.db import get_db , engine
from database.schema import Base, Users
from models.message import MessageResponse
from models.user import UsersResponse , UsersRequest
from models.stats import StatsResponse 
from models.url import URLRequest , URLResponse  , URLStatsResponse
from routes.user import create_admin , create_user , fetch_all_user , delete_user ,login_with_token
from routes.url import get_url_link , create_url , get_all_url , get_url_stats 
from security.user import get_current_user
from dependencies.context import admin_context , current_user_context , new_user_context , owner_context
# from routes.user import test
 
app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
#---------------events-------------------------------------------------------------------

@app.on_event("startup")
def create_tables():
    # if targetted database not exist , then generates the all defined db and tables 
    Base.metadata.create_all(engine)   



#----------------------------------CREATE----------------------------------

#-----------------------------------USER-------------------------------- 
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

@app.post("/login")
def login_with_token_generation(
    form_data: OAuth2PasswordRequestForm = Depends(),
    context = Depends(new_user_context)):

    return login_with_token(context["db"] , form_data)

#----------------------------------------URL-------------------------------
@app.post("/url" , response_model= URLResponse , status_code=201)
def create_url_func(
    req : URLRequest,
    context = Depends(current_user_context)
    ):
    return create_url(context["db"], req ,context["current_user"])

       
#------------------------------READ---------------------

@app.get("/url" , response_model= list[URLStatsResponse])
def get_all_url_func(
    context = Depends(admin_context)):

    return get_all_url(context["db"])

#************************************************************

@app.get("/url/{short_link}")
def get_url_details_short_link(
    short_link : str , 
    request : Request,
    background_tasks : BackgroundTasks,
    # context = Depends(current_user_context)):
    context = Depends(new_user_context)):
    return get_url_link(context["db"] , request , background_tasks , short_link )

#********************************************************

@app.get("/url/stats/{url_id}")
def get_url_details(
    url_id : str,
    # context = Depends(owner_context)
    context = Depends(current_user_context)
    ):
    return get_url_stats(context["db"] , url_id , context["current_user"])

#**********************************************************
#---------------------------Users ---------------

@app.get("/users/me" , response_model= UsersResponse)
def get_my_info(
    current_user: Users = Depends(get_current_user)):

    return current_user

@app.get("/users/all" , response_model = list[UsersResponse])
def get_all_users(
    context = Depends(admin_context)):

    return fetch_all_user(context["db"])

#---------------------------delete-------------------------
@app.delete("/users/delete/{userid}" , response_model = MessageResponse , status_code = 200)
def delete_user_func(
    userid : str,
    context = Depends(admin_context)):

    return delete_user(context["db"] , userid , context["current_user"])



@app.get("/")
def read_root():
    return "Welcome to the URL shortener app"    


# @app.get("/test", response_model=UsersResponse)
# def test_func(
#     context = Depends(new_user_context)):
#     return test(context["db"])