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


def apply_click_date_filters(
    query,
    start_date: date | None,
    end_date: date | None
):
    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=400,detail="start_date cannot be after end_date"
        )

    if start_date:
        query = query.filter(
            ClickLog.clicked_at >= datetime.combine(
                start_date, time.min
            )
        )

    if end_date:
        query = query.filter(
            ClickLog.clicked_at < datetime.combine(
                end_date + timedelta(days=1),
                time.min
            )
        )

    return query


def build_click_analytics(
    db: Session,
    logs_query
):
    daily_rows = (
        logs_query
        .with_entities(
            ClickLog.url_id.label("url_id"),
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

    analytics = [
        {
            "url_id": row.url_id,
            "date": row.date,
            "clicks_per_day": row.clicks
        }
        for row in daily_rows
    ]

    referer_rows = (
        logs_query
        .with_entities(
            #coalesce -> first non-null value from a list of arguments 
            func.coalesce(ClickLog.referer_domain,"Direct").label("referer_domain"),
            func.count(ClickLog.log_id).label("clicks")
        )                                                                                                                             
        .group_by(
            func.coalesce(
                ClickLog.referer_domain,"Direct"
            )
        )
        .order_by(
            desc(func.count(ClickLog.log_id))
        )
        .all()
    )

    referer_analytics = [
        {
            "referer_domain": row.referer_domain,
            "clicks": row.clicks
        }
        for row in referer_rows
    ]

    return analytics, referer_analytics