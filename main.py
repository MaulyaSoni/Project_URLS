import logging
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import FastAPI , Request, Depends , BackgroundTasks , Query
from fastapi.security import OAuth2PasswordRequestForm , OAuth2PasswordBearer
from fastapi.exceptions import HTTPException
from database.db import get_db , SessionLocal
from database.schema import Users
from models.user import UsersResponse , UsersRequest
from models.url import URLRequest , URLResponse  , DashboardResponse , URLPageResponse , URLDetailsResponse , AnalyticsResponse , ClickStatsResponse , PaginationMetadataReposne
from models.message import MessageResponse
from routes.user import create_admin , create_user , fetch_all_user , delete_user ,login_with_token ,logout_route
from routes.url import get_url_link , get_all_url , get_url_stats 
from routes.url import create_url , delete_url , get_user_dashboard , get_admin_dashboard
from routes.url import get_urls_clicks_details , get_user_urls 
from operations.user import get_current_user
from observers.obs_context import lifespan
from dependencies.context import admin_context , current_user_context , new_user_context
from middlewares.central_middleware import unified_logging_and_exception_middleware
from dependencies.rate_limiter import check_rate_limit

logging.basicConfig(
    filename="Log_employee_project.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
 
app = FastAPI(lifespan = lifespan)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

@app.middleware("http")
async def add_custom_middleware(request, call_next):
    return await unified_logging_and_exception_middleware(request, call_next)

# @app.on_event("startup")
# def create_tables():
#     # if targetted database not exist , then generates the all defined db and tables 
#     Base.metadata.create_all(engine)   

@app.post("/user", response_model= UsersResponse , status_code=201)
def register_user(
    user_data: UsersRequest,
    db: Session = Depends(get_db)
):
    try:
        new_user = create_user(db , user_data)
        db.commit()
        return {
            "userid" : new_user.userid,
            "username" : new_user.username,
            "email" : new_user.email,
            "user_role" : new_user.user_role
        }
    except HTTPException:
        raise

    except Exception as e:
        db.rollback()
        logging.error(e)
        raise HTTPException(status_code=500 , detail="Internal Server Error")

    
@app.post("/admin" , response_model = UsersResponse , status_code = 201)
def register_admin(
    user_data: UsersRequest,
    admin_key : str,
    db: Session = Depends(get_db) 
): 
    try:
        new_user = create_admin(db , user_data , admin_key)
        db.commit()
        return {
            "userid" : new_user.userid,
            "username" : new_user.username,
            "email" : new_user.email,
            "user_role" : new_user.user_role
        }
    except HTTPException:
        raise

    except Exception as e:
        db.rollback()
        logging.error(e)
        raise HTTPException(status_code=500 , detail="Internal Server Error")


@app.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db) 
):
    try:
        login_token = login_with_token(db, form_data)
        return login_token

    except HTTPException:
        raise

    except Exception as e:
        db.rollback()
        logging.error(e)
        raise HTTPException(status_code=500 , detail="Internal Server Error")

@app.post("/logout" , response_model = MessageResponse)
def logout(
    token: str = Depends(oauth2_scheme), 
    context = Depends(current_user_context)
):
    db = context["db"]
    try: 
        logout = logout_route(db , token)
        return logout

    except HTTPException:
        raise
    
    except Exception as e:
        db.rollback()
        logging.error(e)
        raise HTTPException(status_code = 500 , detail="Internal Server Error")

@app.post("/url" , response_model = URLResponse , status_code=201)
def create_new_url(
    request : Request,
    req : URLRequest,
    context = Depends(current_user_context)
):
    db = context["db"]
    try:
        new_url , full_link =  create_url(db,request , req ,context["current_user"])
        return{
            "url_id":new_url.url_id,
            "url":new_url.url,
            "short_link": full_link,
            "owner_id":new_url.owner_id,
            "total_clicks":new_url.total_clicks
        }   

    except HTTPException:
        raise

    except Exception as e:
        db.rollback()
        logging.error(e)
        raise HTTPException(status_code=500 ,detail="Internal Server Error")    

def rate_limit_dependency(request: Request, db: Session = Depends(get_db)):
    client_ip = request.client.host
    check_rate_limit(db=db, identifier=client_ip, max_requests=1, window_seconds=60)

@app.get("/urls/click_stats"
, dependencies = [Depends(rate_limit_dependency)] 
, response_model = ClickStatsResponse)
def fetch_url_clicks(
    start_date: date | None = None,
    end_date: date | None = None,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    context=Depends(current_user_context,)
):
    try:
        return get_urls_clicks_details(context["db"],context["current_user"],start_date,end_date,page,limit)

    except HTTPException:
        raise

    except Exception as e:
        logging.exception("Failed to fetch click statistics", e)
        raise HTTPException(status_code=500,detail="Internal Server Error")

@app.get("/urls" , response_model = URLPageResponse)
def fetch_all_url(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    context=Depends(admin_context)
):
    try:
        return get_all_url(context["db"],context["current_user"],page,limit)

    except HTTPException:
        raise

    except Exception as e:
        logging.exception("Failed to fetch URLs",e)
        raise HTTPException(status_code=500,detail="Internal Server Error")

@app.get("/my/urls", response_model= URLPageResponse)
def fetch_user_urls(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    context=Depends(current_user_context)
):
    try:
        return get_user_urls(context["db"],context["current_user"],page,limit)

    except HTTPException:
        raise

    except Exception as e:
        logging.exception("Failed to fetch user URLs",e)
        raise HTTPException(status_code=500,detail="Internal Server Error")
        
        
@app.get("/url/{short_link}")
def fetch_url_from_short_link(
    short_link : str , 
    request : Request,
    context = Depends(new_user_context)
):
    db = context["db"]

    try:
        client_ip = request.client.host if request.client else "Unknown"
        return get_url_link(db,request,short_link,client_ip)
        db.commit()

    except HTTPException:
        raise

    except Exception as e:
        db.rollback()
        logging.exception("Failed to process the short_link redirection",e)
        raise HTTPException(status_code=500 , detail="Internal Server Error")

@app.get("/admin/dashboard" , response_model = DashboardResponse)
def fetch_admin_dashboard(
    page : int | None = None,
    limit : int | None = None,
    context = Depends(admin_context)
):
    try:
        if page and limit :
            dashboard = get_admin_dashboard(context["db"] , context["current_user"] , page , limit)
        else:
            dashboard = get_admin_dashboard(context["db"] , context["current_user"])        
        return dashboard

    except HTTPException:
        raise

    except Exception as e:
        logging.exception(e)
        raise HTTPException(status_code=500 , detail="Internal Server Error")

@app.get("/my/dashboard" , response_model = DashboardResponse)
def fetch_user_dashboard(
    page : int | None = None,
    limit : int | None = None,
    context = Depends(current_user_context)
):
    try:
        if page and limit :
            dashboard = get_user_dashboard(context["db"] , context["current_user"], page , limit)
        else:
            dashboard = get_user_dashboard(context["db"] , context["current_user"] )
        return dashboard

    except HTTPException:
        raise

    except Exception as e:
        logging.exception(e)
        raise HTTPException(status_code=500 , detail="Internal Server Error")


@app.get("/url/stats/{url_id}", response_model = URLDetailsResponse)
def get_url_stats_details(
    url_id: int,
    start_date: date | None = None,
    end_date: date | None = None,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    context=Depends(current_user_context)
):
    try:
        return get_url_stats(context["db"],url_id,context["current_user"],start_date,end_date,page,limit)

    except HTTPException:
        raise

    except Exception as e:
        logging.exception("Failed to fetch URL statistics" ,e)
        raise HTTPException(status_code=500,detail="Internal Server Error")


@app.get("/users/me" , response_model = UsersResponse)
def get_my_info(
    current_user: Users = Depends(get_current_user)
):
    return current_user

@app.get("/users/all" , response_model = list[UsersResponse])
def get_all_users(
    context = Depends(admin_context)
):
    try:
        all_users = fetch_all_user(context["db"] , context["current_user"])
        return all_users
        
    except Exception as e:
        logging.exception(e)
        raise HTTPException(status_code=500 , detail="Internal Server Error")


@app.delete("/users/delete/{userid}",
    response_model = MessageResponse ,
    status_code = 200)
def delete_single_user(
    userid : int,
    context = Depends(admin_context)
):
    db = context["db"]
    try:
        delete_req = delete_user(db , userid , context["current_user"])
        return delete_req

    except HTTPException:
        raise

    except Exception as e:
        db.rollback()
        logging.error(e)
        raise HTTPException(status_code=500 , detail="Internal Server Error")
    
     
@app.delete("/url/delete/{url_id}" ,
    response_model = MessageResponse ,
    status_code = 200)
def delete_single_url(
    url_id : int,
    context = Depends(current_user_context)
):
    db = context["db"]
    try:
        delete_req = delete_url(db , url_id , context["current_user"])
        return delete_req

    except HTTPException:
        raise

    except Exception as e:
        db.rollback()
        logging.error(e)
        raise HTTPException(status_code=500 , detail="Internal Server Error")

        
@app.get("/")
def read_root():
    return "Welcome to the URL shortener app"    