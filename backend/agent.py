import os
from typing import List, Optional
import anthropic
from .data_store import DataStore, OrderItem

SYSTEM_PROMPT = """You are CommerceAI, an intelligent commerce operations agent for a digital storefront.
You manage personalized product recommendations, automate order processing, resolve complex customer service requests,
and orchestrate dynamic marketing campaigns.

Your responsibilities include:
- Using customer profile and purchase history to suggest relevant products.
- Validating and creating order data for fulfillment.
- Answering support questions with empathy, clarity, and operational context.
- Designing campaign briefs that are aligned with audience segments and launch channels.

When answering, produce structured, actionable recommendations and include any relevant next step for the user.
"""

class CommerceAgent:
    def __init__(self, model_name: str = "claude-opus-4-7"):
        self.client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        self.model_name = model_name
        self.store = DataStore()

    def _call_model(self, prompt: str, max_tokens: int = 600) -> str:
        response = self.client.messages.create(
            model=self.model_name,
            max_tokens=max_tokens,
            system=[
                {
                    "type": "text",
                    "text": SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=[{"role": "user", "content": prompt}],
        )

        return next((block.text for block in response.content if block.type == "text"), "")

    def recommend_products(self, user_id: str, current_context: Optional[str] = None) -> dict:
        user = self.store.get_user(user_id)
        if not user:
            return {"error": f"User {user_id} not found."}

        products = self.store.recommend_products(user_id, current_context)
        product_summary = "\n".join(
            [f"- {product.name} ({product.category}) — ${product.price}: {product.description}" for product in products]
        )

        prompt = f"Provide personalized product recommendations for {user.name}.\n\nCustomer profile:\n- Segment: {user.segment}\n- Loyalty tier: {user.loyalty_tier}\n- Preferred categories: {', '.join(user.preferred_categories)}\n- Purchase history: {', '.join(user.purchase_history)}\n\nRecommended products:\n{product_summary}\n\nContext: {current_context or 'No additional context provided.'}\n\nExplain why each product is a good fit and suggest the next best action."
        assistant_text = self._call_model(prompt)

        return {
            "user_id": user_id,
            "recommendations": [product.dict() for product in products],
            "assistant_message": assistant_text,
        }

    def process_order(self, user_id: str, items: List[OrderItem]) -> dict:
        user = self.store.get_user(user_id)
        if not user:
            return {"error": f"User {user_id} not found."}

        if not items:
            return {"error": "No order items provided."}

        order = self.store.create_order(user_id, items)
        prompt = f"You have created a new order for {user.name}.\n\nOrder ID: {order.id}\nTotal: ${order.total_amount}\nItems:\n" + "\n".join(
            [f'- {item.quantity} x {self.store.get_product(item.product_id).name if self.store.get_product(item.product_id) else item.product_id}' for item in items]
        ) + "\n\nWrite an order confirmation message that includes next fulfillment and shipment steps." 

        assistant_text = self._call_model(prompt)
        return {
            "order_id": order.id,
            "status": order.status,
            "total_amount": order.total_amount,
            "assistant_message": assistant_text,
        }

    def handle_support(self, user_id: str, inquiry: str) -> dict:
        user = self.store.get_user(user_id)
        profile_text = "unknown user" if not user else f"{user.name}, segment {user.segment}, loyalty {user.loyalty_tier}"
        prompt = f"You are answering a customer support inquiry for {profile_text}.\n\nInquiry:\n{inquiry}\n\nRespond with empathy, clear resolution steps, and if required, mention order follow-up or escalation." 

        assistant_text = self._call_model(prompt)
        return {
            "user_id": user_id,
            "support_response": assistant_text,
        }

    def create_campaign(
        self,
        name: str,
        audience: str,
        objective: str,
        channels: List[str],
        offer: Optional[str] = None,
    ) -> dict:
        message = f"Launch a {objective} campaign targeting {audience} through {', '.join(channels)}."
        if offer:
            message += f" Include this promotional offer: {offer}."

        prompt = (
            f"Design a marketing campaign brief for the following request:\n"
            f"Name: {name}\n"
            f"Audience: {audience}\n"
            f"Objective: {objective}\n"
            f"Channels: {', '.join(channels)}\n"
            f"Offer: {offer or 'None'}\n\n"
            f"Produce a short campaign outline, key messaging, launch sequence, and measurement metrics."
        )
        assistant_text = self._call_model(prompt)
        campaign = self.store.create_campaign(name, audience, channels, objective, assistant_text)
        return {
            "campaign_id": campaign.id,
            "campaign_details": campaign.dict(),
            "assistant_message": assistant_text,
        }
