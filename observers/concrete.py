from observers.interface import StatsObserver
from database.db import SessionLocal
from datetime import date
from sqlalchemy.orm import Session
from fastapi.exceptions import HTTPException
from sqlalchemy.dialects.mysql import insert
from database.schema import URL, ClickLog
import logging

class ClickLogObserver(StatsObserver):
    
    def update(self , url_id: int, date_time , referer : str ,referer_domain : str, client_ip : str) -> None:

        db : Session = SessionLocal()

        new_log = ClickLog(
            url_id=url_id,
            clicked_at=date_time ,
            referer = referer ,
            referer_domain = referer_domain,
            ip = client_ip)
        
        db.add(new_log)
        db.commit()
        logging.info(f"Click_log created {date_time}")

class ClickCountObserver(StatsObserver):
    def update(self , url_id :int , date_time ,referer : str , referer_domain : str ,client_ip : str) -> None:

        db : Session = SessionLocal()

        db.query(URL).filter(URL.url_id == url_id).update(
            {
                URL.total_clicks : URL.total_clicks + 1
            },
            synchronize_session = False
        )

        logging.info(f"Total Clicks Count updated for {url_id}")
        db.commit()

class ClickMetricsObserver(StatsObserver):

    def update(self,url_id: int,date_time,referer: str,referer_domain: str,client_ip: str
    ) -> None:
        db : Session = SessionLocal()
        try:
            click_log = ClickLog(
                url_id=url_id,
                clicked_at=date_time,
                referer=referer,
                referer_domain=referer_domain,
                ip=client_ip
            )
            db.add(click_log)
            updated_rows = (
                db.query(URL)
                .filter(URL.url_id == url_id)
                .update(
                    {
                        URL.total_clicks: URL.total_clicks + 1
                    },
                    synchronize_session=False
                )
            )

            if updated_rows == 0:
                raise ValueError(f"URL with ID {url_id} does not exist")

            logging.info(f"Click metrics updated for url_id : {url_id}")

        except Exception as e:
            logging.exception("Failed to update click metrics" , e)
            raise