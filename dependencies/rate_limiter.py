from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database.schema import RateLimit
from fastapi.exceptions import HTTPException
from fastapi import Depends , Request
from database.db import get_db

def check_rate_limit(db: Session, identifier: str, max_requests: int, window_seconds: int):
  
  now = datetime.now()
  window_limit_time = now - timedelta(seconds=window_seconds)

  # Fetch record with row locking (prevent Race Condition)
  limit_record = (
      db.query(RateLimit)
      .filter(RateLimit.identifier == identifier)
      .with_for_update() # pessimistic locking 
      .first()
  )

  if not limit_record:
    try:
      limit_record = RateLimit(identifier=identifier, request_count=1, window_start=now)
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

  if limit_record.window_start < window_limit_time:
    # Window expired; reset counter and start time
    limit_record.request_count = 1
    limit_record.window_start = now
    db.commit()
    return

  if limit_record.request_count >= max_requests:
    # Limit reached within current window
    db.rollback()
    raise HTTPException(
        status_code = 429 , 
        detail= "Too many requests. Please try again later."
    )

  # Within window and under limit; increment count
  limit_record.request_count += 1
  db.commit()


def rate_limit_dependency(request: Request, db: Session = Depends(get_db)):
  client_ip = request.client.host
  check_rate_limit(db=db, identifier=client_ip, max_requests=10, window_seconds=60)

def render_rate_limit(request : Request , db : Session = Depends(get_db)):
  client_ip = request.client.host
  check_rate_limit(db=db, identifier=client_ip, max_requests=20 , window_seconds=60)
