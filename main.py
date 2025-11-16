import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

from database import db, create_document, get_documents
from schemas import Watch, BlogPost, Order, OrderItem

app = FastAPI(title="LuxTime API", description="Backend for a luxury watch brand with blog and payments")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "LuxTime Backend Running"}

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
            response["database_name"] = os.getenv("DATABASE_NAME") or "❌ Not Set"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
                response["connection_status"] = "Connected"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    return response

# Seed utility for demo content
class SeedResponse(BaseModel):
    inserted: int

@app.post("/seed", response_model=SeedResponse)
def seed_demo_content():
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")

    # Only seed if empty
    existing_watches = db["watch"].count_documents({})
    existing_posts = db["blogpost"].count_documents({})

    inserted = 0
    if existing_watches == 0:
        demo_watches = [
            {
                "name": "Cosmograph Daytona",
                "brand": "Rolex",
                "price": 14999.0,
                "description": "Iconic chronograph crafted in Oystersteel with Cerachrom bezel.",
                "image": "https://images.unsplash.com/photo-1548171916-c0dea5c53030?q=80&w=1600&auto=format&fit=crop",
                "slug": "cosmograph-daytona",
                "in_stock": True,
            },
            {
                "name": "Submariner Date",
                "brand": "Rolex",
                "price": 12999.0,
                "description": "The archetype of the diver's watch with Oyster bracelet.",
                "image": "https://images.unsplash.com/photo-1524805444758-089113d48a6d?q=80&w=1600&auto=format&fit=crop",
                "slug": "submariner-date",
                "in_stock": True,
            },
            {
                "name": "GMT-Master II",
                "brand": "Rolex",
                "price": 13999.0,
                "description": "Designed to show the time in two different time zones simultaneously.",
                "image": "https://images.unsplash.com/photo-1594535182308-8ffb6d6b8a34?q=80&w=1600&auto=format&fit=crop",
                "slug": "gmt-master-ii",
                "in_stock": True,
            },
        ]
        for w in demo_watches:
            create_document("watch", w)
            inserted += 1

    if existing_posts == 0:
        demo_posts = [
            {
                "title": "The Art of Precision",
                "excerpt": "Inside the craftsmanship that defines a legend.",
                "content": "Precision is not an act, but a habit. Our timepieces embody decades of innovation and mastery.",
                "cover_image": "https://images.unsplash.com/photo-1490367532201-b9bc1dc483f6?q=80&w=1600&auto=format&fit=crop",
                "author": "Editorial Team",
                "slug": "the-art-of-precision"
            },
            {
                "title": "Diving into Excellence",
                "excerpt": "Why divers trust our iconic Submariner.",
                "content": "From the depths of the ocean to the boardroom, a symbol of performance and style.",
                "cover_image": "https://images.unsplash.com/photo-1514890547357-a9ee0b733005?q=80&w=1600&auto=format&fit=crop",
                "author": "Editorial Team",
                "slug": "diving-into-excellence"
            }
        ]
        for p in demo_posts:
            create_document("blogpost", p)
            inserted += 1

    return {"inserted": inserted}

# Catalog endpoints
@app.get("/watches", response_model=List[Watch])
def list_watches():
    docs = get_documents("watch")
    # Convert _id to str-safe items
    cleaned = []
    for d in docs:
        d.pop("_id", None)
        cleaned.append(Watch(**d))
    return cleaned

@app.get("/watches/{slug}", response_model=Watch)
def get_watch(slug: str):
    docs = get_documents("watch", {"slug": slug}, limit=1)
    if not docs:
        raise HTTPException(status_code=404, detail="Watch not found")
    d = docs[0]
    d.pop("_id", None)
    return Watch(**d)

# Blog endpoints
@app.get("/blog", response_model=List[BlogPost])
def list_posts():
    docs = get_documents("blogpost")
    cleaned = []
    for d in docs:
        d.pop("_id", None)
        cleaned.append(BlogPost(**d))
    return cleaned

@app.get("/blog/{slug}", response_model=BlogPost)
def get_post(slug: str):
    docs = get_documents("blogpost", {"slug": slug}, limit=1)
    if not docs:
        raise HTTPException(status_code=404, detail="Post not found")
    d = docs[0]
    d.pop("_id", None)
    return BlogPost(**d)

# Payments (simulated) endpoints
class CheckoutRequest(BaseModel):
    customer_name: str
    customer_email: str
    items: List[OrderItem]

class CheckoutResponse(BaseModel):
    order_id: str
    status: str
    subtotal: float

@app.post("/checkout", response_model=CheckoutResponse)
def checkout(payload: CheckoutRequest):
    # calculate subtotal
    subtotal = sum(i.price * i.quantity for i in payload.items)
    order = Order(
        customer_name=payload.customer_name,
        customer_email=payload.customer_email,
        items=payload.items,
        subtotal=subtotal,
        status="confirmed",  # simulate success
    )
    order_id = create_document("order", order)
    return {"order_id": order_id, "status": "confirmed", "subtotal": subtotal}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
