from datetime import datetime
from fastapi import Request
from database.schema import URL
from operations.tasks import record_click_metrics
from tests.confest import authenticated_client
from sqlalchemy.orm import Session 
from database.db import get_db , SessionLocal

def test_short_link_unique(authenticated_client):
    response1=authenticated_client.post("/url",json={"url":"https://example.com/1"})
    response2=authenticated_client.post("/url",json={"url":"https://example.com/2"})
    
    assert response1.status_code == 201
    assert response2.status_code == 201

    short_link_1 = response1.json()["short_link"]
    short_link_2 = response2.json()["short_link"]

    assert short_link_1 != short_link_2

def test_short_url_redirected(client : Request , short_link : str):
    response = client.get(f"/url/{short_link}" , follow_redirections=False)
    assert response.status_code == 303
    assert response.headers["location"] == short_link

db : Session = SessionLocal()

def test_short_url_stats(db : Session , short_link : str):
    record_click_metrics(short_link.url_id , datetime.now() , "pytest")
    record_click_metrics(short_link.url_id , datetime.now() , "pytest")
    db.refresh(short_link)

    assert short_link.total_clicks == 2  
    assert short_link.logs is not None
    assert len(short_link) == 2

