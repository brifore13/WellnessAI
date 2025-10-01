# 🤖 Benny - AI-Powered Wellness Coach

A full-stack healthcare application providing personalized wellness coaching through AI-driven conversations, habit tracking, and goal prioritization. Built with React, FastAPI, and Azure OpenAI.

## **Live Demo**
- **Frontend**: [https://benny-wellness.vercel.app](your-url)
- **Backend API**: [https://api.benny-wellness.com](your-api-url)
- **Demo Credentials**: demo@benny.com / demo123


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
```bash
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



