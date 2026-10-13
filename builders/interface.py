from dataclasses import dataclass
from models.url import URLResponse , ClickLogResponse , AnalyticsResponse

@dataclass(frozen = True)
class BuilderStatsInterface:
    urls: list[URLResponse]
    click_logs : list[ClickLogResponse]
    daily_clicks_response : list[AnalyticsResponse]
