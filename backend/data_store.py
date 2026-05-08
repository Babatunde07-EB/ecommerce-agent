import uuid
from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel

class Product(BaseModel):
    id: str
    name: str
    category: str
    price: float
    tags: List[str]
    description: str

class UserProfile(BaseModel):
    id: str
    name: str
    segment: str
    preferred_categories: List[str]
    purchase_history: List[str]
    loyalty_tier: str

class OrderItem(BaseModel):
    product_id: str
    quantity: int

class Order(BaseModel):
    id: str
    user_id: str
    items: List[OrderItem]
    status: str
    total_amount: float
    created_at: datetime
    updated_at: datetime

class Campaign(BaseModel):
    id: str
    name: str
    audience: str
    channels: List[str]
    objective: str
    message: str
    created_at: datetime
    status: str

class DataStore:
    def __init__(self):
        self.products: Dict[str, Product] = {
            "P1001": Product(
                id="P1001",
                name="Velocity Smart Trainer",
                category="Fitness",
                price=299.99,
                tags=["wearable", "connected", "fitness"],
                description="A smart fitness band with workout coaching, sleep tracking, and on-device AI guidance.",
            ),
            "P1002": Product(
                id="P1002",
                name="EcoBrew Coffee Maker",
                category="Home",
                price=159.95,
                tags=["kitchen", "sustainability", "automatic"],
                description="A low-waste coffee maker with adaptive brew profiles and voice control.",
            ),
            "P1003": Product(
                id="P1003",
                name="Aura Pro Noise-Cancelling Headphones",
                category="Electronics",
                price=219.00,
                tags=["audio", "travel", "comfort"],
                description="Premium headphones engineered for long flights, remote work, and immersive audio." ,
            ),
            "P1004": Product(
                id="P1004",
                name="HomeGlow Smart Light Kit",
                category="Home",
                price=79.99,
                tags=["lighting", "smart home", "ambience"],
                description="A connected smart lighting kit for mood scenes, schedules, and voice automation.",
            ),
        }

        self.users: Dict[str, UserProfile] = {
            "U1001": UserProfile(
                id="U1001",
                name="Maya Patel",
                segment="urban professional",
                preferred_categories=["Electronics", "Fitness"],
                purchase_history=["P1001"],
                loyalty_tier="gold",
            ),
            "U1002": UserProfile(
                id="U1002",
                name="Noah Chen",
                segment="young family",
                preferred_categories=["Home", "Kitchen"],
                purchase_history=["P1002"],
                loyalty_tier="silver",
            ),
        }

        self.orders: Dict[str, Order] = {}
        self.campaigns: Dict[str, Campaign] = {}

    def get_user(self, user_id: str) -> Optional[UserProfile]:
        return self.users.get(user_id)

    def get_product(self, product_id: str) -> Optional[Product]:
        return self.products.get(product_id)

    def search_products(self, categories: List[str], keywords: Optional[str] = None) -> List[Product]:
        results = []
        normalized_keywords = keywords.lower() if keywords else None
        for product in self.products.values():
            if product.category in categories or any(tag in categories for tag in product.tags):
                if not normalized_keywords:
                    results.append(product)
                elif normalized_keywords in product.name.lower() or normalized_keywords in product.description.lower():
                    results.append(product)
        return results

    def recommend_products(self, user_id: str, context: Optional[str] = None) -> List[Product]:
        user = self.get_user(user_id)
        if not user:
            return []

        categories = list(user.preferred_categories)
        if context and "sleep" in context.lower():
            categories.append("Home")
        if context and "fitness" in context.lower():
            categories.append("Fitness")

        products = self.search_products(categories, keywords=context)
        if not products:
            products = list(self.products.values())

        return products[:3]

    def create_order(self, user_id: str, items: List[OrderItem]) -> Order:
        total = 0.0
        for item in items:
            product = self.get_product(item.product_id)
            if product:
                total += product.price * item.quantity

        order_id = str(uuid.uuid4())
        now = datetime.utcnow()
        order = Order(
            id=order_id,
            user_id=user_id,
            items=items,
            status="pending",
            total_amount=round(total, 2),
            created_at=now,
            updated_at=now,
        )
        self.orders[order_id] = order
        return order

    def get_order(self, order_id: str) -> Optional[Order]:
        return self.orders.get(order_id)

    def update_order_status(self, order_id: str, status: str) -> Optional[Order]:
        order = self.get_order(order_id)
        if order:
            order.status = status
            order.updated_at = datetime.utcnow()
        return order

    def create_campaign(self, name: str, audience: str, channels: List[str], objective: str, message: str) -> Campaign:
        campaign_id = str(uuid.uuid4())
        campaign = Campaign(
            id=campaign_id,
            name=name,
            audience=audience,
            channels=channels,
            objective=objective,
            message=message,
            created_at=datetime.utcnow(),
            status="draft",
        )
        self.campaigns[campaign_id] = campaign
        return campaign

    def get_campaign(self, campaign_id: str) -> Optional[Campaign]:
        return self.campaigns.get(campaign_id)
