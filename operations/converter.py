import os 
import requests
from dotenv import load_dotenv
from fastapi import Request
load_dotenv()

SHORTURL_API_KEY = os.getenv("SHORTURL_API_KEY")

def short_link_func(url:str):
    try:
        response = requests.get(SHORTURL_API_KEY,url,timeout=5)
        response.raise_for_status()
        data = response.json()
        print(data)

    except requests.exceptions.Timeout:
            return {"error": "Unable to fetch (Request Timed Out)."}

    except requests.exceptions.ConnectionError:
        return {"error": "No Internet Connection."}

    except requests.exceptions.HTTPError:
        return {"error": "Service returned an error."}

    except Exception:
        return {"error": "Nationality Prediction Service unavailable."}