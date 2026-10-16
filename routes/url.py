import os
import logging
from math import ceil
import validators
from dotenv import load_dotenv
from datetime import datetime , date , time , timedelta
from urllib.parse import urlparse
from sqlalchemy import desc , func
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import BackgroundTasks , Request
from fastapi.exceptions import HTTPException
from fastapi.responses import RedirectResponse
from database.schema import Users , URL , ClickLog 
from models.url import URLRequest 
from operations.key import create_unique_random_short_link
from operations.tasks import record_click_metrics
from observers.subject import stats_obs
from builders.builder import StatsBuilderClass
from operations.analytics import apply_click_date_filters , build_click_analytics 

def create_url(
    db : Session,
    request : Request,
    url_req : URLRequest,
    current_user : Users
    ):

    if not validators.url(url_req.url):
        raise HTTPException(status_code = 400 ,detail="Your provided URL is not valid")

    existing_url = (
        db.query(URL)
        .filter(URL.url == url_req.url)
        .order_by(desc(URL.url_id))
        .first()
    )

    base_url = os.getenv("BASE_URL")
    base_domain = str(request.base_url).rstrip("/")

    if (existing_url and existing_url.owner_id == current_user.userid):
        logging.warning(f"Re-perform operation for same url : '{current_user.userid}'")
        
        raise HTTPException(
            status_code = 409,
            detail=
                {
                    "message":"You already have created link for this",
                    "short_link":f"{base_domain}/url/{existing_url.short_link}"
                }
        )

    short_link = create_unique_random_short_link(db)
    full_short_link = f"{base_domain}/url/{short_link}"

    new_url = URL(
        url = url_req.url,
        short_link = short_link,
        owner_id = current_user.userid
    )

    db.add(new_url)
    db.commit()
    logging.info(f"New short link generated : '{current_user.userid}'")
    return new_url , full_short_link

def get_url_link(
    db : Session ,
    request : Request,
    short_link : str,
    client_ip : str
    ):

    exist_url = (
        db.query(URL)
        .filter(URL.short_link == short_link)
        .order_by(desc(URL.url_id)).
        first()
    )

    if exist_url is None:
        raise HTTPException(status_code=404,detail=f"Invalid Link , can't redirect to URL")

    referer = request.headers.get("referer") or "null"
    
    if referer : 
        referer_domain = urlparse(referer).hostname or "Unknown"
    
    else:
        referer = "Direct"
        referer_domain = "Direct"

    date_time = datetime.now()

    stats_obs.notify_observers(
        url_id = exist_url.url_id, 
        date_time = date_time , 
        referer =  referer , 
        referer_domain = referer_domain,
        client_ip = client_ip
    )

    return RedirectResponse(url = exist_url.url , status_code = 303)

# def get_user_urls(
#     db: Session,
#     current_user: Users,
#     page: int = 1,
#     limit: int = 10
# ):
#     query = (
#         db.query(URL)
#         .filter(URL.owner_id == current_user.userid)
#         .order_by(desc(URL.url_id))
#     )

#     total = query.count()

#     urls = (
#         query
#         .offset((page - 1) * limit)
#         .limit(limit)
#         .all()
#     )

#     return {
#         "items": urls,
#         "page": page,
#         "limit": limit,
#         "total": total,
#         "total_pages": ceil(total / limit) if total else 0
#     }
def get_user_urls(
    db: Session,
    current_user: Users,
    page: int = 1,
    limit: int = 10
    ):

    if current_user.userid is None:
        raise HTTPException(status_code=404,detail="No details found")

    data = (
        StatsBuilderClass()
        .add_urls(
            db=db,
            owner_id=current_user.userid,
            page=page,
            limit=limit
        )
        .build()
    )

    return {
        "items": data.urls,
        **data.url_pagination
    }

def get_urls_clicks_details(
    db: Session,
    current_user: Users,
    start_date: date | None = None,
    end_date: date | None = None,
    page: int = 1,
    limit: int = 10
):
    logs_query = (
        db.query(ClickLog)
        .join(URL, ClickLog.url_id == URL.url_id)
        .filter(URL.owner_id == current_user.userid)
    )

    logs_query = apply_click_date_filters(logs_query,start_date,end_date)

    total = logs_query.count()

    analytics, referer_analytics = build_click_analytics(db,logs_query)

    click_logs = (
        logs_query
        .order_by(
            desc(ClickLog.clicked_at),
            desc(ClickLog.log_id)
        )
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    return {
        "click_logs": click_logs,
        "analytics": analytics,
        "referer_analytics": referer_analytics,
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": ceil(total / limit) if total else 0
    }

def get_user_dashboard(
    db : Session,
    current_user : Users):
    owner_id = current_user.userid

    if owner_id is None:
        raise HTTPException(status_code = 404 , detail = "No details found")

    builder = StatsBuilderClass()

    data = (
        builder
        .add_urls(db = db , owner_id = owner_id) 
        .add_logs(db = db , owner_id = owner_id)
        .add_daily_clicks(db = db , owner_id = owner_id)
        .build()
    )

    return data 

def get_admin_dashboard(
    db : Session ,
    current_user : Users):
    owner_id = current_user.userid

    if owner_id is None:
        raise HTTPException(status_code = 404 , detail = "No details found")
    
    urls = (db.query(URL).order_by(desc(URL.url_id)).all())
    logs = (db.query(ClickLog).order_by(desc(ClickLog.clicked_at)).all()) 

    daily_clicks = (
        db.query(
            ClickLog.url_id,
            func.date(ClickLog.clicked_at).label("date"), 
            func.count(ClickLog.log_id).label("clicks")
        )
        .group_by(
            ClickLog.url_id, 
            func.date(ClickLog.clicked_at)
        )
        .order_by(
            desc(func.date(ClickLog.clicked_at))
        )
        .all()
    )
    daily_clicks_response = [ 
        {
            "url_id": row.url_id, 
            "date": row.date,
            "clicks_per_day": row.clicks 
        } 
        for row in daily_clicks 
    ]

    return{
        "urls":urls , "click_logs" : logs , "analytics":daily_clicks_response    
    }
 
# def get_all_url(
#     db: Session,
#     current_user: Users,
#     page: int = 1,
#     limit: int = 10
# ):
#     query = db.query(URL).order_by(desc(URL.url_id))

#     total = query.count()

#     urls = (
#         query
#         .offset((page - 1) * limit)
#         .limit(limit)
#         .all()
#     )

#     return {
#         "items": urls,
#         "page": page,
#         "limit": limit,
#         "total": total,
#         "total_pages": ceil(total / limit) if total else 0
#     }
def get_all_url(
    db: Session,
    current_user: Users,
    page: int = 1,
    limit: int = 10
    ):
    
    data = (
        StatsBuilderClass()
        .add_urls(
            db=db,
            page=page,
            limit=limit,
            all_urls=True
        )
    .build()
    )

    return {
        "items": data.urls,
        **data.url_pagination
    }

def get_url_stats(
    db: Session,
    url_id: int,
    current_user: Users,
    start_date: date | None = None,
    end_date: date | None = None,
    page: int = 1,
    limit: int = 10
):
    url_res = db.get(URL, url_id)

    if url_res is None:
        raise HTTPException(status_code=404,detail="URL ID not found")

    if (url_res.owner_id != current_user.userid and current_user.user_role != "Admin"):
        raise HTTPException(status_code=403,detail="Access restricted")

    logs_query = db.query(ClickLog).filter(
        ClickLog.url_id == url_id
    )

    logs_query = apply_click_date_filters(logs_query,start_date,end_date)

    total = logs_query.count()

    analytics, referer_analytics = build_click_analytics(db,logs_query)

    click_logs = (
        logs_query
        .order_by(
            desc(ClickLog.clicked_at),desc(ClickLog.log_id)
        )
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    return {
        "url": url_res,
        "click_logs": click_logs,
        "analytics": analytics,
        "referer_analytics": referer_analytics,
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": ceil(total / limit) if total else 0
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

        db.delete(url)
        db.commit()
    
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code = 409 , detail=str(e))


    except Exception as e:
        db.rollback()
        logging.exception(e)
        raise 

    logging.info(f"ID {url_id} , url deleted by : '{current_user.username}'")
    return {
        "message" : f"ID - {url_id} Deleted successfully"
        }


# def delete_all(
#     db : Session,
#     current_user : Users
# ):
#     c1 = db.query(URL).all()
#     db.delete(c1)
#     db.commit()
