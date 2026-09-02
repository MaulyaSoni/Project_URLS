from sqlalchemy.orm import Session
from fastapi.exceptions import HTTPException
from sqlalchemy.exc import IntegrityError
from fastapi import FastAPI , Request, Depends , BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm , OAuth2PasswordBearer
from database.db import get_db , engine , SessionLocal
from database.schema import Base, Users
from models.message import MessageResponse
from models.user import UsersResponse , UsersRequest
from models.url import URLRequest , URLResponse  , URLStatsResponse
from routes.user import create_admin , create_user , fetch_all_user , delete_user ,login_with_token
from routes.url import get_url_link , get_all_url , get_url_stats 
from routes.url import create_url , delete_url , get_user_urls , get_dashboard
from operations.user import get_current_user
from dependencies.context import admin_context , current_user_context , new_user_context

 
app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

#---------------events-------------------------------------------------------------------

@app.on_event("startup")
def create_tables():
    # if targetted database not exist , then generates the all defined db and tables 
    Base.metadata.create_all(engine)   

#----------------------------------CREATE----------------------------------

#-----------------------------------USER-------------------------------- 
@app.post("/user"
 , response_model = UsersResponse , status_code=201)
 
def register_user(
    user_data: UsersRequest,
    db: Session = Depends(get_db)
):
    try:
        new_user = create_user(db , user_data)
        db.flush()
        db.commit()
        return {
            "userid":new_user.userid,
            "username":new_user.username,
            "email":new_user.email,
            "user_role":new_user.user_role
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500 , detail={e})

    finally:
        db.close()
    

@app.post("/admin" , response_model = UsersResponse , status_code = 201)
def register_admin(
    user_data: UsersRequest,
    admin_key = str,
    db: Session = Depends(get_db) 
): 
    try:
        new_user = create_admin(db , user_data)
        db.flush()
        db.commit()
        return {
            "userid":new_user.userid,
            "username":new_user.username,
            "email":new_user.email,
            "user_role":new_user.user_role
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500 , detail={e})

    finally:
        db.close()

@app.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db) 
):
    try:
        login_token = login_with_token(db, form_data)
        return login_token

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500 , detail={e})
    finally:
        db.close()


#----------------------------------------URL-------------------------------
@app.post("/url" , response_model = URLResponse , status_code=201)
def create_new_url(
    req : URLRequest,
    context = Depends(current_user_context)
):
    db = context["db"]
    try:
        new_url =  create_url(context["db"], req ,context["current_user"])
        db.flush()
        db.commit()

        return{
            "url_id":new_url.url_id,
            "url":new_url.url,
            "short_link":new_url.short_link,
            "owner_id":new_url.owner_id
        }   

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500 , detail={e})

    finally:
        db.close()       
#------------------------------READ---------------------

@app.get("/url" , response_model = list[URLStatsResponse])
def fetch_all_url(
    context = Depends(admin_context)
):
    db = context["db"]
    try:
        urls = get_all_url(context["db"],context["current_user"])
        return urls

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500 , detail={e})

    finally:
        db.close()     

#************************************************************

@app.get("/url/{short_link}")
def fetch_url_from_short_link(
    short_link : str , 
    request : Request,
    background_tasks : BackgroundTasks,
    context = Depends(new_user_context)
):
    db = context["db"]
    try:
        og_url = get_url_link(context["db"] , request , background_tasks , short_link )
        db.commit()
        return og_url

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500 , detail={e})

    finally:
        db.close()

@app.get("/my/urls/" , response_model= list[URLResponse])
def fetch_user_urls(
    context = Depends(current_user_context)
):
    db = context["db"]
    try:
        my_urls = get_user_urls(context["db"] , context["current_user"])
        return my_urls

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500 , detail={e})

    finally:
        db.close()

@app.get("/dashboard")
def fetch_dashboard(
    context = Depends(admin_context)
):
    db = context["db"]
    try:
        dashboard = get_dashboard(context["db"] , context["current_user"])
        return dashboard

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500 , detail={e})

    finally:
        db.close()

#********************************************************

@app.get("/url/stats/{url_id}")
def get_url__stats_details(
    url_id : str,
    context = Depends(current_user_context)
):
    db = context["db"]
    try:
        stats = get_url_stats(context["db"] , url_id , context["current_user"])
        return stats

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500 , detail={e})

    finally:
        db.close()

#---------------------------Users ---------------

@app.get("/users/me" , response_model = UsersResponse)
def get_my_info(
    current_user: Users = Depends(get_current_user)
):
    return current_user

@app.get("/users/all" , response_model = list[UsersResponse])
def get_all_users(
    context = Depends(admin_context)
):
    db = context["db"]
    try:
        all_users = fetch_all_user(context["db"] , context["current_user"])
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500 , detail={e})
    finally:
        db.close()

#---------------------------delete-------------------------
@app.delete("/users/delete/{userid}" , response_model = MessageResponse , status_code = 200)
def delete_single_user(
    userid : str,
    context = Depends(admin_context)
):
    db = context["db"]
    try:
        delete_req = delete_user(context["db"] , userid , context["current_user"])
        db.commit()
        return delete_req

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500 , detail={e})
    
    finally:
        db.close()
     
@app.delete("/url/delete/{url_id}" , response_model = MessageResponse , status_code = 200)
def delete_single_url(
    url_id : str,
    context = Depends(current_user_context)
):
    db = context["db"]
    try:
        delete_req = delete_url(context["db"] , url_id , context["current_user"])
        db.commit()
        return delete_req

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500 , detail={e})
    
    finally:
        db.close()
    
 
# @app.delete("/delete/all")
# def del_all(
#     context = Depends(admin_context)
# ):
#     return delete_all(context["db"],context["current_user"])

@app.get("/")
def read_root():
    return "Welcome to the URL shortener app"    
