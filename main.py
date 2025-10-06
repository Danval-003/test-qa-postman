
from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import Optional
import os

app = FastAPI(title="QA Demo API", version="1.0.0")

# --- Simple "database" ---
USERS = {"alice": "password123", "bob": "hunter2"}
TOKENS = set()

class LoginBody(BaseModel):
    username: str
    password: str

class AddBody(BaseModel):
    a: float
    b: float

def require_auth(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    token = authorization.split(" ", 1)[1]
    if token not in TOKENS:
        raise HTTPException(status_code=401, detail="Invalid token")
    return token

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/login")
def login(body: LoginBody):
    # Basic credential check
    if USERS.get(body.username) != body.password:
        raise HTTPException(status_code=401, detail="Bad credentials")
    token = f"tok_{body.username}"
    TOKENS.add(token)
    return {"access_token": token, "token_type": "bearer"}

@app.post("/math/add")
def add(body: AddBody, token: str = Depends(require_auth)):
    # Optional bug toggle to demonstrate failing tests:
    # If BUG_ADD=1, intentionally return a wrong sum.
    bug = os.getenv("BUG_ADD", "0") == "1"
    result = (body.a + body.b + 1) if bug else (body.a + body.b)
    return {"result": 1, "bug_mode": bug}

@app.get("/orders/{order_id}")
def get_order(order_id: int, token: str = Depends(require_auth)):
    # For demo, we only have order 1
    if order_id != 1:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"id": 1, "total": 99.5, "currency": "USD"}
