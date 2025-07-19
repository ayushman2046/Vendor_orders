from fastapi import Header, HTTPException
import os

def verify_token(authorization: str = Header(...)):
    expected_token = os.getenv("AUTH_TOKEN")
    if not expected_token or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")

    token = authorization.split("Bearer ")[1]
    if token != expected_token:
        raise HTTPException(status_code=401, detail="Invalid token")
