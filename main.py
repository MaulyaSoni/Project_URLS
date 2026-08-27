from sqlalchemy.orm import Session
from fastapi import FastAPI, HTTPException , Request, Depends , BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from db import get_db , engine
from schema import Base, Users
from models.message import MessageResponse
from models.user import UsersResponse , UsersRequest 
from models.url import URLRequest , URLResponse
from routes.user import create_admin , create_user , fetch_all_user , delete_user
from routes.token import create_token
from routes.url import get_url_stats , get_url , create_url , get_all_url
from dependencies.context import admin_context , current_user_context , new_user_context , url_stats_context
from security.user import get_current_user
 
app = FastAPI()

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

@app.post("/token")
def token_generation(
    form_data: OAuth2PasswordRequestForm = Depends(),
    context = Depends(new_user_context)):

    return create_token(context["db"] , form_data)

#----------------------------------------URL-------------------------------
@app.post("/url" , response_model=URLResponse , status_code=201)
def create_url_func(
    req : URLRequest,
    context = Depends(current_user_context)
    ):
    return create_url(context["db"], req ,context["current_user"])

       
#------------------------------READ---------------------
@app.get("/url/{short_link}")
def get_url_details(
    short_link : str , 
    request : Request,
    context = Depends(current_user_context)):
    return get_url(context["db"] , short_link )

@app.get("/url/stats/{url_id}")
        #   , response_model = URLResponse 
        # )
def get_url_stats_func(
    url_id : str,
    context = Depends(current_user_context)
    ):
    return get_url_stats(context["db"] , url_id , context["current_user"])

@app.get("/url")
def get_all_url_func(
    context = Depends(admin_context)):

    return get_all_url(context["db"])





#---------------------------Users ---------------
@app.get("/users/me" , response_model= UsersResponse)
def get_my_info(
    current_user: Users = Depends(get_current_user)):

    return current_user

@app.get("/users/all" , response_model = list[UsersResponse])
def get_all_users(
    context = Depends(admin_context)):

    return fetch_all_user(context["db"],context["current_user"])

#---------------------------delete-------------------------
@app.delete("/users/delete/{userid}" , response_model = MessageResponse , status_code = 200)
def delete_user_func(
    userid : str,
    context = Depends(admin_context)):

    return delete_user(context["db"] , userid , context["current_user"])


@app.get("/")
def read_root():
    return "Welcome to the URL shortener app "    