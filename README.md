# Commerce Agent

A next-generation commerce orchestration agent that:

- Manages personalized product recommendations
- Automates order processing and fulfillment workflows
- Handles complex customer service inquiries beyond a simple chatbot
- Orchestrates dynamic marketing campaigns

## Install

1. Open a command prompt in `commerce-agent`.
2. Install dependencies:

   python -m pip install -r requirements.txt

## Run

1. Set your Anthropic API key:

   set ANTHROPIC_API_KEY=your_api_key_here

2. Start the app:

   start.bat

3. Open `http://127.0.0.1:8001` in your browser.

## Project structure

- `backend/main.py`: FastAPI API server with commerce agent endpoints
- `backend/agent.py`: Agent orchestration logic
- `backend/data_store.py`: Sample product, user, order, and campaign data
- `frontend/index.html`: Simple UI for interacting with the agent

## Endpoints

- `POST /recommendations`
- `POST /orders/create`
- `GET /orders/{order_id}`
- `POST /customer-support`
- `POST /campaigns/create`
- `GET /health`
