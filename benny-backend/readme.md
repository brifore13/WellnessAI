# Benny Wellness AI - Backend

A modern FastAPI backend for the Benny wellness coaching application with PostgreSQL database, clean architecture, and AI-powered recommendations.

## Tech Stack

- **Framework**: FastAPI (async)
- **Database**: PostgreSQL with SQLAlchemy (async)
- **Migrations**: Alembic
- **Validation**: Pydantic v2
- **AI Integration**: Azure OpenAI (microservice)

## Architecture
app/
├── api/routes/      # HTTP endpoints
├── core/            # Config, database, logging
├── models/          # SQLAlchemy models
├── repositories/    # Data access layer
├── schemas/         # Pydantic request/response models
└── services/        # Business logic

**Design Patterns**: Repository pattern, dependency injection, layered architecture

## Setup

### Prerequisites

- Python 3.12+
- PostgreSQL 16+
- AI Service running on port 8001

### Installation
- bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your database credentials

# Create database
psql postgres -c "CREATE DATABASE wellness_dev;"

# Run migrations
alembic upgrade head

# Start server
python main.py

Server runs on http://localhost:8000

## Environment Variables
# Database
DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/wellness_dev

# CORS
FRONTEND_URL=http://localhost:5173

# External Services
AI_SERVICE_URL=http://127.0.0.1:8001

# Application
DEBUG=true
SECRET_KEY=your-secret-key-here

## API Endpoints
GET /health
POST /api/checkin/submit
Content-Type: application/json

{
  "responses": [
    {"category": "nutrition", "response": "Good"},
    {"category": "sleep", "response": "Okay"},
    {"category": "fitness", "response": "Yes, completed"},
    {"category": "stress", "response": "Moderate"}
  ]
}
GET /api/checkin/history?limit=30
GET /api/checkin/streak

# DB Migrations
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

## Development
# Run with auto-reload
python main.py

# View API documentation
http://localhost:8000/docs