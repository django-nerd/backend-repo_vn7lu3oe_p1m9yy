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

from pydantic import BaseModel, Field
from typing import Optional, List

# Core domain schemas for the Rolex-style watch site

class Watch(BaseModel):
    """
    Luxury watches catalog
    Collection name: "watch"
    """
    name: str = Field(..., description="Watch name")
    brand: str = Field("Rolex", description="Brand name")
    price: float = Field(..., ge=0, description="Price in USD")
    description: str = Field(..., description="Short description")
    image: str = Field(..., description="Image URL")
    slug: str = Field(..., description="URL-friendly identifier")
    in_stock: bool = Field(True, description="Availability status")

class BlogPost(BaseModel):
    """
    Editorial blog articles
    Collection name: "blogpost"
    """
    title: str = Field(..., description="Post title")
    excerpt: str = Field(..., description="Short excerpt")
    content: str = Field(..., description="Full content (markdown supported)")
    cover_image: str = Field(..., description="Cover image URL")
    author: str = Field(..., description="Author name")
    slug: str = Field(..., description="URL-friendly identifier")

class OrderItem(BaseModel):
    slug: str
    name: str
    price: float
    quantity: int = Field(1, ge=1, le=10)

class Order(BaseModel):
    """
    Customer checkout orders (simulated payments)
    Collection name: "order"
    """
    customer_name: str
    customer_email: str
    customer_phone: Optional[str] = None
    items: List[OrderItem]
    subtotal: float = Field(..., ge=0)
    status: str = Field("pending", description="pending | confirmed | failed")

# Example schemas retained for reference (not used directly by app)
class User(BaseModel):
    name: str
    email: str
    address: str
    age: Optional[int] = None
    is_active: bool = True

class Product(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    category: str
    in_stock: bool = True
