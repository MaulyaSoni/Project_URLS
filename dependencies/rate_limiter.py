from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database.schema import RateLimit
from fastapi.exceptions import HTTPException

def check_rate_limit(
    db: Session, identifier: str, max_requests: int = 1, window_seconds: int = 60
):
  now = datetime.utcnow()
  window_limit_time = now - timedelta(seconds=window_seconds)

  # Fetch record with row locking to prevent race conditions across workers
  limit_record = (
      db.query(RateLimit)
      .filter(RateLimit.identifier == identifier)
      .with_for_update()
      .first()
  )

  if not limit_record:
    # First request from this user/IP
    limit_record = RateLimit(
        identifier=identifier, request_count=1, window_start=now
    )
    db.add(limit_record)
    db.commit()
    return

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