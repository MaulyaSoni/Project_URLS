from datetime import datetime
from database.schema import URL , ClickLog , URLStats
from operations.tasks import record_click_metrics
from tests.conftest import authenticated_client , created_url

def test_short_link_unique(authenticated_client):
    response1=authenticated_client.post("/url",json={"url":"https://example.com/1"})
    response2=authenticated_client.post("/url",json={"url":"https://example.com/2"})
    
    assert response1.status_code == 201
    assert response2.status_code == 201

    short_link_1 = response1.json()["short_link"]
    short_link_2 = response2.json()["short_link"]

    assert short_link_1 != short_link_2

def test_short_url_redirected(client , created_url):
    response = client.get(
        f"/url/{created_url.short_link}" ,
        follow_redirects=False
    )
    assert response.status_code == 303
    assert response.headers["location"] == created_url.url


def test_short_url_stats(db, created_url):
    record_click_metrics(created_url.url_id , datetime.now() , "pytest" , "127.0.0.1" )
    record_click_metrics(created_url.url_id , datetime.now() , "pytest" , "127.0.0.1")
    
    db.add(created_url)
    db.commit()
    url = db.get(URL , created_url.url_id)
    print(url.url_id , url.total_clicks)    
    assert url is not None
    assert url.total_clicks == 2

    logs = (
        db.query(ClickLog).filter(ClickLog.url_id == created_url.url_id).all()
        )

    print(ClickLog.url_id)
    assert len(logs) == 2

    stats = (
        db.query(URLStats).filter(URLStats.url_id == created_url.url_id).all()
    )

    assert len(stats) == 1
    assert stats[0].clicks_per_day == 2