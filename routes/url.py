import validators
from sqlalchemy import desc
from sqlalchemy.orm import Session
from models.url import URLRequest , URLStatsResponse , URLUserResponse
from fastapi.exceptions import HTTPException
from fastapi import Request
from database.schema import Users , URL
from fastapi.responses import RedirectResponse
from operations.key import create_random_key , create_unique_random_short_link


def create_url(
    db : Session,
    url_req : URLRequest,
    current_user : Users):

    if not validators.url(url_req.url):
        raise HTTPException (status_code = 400 ,detail="Your provided URL is not valid")

    existing_url = (db.query(URL).filter(URL.url == url_req.url).order_by(desc(URL.url_id)).first())
    # print(existing_url.owner_id , current_user.userid)
    if (existing_url and existing_url.owner_id == current_user.userid):
        raise HTTPException (status_code = 409 ,detail=f"""You already have created link for this,Short link for that is {existing_url.short_link}""")
   
    short_link = create_unique_random_short_link(db)
    secret_key = create_random_key(length = 10)

    new_url = URL(
        url = url_req.url,
        short_link = short_link,
        secret_key = secret_key,
        owner_id = current_user.userid
    )
    db.add(new_url)
    db.commit()
    return new_url

def get_url_link(
    db : Session ,
    request : Request,
    short_link : str):

    exist_url = (db.query(URL).filter(URL.short_link == short_link).order_by(desc(URL.url_id)).first())
    # print(URL.short_link , exist_url)
    if exist_url is None:
        raise HTTPException(status_code=404,detail=f"{request} not found")

    exist_url.total_clicks = URL.total_clicks + 1

    db.commit()

    return RedirectResponse(exist_url.url)

def get_all_url(
    db : Session):
    return db.query(URL).all()

def url_stats_key(
    db : Session,
    secret_key : str):

    existing_url = db.query(URL).filter(URL.secret_key == secret_key).all()
    # existing_url = db.get(URL , secret_key)
 
    if existing_url is None:
        raise HTTPException(status_code = 404 , detail= "!! Resource not found !! Secret key invalid ")    

    return existing_url

def url_stats_id(
    db : Session,
    url_id : str,
    current_user: Users):

    url_res = db.get(URL , url_id)
    # print(url_res.owner_id , current_user.userid, current_user.user_role)

    if url_res.owner_id != current_user.userid and current_user.user_role != 'Admin':
        raise HTTPException(status_code = 403 , detail = "!! Access restricted !!")
    
    if url_id is None :
        # logging.warning(f"{url_id} , url  ")
        raise HTTPException(status_code = 404 , detail = "Url ID not found ")

    return url_res 