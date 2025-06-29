import os
import requests
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../..', '.env'))
API_KEY = os.getenv("SNCF_API_KEY")
HEADERS = {"Authorization": API_KEY}

def get_trains(from_id, to_id):
    url = f"https://api.sncf.com/v1/coverage/sncf/journeys?from={from_id}&to={to_id}&count=10&data_freshness=realtime"
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        return []
    return response.json().get("journeys", [])