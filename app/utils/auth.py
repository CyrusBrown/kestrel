from fastapi import Security, HTTPException, status, Request
from fastapi.security import APIKeyHeader
import os 
import hashlib
import time
from datetime import datetime, timezone

# Define the header value that our key will be in
api_key_header = APIKeyHeader(name="Kestrel-API-Key", auto_error=False)

API_KEY = os.getenv("API_KEY") # Load the correct key from the environment variable

# The function to actually authenticate
def check_key(request: Request, api_key_header: str = Security(api_key_header)):
    if api_key_header == API_KEY:
        return "Authorized"
    else:
        # IF Username header exists get current usernamme
        if "username" in request.headers:
            if api_key_header == generate_access_token(request.headers["username"]):
                return "Authorized"
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API Key") # Raising a 401 (unauthorized) error if unauthenticated

def generate_access_token(username: str):
    # API KEY + username + current day (UTC)
    return hashlib.sha256(f"{API_KEY}{username}{datetime.now(timezone.utc).date()}")