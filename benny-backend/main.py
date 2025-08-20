from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware 
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import datetime
import sys
import os
from pathlib import Path

from config import SECRET_KEY
from routers import auth, users
import httpx

# add bennyDB directory to Python path
bennydb_path = Path(__file__).parent.parent/"bennyDB"
sys.path.append(str(bennydb_path))

# Import database
import db_connector_real
db = db_connector_real.wellness_ai_db()
print("Database connected successfully!")


app = FastAPI()

# Get CORS origins from environment variable
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
allowed_origins = [
    frontend_url,
    "http://localhost:5173",  # Vite dev
    "http://localhost:3000",  # Create React App dev
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000"
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
app.include_router(auth.router)
app.include_router(users.router)

# Add OUATH middleware
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

# Pydantic models for request/response
class CheckInResponse(BaseModel):
    category: str
    question: str
    response: str

class CheckInSubmission(BaseModel):
    responses: List[CheckInResponse]

@app.get("/")
async def root():
    """API info endpoint"""
    return {
        "service": "Benny Daily Check-in Backend",
        "database_connected": True,
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "database_connected": True,
    }

@app.post("/api/checkin/submit")
async def submit_checkin(submission: CheckInSubmission):
    """Submit daily check-in responses"""
    
    database_saved = False

    try:
        # Get today's date
        today = datetime.datetime.now().strftime("%m/%d/%Y")
        
        # Process the responses into the format the database expects
        checkin_data = {}
        
        for response in submission.responses:
            checkin_data[response.category] = response.response
        
        print(f"Processing check-in for {today}: {checkin_data}")
        
        # Save to database
        db.run_query("""
            INSERT INTO daily_log_table 
            (log_date, nutrition, sleep_quality, stress_level, activity_complete, activity_name, user_program_row_id, activity_addresses_goal)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, today, checkin_data.get("nutrition"), checkin_data.get("sleep"), 
            checkin_data.get("stress"), 1, "Daily Check-in", 1, 1)
        print(f"Saved to database")
        database_saved = True

        # Call AI for recommendation
        benny_recommendation = None
        try:
            import httpx
            
            ai_service_url = os.getenv("AI_SERVICE_URL", "http://127.0.0.1:8001")
            
            async with httpx.AsyncClient() as client:
                ai_response = await client.post(
                    f"{ai_service_url}/recommend",
                    json={"daily_checkin": checkin_data},
                    timeout=30.0
                )

                if ai_response.status_code == 200:
                    ai_data = ai_response.json()
                    if ai_data.get("success"):
                        benny_recommendation = ai_data.get("response")

        except Exception:
            pass    # continue without rec iv AI service fails

        return {
            "success": True,
            "message": "Check-in saved!",
            "data": checkin_data,
            "recommendation": benny_recommendation
        }
        
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/api/chat/recent")
async def get_recent_chat_messages():
#
# async def get_recent_chat_messages(current_user: dict = Depends(users.get_current_user)):
#
    """
    Get the last 10 recent chat messages
    """

    
    # Add this in to query individual user history
    # user_id = current_user['user']['sub']
    # print(f"Fetching chat history for user: {user_id}")
    
    try:
        # get database chat history
        # -- WHERE ch.user_id = ?  <-- Something like this needs to be added to separate user history
        query = """
        SELECT
            che.sequence_number,
            che.user_or_benny,
            che.entry_text,
            ch.date
        FROM chat_history_entries che
        JOIN chat_history ch ON che.fk_row_id =  ch.row_id
        ORDER BY ch.date DESC, che.sequence_number DESC
        LIMIT 10
        """

        # result = db.run_query(query, user_id) 
        # The query would need the user_id
        result = db.run_query(query)
        messages = result.fetchall()

        # format response
        formatted_messages = []
        for message in messages:
            formatted_messages.append({
                "sequence_number": message[0],
                "user_or_benny": message[1],
                "entry_text": message[2],
                "date": message[3]
            })

        formatted_messages.reverse()
        return {
            "success": True,
            "messages": formatted_messages
        }
    
    except Exception as e:
        print(f"Error fetching recent messages: {e}")
        raise HTTPException(status_code=500, detail=str(e))
           

if __name__ == "__main__":
    print("Starting Benny Daily Check-in Backend (Testing Mode)...")
    print("Database connection: DISABLED")
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)