from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends
from fastapi import HTTPException
import os
from dotenv import load_dotenv
import time 
import streamlit as st
from jose import jwt, JWTError
load_dotenv()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],  # Added wildcard for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET_TOKEN = os.getenv("SECRET_TOKEN")
ALGORITHM = os.getenv("ALGORITHM")

def decode_token(token: str):
    try:
        return jwt.decode(token, SECRET_TOKEN, algorithms=[ALGORITHM])
    except JWTError:
        return None
security = HTTPBearer()

def get_token_from_header(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        return jwt.decode(token, SECRET_TOKEN, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=403, detail="Invalid Bearer token")

@app.get("/set_cookie")
def set_cookie(response: Response, username:str, role: str):
    payload = {
        "username": username,
        "role": role,
        "exp": time.time() + 8640000
    }
    token = jwt.encode(payload, SECRET_TOKEN, algorithm=ALGORITHM)
    response.set_cookie(
        key="auth_token",
        value=token,
        httponly=False,  # False allows JavaScript to access
        samesite="None",  # Allow cross-site requests
        secure=False,     # Set to True for HTTPS
        path="/",         # Available across the entire site
        max_age=8640000   # 100 days in seconds
    )
    return {"msg": "Token set", "token": token}

@app.get("/get_cookie")
def get_cookie(request: Request):
    token = request.cookies.get("auth_token")
    return {"auth_token": token}

@app.get("/logout")
def logout(response: Response):
    response.delete_cookie("auth_token")
    return HTMLResponse("<h3>Logged out — cookie cleared!</h3>")

@app.get("/whoami")
def whoami(user_data = dict=Depends(get_token_from_header)):
    return {"user_info": user_data}


@app.get("/protected")
def protected_route(request: Request):
    token = request.cookies.get("auth_token")
    user_data = decode_token(token) if token else None
    if not user_data:
        raise HTTPException(status_code=403, detail="Forbidden")
    return {"msg": "Access granted", "user": user_data}