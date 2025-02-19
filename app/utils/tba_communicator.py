import requests
import os
from dotenv import load_dotenv

load_dotenv()

def get_api_key():
    return os.getenv("TBA_KEY")

async def tba_request(api_url):
    request = None
    full_url = f"https://www.thebluealliance.com/api/v3/{api_url}"
    request_headers = {"X-TBA-Auth-Key": get_api_key()}
    print(f"starting api request to {full_url}")
    try:
        request = requests.get(full_url, headers=request_headers)
        print(f"finished api request from {full_url}")
    except requests.exceptions.ConnectionError:
        print(f"ERROR: No internet")
        return None

    if request.status_code == 200:
        return request.json()
    