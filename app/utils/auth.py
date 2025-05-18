from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
import os 

# Define the header value that our key will be in
api_key_header = APIKeyHeader(name="Kestrel-API-Key", auto_error=False)

# The function to actually authenticate
def check_key(api_key_header: str = Security(api_key_header)):
    api_key = os.getenv("API_KEY") # Load the correct key from the environment variable
    if api_key_header == api_key:
        return "Authorized"
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API Key") # Raising a 401 (unauthorized) error if unauthenticated