import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import List, Optional
import hashlib
from datetime import datetime

from database import db, create_document, get_documents

app = FastAPI(title="SaaS Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class ContactRequest(BaseModel):
    name: str
    email: EmailStr
    message: str


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


@app.get("/")
def read_root():
    return {"message": "SaaS Backend running"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    return response


# Auth endpoints
@app.post("/api/auth/register")
def register_user(payload: RegisterRequest):
    # Check if user exists
    existing = get_documents("user", {"email": payload.email}, limit=1)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user_doc = {
        "name": payload.name,
        "email": payload.email,
        "password_hash": hash_password(payload.password),
        "is_active": True,
    }
    user_id = create_document("user", user_doc)
    return {"status": "ok", "user_id": user_id}


@app.post("/api/auth/login")
def login_user(payload: LoginRequest):
    users = get_documents("user", {"email": payload.email}, limit=1)
    if not users:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    user = users[0]
    if user.get("password_hash") != hash_password(payload.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # For simplicity, return a mock token
    return {"status": "ok", "token": hash_password(payload.email + "|" + str(datetime.utcnow())), "name": user.get("name")}


# Blog endpoints
@app.get("/api/blog")
def list_blog_posts(limit: int = 6):
    posts = get_documents("blogpost", {"published_at": {"$ne": None}}, limit=limit)
    # Map to safe fields
    result = []
    for p in posts:
        result.append({
            "title": p.get("title"),
            "slug": p.get("slug"),
            "excerpt": p.get("excerpt"),
            "author": p.get("author"),
            "tags": p.get("tags", []),
            "published_at": p.get("published_at")
        })
    return {"items": result}


# Contact endpoint
@app.post("/api/contact")
def submit_contact(payload: ContactRequest):
    doc = {
        "name": payload.name,
        "email": payload.email,
        "message": payload.message,
    }
    contact_id = create_document("contact", doc)
    return {"status": "ok", "message": "Thanks for reaching out!", "id": contact_id}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
