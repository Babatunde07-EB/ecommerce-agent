import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import List, Optional
from fastapi.responses import FileResponse
from .agent import CommerceAgent
from .data_store import OrderItem

app = FastAPI(title="Commerce Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

agent = CommerceAgent()

class RecommendationRequest(BaseModel):
    user_id: str
    current_context: Optional[str] = None

class OrderRequest(BaseModel):
    user_id: str
    items: List[OrderItem]

class SupportRequest(BaseModel):
    user_id: str
    inquiry: str

class CampaignRequest(BaseModel):
    name: str
    audience: str
    objective: str
    channels: List[str]
    offer: Optional[str] = None

@app.post("/recommendations")
async def recommendations(request: RecommendationRequest):
    result = agent.recommend_products(request.user_id, request.current_context)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

@app.post("/orders/create")
async def create_order(request: OrderRequest):
    result = agent.process_order(request.user_id, request.items)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@app.get("/orders/{order_id}")
async def get_order(order_id: str):
    order = agent.store.get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@app.post("/customer-support")
async def customer_support(request: SupportRequest):
    return agent.handle_support(request.user_id, request.inquiry)

@app.post("/campaigns/create")
async def create_campaign(request: CampaignRequest):
    return agent.create_campaign(request.name, request.audience, request.objective, request.channels, request.offer)

@app.get("/health")
async def health():
    return {"status": "ok", "model": "claude-opus-4-7"}

frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")

    @app.get("/")
    async def root():
        return FileResponse(os.path.join(frontend_path, "index.html"))
