import validators
from datetime import datetime , date
from sqlalchemy import desc
from sqlalchemy.orm import Session
from fastapi import BackgroundTasks , Request
from fastapi.exceptions import HTTPException
from fastapi.responses import RedirectResponse
from database.schema import Users , URL , ClickLog , URLStats
from models.url import URLRequest 
from operations.key import create_unique_random_short_link
from operations.tasks import record_click_metrics
import logging
from sqlalchemy.exc import IntegrityError
from operations.query import click_count_today , overall_stats


def create_url(
    db : Session,
    url_req : URLRequest,
    current_user : Users):

    if not validators.url(url_req.url):
        raise HTTPException (status_code = 400 ,detail="Your provided URL is not valid")

    existing_url = (db.query(URL).filter(URL.url == url_req.url).order_by(desc(URL.url_id)).first())
    if (existing_url and existing_url.owner_id == current_user.userid):
        logging.warning(f"Re-perform operation for same url : '{current_user.userid}'")
        raise HTTPException (status_code = 409 ,detail=f"""You already have created link for this,Short link for that is {existing_url.short_link}""")

    short_link = create_unique_random_short_link(db)

    new_url = URL(
        url = url_req.url,
        short_link = short_link,
        owner_id = current_user.userid
    )
    db.add(new_url)
    
    logging.info(f"New short link generated : '{current_user.userid}'")
    return new_url

def get_url_link(
    db : Session ,
    request : Request,
    background_tasks : BackgroundTasks,
    short_link : str,
    client_ip : str):

    exist_url = (db.query(URL).filter(URL.short_link == short_link).order_by(desc(URL.url_id)).first())

    if exist_url is None:
        raise HTTPException(status_code=404,detail=f"Invalid Link , can't redirect to URL")

    referer = request.headers.get("referer") or "null"
    date_time = datetime.now()

    if referer is None: 
        referer = "null" 

    background_tasks.add_task(record_click_metrics, exist_url.url_id, date_time , referer , client_ip )

    return RedirectResponse(url = exist_url.url , status_code = 303)

def get_user_urls(
    db : Session,
    current_user : Users):
    owner_id = current_user.userid

    if owner_id is None:
        raise HTTPException(status_code = 404 , detail = "No details found")
 
    data = db.query(URL).filter(URL.owner_id == current_user.userid).all()

    if not data:
        raise HTTPException(status_code = 404 , detail = "User don't have created any URLs")

    return data

def get_dashboard(
    db : Session,
    current_user : Users):
    owner_id = current_user.userid

    if owner_id is None:
        raise HTTPException(status_code = 404 , detail = "No details found")

    urls = (db.query(URL).order_by(desc(URL.url_id)).all())

    logs = (db.query(ClickLog).order_by(desc(ClickLog.clicked_at)).all()) 

    # analytics = (db.query(URLStats).order_by(desc(URLStats.date),desc(URLStats.stats_id)).all())
    analytics = overall_stats(db , url_id)

    return{
        "urls":urls , "click_logs" : logs , "analytics":analytics
    }

def get_all_url(
    db : Session,
    current_user : Users):
    logging.info(f"All URL details called : '{current_user.username}")
    return db.query(URL).all()

def get_url_stats(
    db : Session,
    url_id : int,
    current_user: Users):

    url_res = db.get(URL , url_id)

    if url_res is None:
        raise HTTPException(status_code = 404 , detail = "!! URL ID not found !!")
        
    if url_res.owner_id != current_user.userid and current_user.user_role != 'Admin':
        raise HTTPException(status_code = 403 , detail = "!! Access restricted !!")

    logs = (db.query(ClickLog).filter(ClickLog.url_id == url_id).order_by(desc(ClickLog.clicked_at)).all())

    # per_day_clicks = (db.query(ClickLog).filter(ClickLog.clicked_at)).all()
    # print(per_day_clicks[0])
    # analytics = (db.query(URLStats).filter(URLStats.url_id == url_id).order_by(desc(URLStats.date) , desc(URLStats.stats_id)).all())
    
    # today's stats 
    analytics = [overall_stats(db , url_id)]
    # analytics = [f"{date.today()} : {click_count_today(db , url_id)}"]
    
    return{
        "url":url_res , "logs":logs , "stats":analytics
    }

def delete_url(
    db : Session,
    url_id : int,
    current_user : str
):
    url = db.get(URL , url_id)

    if url is None:
        raise HTTPException(status_code = 404 , detail = "URL ID not found")
        
    if url.owner_id != current_user.userid and current_user.user_role != 'Admin':
        raise HTTPException(status_code = 403 , detail = "!! Access restricted !!")

    try:
    
        db.query(ClickLog).filter(ClickLog.url_id == url_id).delete(
            synchronize_session = False)

        db.query(URLStats).filter(URLStats.url_id == url_id).delete(
            synchronize_session = False)
        
        db.delete(url)
        db.commit()
    
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code = 409 , detail=str(e))

    except Exception as e:
        db.rollback()
        raise 

    logging.info(f"ID {url_id} , url deleted by : '{current_user.username}'")
    return {"message" : f"ID - {url_id} Deleted successfully"}

