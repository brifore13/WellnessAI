# Benny AI Service

AI microservice for wellness coaching powered by Azure OpenAI. Provides conversational chat and personalized wellness recommendations.

## Tech Stack

- **Framework**: FastAPI (async)
- **AI**: Azure OpenAI (GPT-3.5/4)
- **Validation**: Pydantic v2
- **Architecture**: Stateless microservice

## Project Structure
src/
├── api/
│   └── main.py          # FastAPI endpoints
└── core/
├── config.py        # Pydantic settings
└── benny.py         # AI logic

## Setup

### Prerequisites

- Python 3.12+
- Azure OpenAI API access

### Installation
- bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Add your Azure OpenAI credentials to .env

# Start service
python -m src.api.main

Service runs on http://localhost:8001

## Environmental Variables
# Azure OpenAI (Required)
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_DEPLOYMENT=gpt-35-turbo

# CORS (Optional)
FRONTEND_URL=http://localhost:5173
BACKEND_URL=http://localhost:8000

# Server (Optional)
HOST=127.0.0.1
PORT=8001

## API Endpoints
# Health Check
GET /health
# Chat with Benny
POST /chat
Content-Type: application/json

{
  "message": "How can I improve my sleep?"
}

Response:
{
  "success": true,
  "response": "Try establishing a consistent bedtime routine...",
  "tokens_used": 87
}
# Get Wellness Recommendation
POST /recommend
Content-Type: application/json

{
  "daily_checkin": {
    "nutrition": "Good",
    "sleep": "Poor",
    "fitness": "Yes, completed",
    "stress": "Moderate"
  }
}

Response:
{
  "success": true,
  "response": "Prioritize 7-8 hours of sleep tonight by going to bed 30 minutes earlier.",
  "tokens_used": 45
}

