from sqlalchemy.orm import Session
from models.url import URLRequest
from schema import URL
from fastapi.exceptions import HTTPException
from schema import Users
from operations.clicks import total_clicks , clicks_per_day
from operations.converter import short_link_func

def create_url(
    db : Session,
    req : URLRequest,
    current_user : Users):

    # print(current_user)
    existing_url = (db.query(URL).filter(URL.url == req.url).first())
    if existing_url:
        raise HTTPException(status_code=409 , detail="Duplicate Data found")
    
    new_url = URL(
        url = req.url,
        short_link = short_link_func(req.url),
        owner = current_user.username
    )
    db.add(new_url)
    db.commit()
    return new_url


def get_url_stats(
    db : Session,
    url_id : str,
    current_user: Users):

    url_obj = db.get(URL , url_id)

    if URL.owner != current_user.owner:
        raise HTTPException(status_code = 403 , detail = "!! Access restricted !!")
    if url_id is None :
        # logging.warning(f"{url_id} , url not found while updating ")
        raise HTTPException(status_code = 404 , detail = "Url ID not found ")
    return url_obj    
