from contextlib import asynccontextmanager
from fastapi import FastAPI
from observers.concrete import ClickLogObserver, ClickCountObserver
from observers.subject import stats_obs

@asynccontextmanager
async def lifespan(app: FastAPI):

    stats_obs.add(ClickLogObserver())
    stats_obs.add(ClickCountObserver())
    yield

    # clear when server stops for restarting the server , a safety cache
    stats_obs._observers.clear()
