"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogpost" collection
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime

# SaaS App Schemas

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user"
    """
    name: str = Field(..., description="Full name")
    email: EmailStr = Field(..., description="Email address")
    password_hash: str = Field(..., description="Hashed password")
    is_active: bool = Field(True, description="Whether user is active")

class Blogpost(BaseModel):
    """
    Blog posts collection schema
    Collection name: "blogpost"
    """
    title: str
    slug: str
    excerpt: Optional[str] = None
    content: str
    author: str
    tags: List[str] = []
    published_at: Optional[datetime] = None
    featured: bool = False

class Contact(BaseModel):
    """
    Contact messages collection schema
    Collection name: "contact"
    """
    name: str
    email: EmailStr
    message: str

# Legacy examples (kept for reference)
class Product(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    category: str
    in_stock: bool = True
