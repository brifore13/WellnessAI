# 🤖 Benny - AI-Powered Wellness Coach

A full-stack healthcare application providing personalized wellness coaching through AI-driven conversations, habit tracking, and goal prioritization. Built with React, FastAPI, and Azure OpenAI.

## **Live Demo**
- **Frontend**: [https://benny-wellness.vercel.app](your-url)
- **Backend API**: [https://api.benny-wellness.com](your-api-url)
- **Demo Credentials**: demo@benny.com / demo123

*[Add 2-3 screenshots or a GIF showing the main features]*

## 🎯 **Key Features**
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

## 🏥 **Healthcare Focus**
- Evidence-based wellness recommendations
- Secure health data storage with encryption
- HIPAA-compliant architecture design
- Integration with health tracking APIs

## 🚀 **Quick Start**
```bash
# Clone and setup
git clone https://github.com/yourusername/benny-ai-wellness
cd benny-ai-wellness

# Backend
cd backend && pip install -r requirements.txt
uvicorn main:app --reload

# Frontend  
cd frontend && npm install && npm run dev
