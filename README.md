# 🤖 Benny - AI-Powered Wellness Coach

A full-stack healthcare application providing personalized wellness coaching through AI-driven conversations, habit tracking, and goal prioritization. Built with React, FastAPI, and Azure OpenAI.

## **Live Demo**
- **Frontend**: [https://benny-wellness.vercel.app](your-url)
- **Backend API**: [https://api.benny-wellness.com](your-api-url)
- **Demo Credentials**: demo@benny.com / demo123

## AI Service

**Location**: `benny-ai-service/`

**Tech Stack**: FastAPI, Azure OpenAI, Pydantic

### Features
- Conversational wellness coaching with context awareness
- Personalized daily recommendations from check-in data
- Stateless microservice (no database)
- Async operations with fallback responses

Service URL: http://localhost:8001
API Documentation: http://localhost:8001/docs
## Integration
Backend calls AI service for recommendations:
# After user submits check-in
recommendation = await ai_service.get_recommendation(checkin_data)

AI service is stateless - backend manages all data persistence.
See benny-ai-service/README.md for detailed API reference.

### Quick Start
- bash
cd benny-ai-service
pip install -r requirements.txt
cp .env.example .env
# Add Azure OpenAI credentials to .env
python -m src.api.main

## Backend

**Location**: `benny-backend/`

**Tech Stack**: FastAPI, PostgreSQL, SQLAlchemy (async), Alembic

### Features
- RESTful API with async operations
- PostgreSQL database with migrations
- Clean architecture (Repository + Service patterns)
- Type-safe validation with Pydantic v2
- Enum-based check-in responses for data consistency
- AI recommendation integration (optional, non-blocking)

### Quick Start
- bash
cd benny-backend
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
python main.py

## **Key Features**
- **AI Wellness Coaching**: Personalized health guidance using Azure OpenAI
- **Daily Check-ins**: Structured health assessments with AI recommendations  
- **Goal Prioritization**: Drag-and-drop interface for wellness objectives
- **Real-time Chat**: Conversational AI with memory and context awareness
- **Progress Tracking**: Visual dashboards and historical data analysis

## 🛠 **Tech Stack**
- **Frontend**: React, TypeScript, Tailwind CSS
- **Backend**: FastAPI, PostgreSQL, SQLAlchemy
- **AI**: Azure OpenAI API with custom prompt engineering
- **Auth**: OAuth 2.0 (Google, Apple, Facebook)
- **Deployment**: Vercel (frontend), Railway (backend)



