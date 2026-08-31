import validators
from sqlalchemy import desc
from sqlalchemy.orm import Session
from fastapi import BackgroundTasks
from fastapi.exceptions import HTTPException
from fastapi import Request
from fastapi.responses import RedirectResponse
from datetime import datetime
from database.schema import Users , URL , ClickLog , URLStats
from models.url import URLRequest , URLStatsResponse
from operations.key import create_unique_random_short_link
from operations.tasks import record_click_metrics

def create_url(
    db : Session,
    url_req : URLRequest,
    current_user : Users):

    if not validators.url(url_req.url):
        raise HTTPException (status_code = 400 ,detail="Your provided URL is not valid")

    existing_url = (db.query(URL).filter(URL.url == url_req.url).order_by(desc(URL.url_id)).first())
    if (existing_url and existing_url.owner_id == current_user.userid):
        raise HTTPException (status_code = 409 ,detail=f"""You already have created link for this,Short link for that is {existing_url.short_link}""")
   
    short_link = create_unique_random_short_link(db)

    new_url = URL(
        url = url_req.url,
        short_link = short_link,
        owner_id = current_user.userid
    )
    db.add(new_url)
    db.commit()
    return new_url



def get_url_link(
    db : Session ,
    request : Request,
    background_tasks : BackgroundTasks,
    short_link : str):

    exist_url = (db.query(URL).filter(URL.short_link == short_link).order_by(desc(URL.url_id)).first())

    if exist_url is None:
        raise HTTPException(status_code=404,detail=f"{request} not found")
    referer = request.headers.get("referer")
    date_time = datetime.now()
    # exist_url.total_clicks = URL.total_clicks + 1
    background_tasks.add_task(record_click_metrics, db, exist_url.url_id, date_time , referer)

    db.commit()
    
    return RedirectResponse(exist_url.url)

def get_all_url(
    db : Session):
    return db.query(URL).all()

def get_url_stats(
    db : Session,
    url_id : str,
    current_user: Users):

    url_res = db.get(URL , url_id)
    
    try :
        if url_res.owner_id != current_user.userid and current_user.user_role != 'Admin':
            raise HTTPException(status_code = 403 , detail = "!! Access restricted !!")
        
        if url_id is None :
            # logging.warning(f"{url_id} , url not found")
            raise HTTPException(status_code = 404 , detail = "Url ID not found ")
    except Exception as e:
        raise e
    
    logs = db.query(ClickLog).filter(ClickLog.url_id == url_id).all()

    analytics = db.query(URLStats).filter(URLStats.url_id == url_id).all()

    res = []
    res.append(url_res)
    res.append(logs)
    res.append(analytics)
    return res