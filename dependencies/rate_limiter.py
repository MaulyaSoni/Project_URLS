from datetime import datetime, timedelta
from sqlalchemy.orm import Session
# from sqlalchemy.exe import IntegrityError
from database.schema import RateLimit
from fastapi.exceptions import HTTPException
from fastapi import Depends , Request
from database.db import get_db

def check_rate_limit(db: Session, identifier: str, max_tokens : int, refill_rate: int):
  
  now = datetime.now()

  # Fetch record with row locking (prevent Race Condition)
  limit_record = (
      db.query(RateLimit)
      .filter(RateLimit.identifier == identifier)
      .with_for_update() # pessimistic locking 
      .first()
  )

  # Cache Stempede handling for first request 
  if not limit_record:
    try:
      limit_record = RateLimit(identifier=identifier, tokens = max_tokens - 1, last_updated = now)
      db.add(limit_record)
      db.commit()
      return
    
    except IntegrityError:
      db.rollback()
    
    limit_record = (
      db.query(RateLimit)
      .filter(RateLimit.identifier == identifier)
      .with_for_update() # pessimistic locking 
      .first()
    )

  time_elapsed = (now - limit_record.last_updated).total_seconds()
  refilled_tokens = time_elapsed * refill_rate

  current_tokens =  min(max_tokens , limit_record.tokens + refilled_tokens )

  if current_tokens < 1.0 :
    db.rollback()
    raise HTTPException(
        status_code = 429 , 
        detail= "Too many requests. Please try again later."
    )
  limit_record.tokens = current_tokens - 1.0 
  limit_record.last_updated = now
  db.commit()


  # if limit_record.window_start < window_limit_time:
  #   # Window expired; reset counter and start time
  #   limit_record.request_count = 1
  #   limit_record.window_start = now
  #   db.commit()
  #   return

  # if limit_record.request_count >= max_requests:
  #   # Limit reached within current window
  #   db.rollback()
  #   raise HTTPException(
  #       status_code = 429 , 
  #       detail= "Too many requests. Please try again later."
  #   )

  # # Within window and under limit; increment count
  # limit_record.request_count += 1
  # db.commit()


def rate_limit_dependency(request: Request, db: Session = Depends(get_db)):
  client_ip = request.client.host
  check_rate_limit(db=db, identifier=client_ip, max_tokens = 10.0 , refill_rate = 10/ 60)

def render_rate_limit(request : Request , db : Session = Depends(get_db)):
  client_ip = request.client.host
  check_rate_limit(db=db, identifier=client_ip, max_tokens = 20.0 , refill_rate = 20/60)
