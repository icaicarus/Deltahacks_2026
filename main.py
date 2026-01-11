import os
import json
import google.generativeai as genai
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

# --- CONFIGURATION ---
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env file")

genai.configure(api_key=api_key)
# We use flash for high speed and lower cost
model = genai.GenerativeModel("gemini-1.5-flash")

app = FastAPI()

# --- DATA MODELS ---
class GodotTaskRequest(BaseModel):
    task_description: str
    parent_type: str  # "blackhole", "star", or "planet"
    parent_id: int

# --- HELPER FUNCTIONS ---
def get_child_type(parent_type: str) -> str:
    mapping = {
        "blackhole": "star",
        "star": "planet",
        "planet": "moon"
    }
    return mapping.get(parent_type.lower(), "planet")

# --- MAIN ENDPOINT ---
@app.post("/generate")
async def generate_solar_system(request: GodotTaskRequest):
    child_type = get_child_type(request.parent_type)
    
    # The prompt forces Gemini to behave as a structured data generator
    prompt = f"""
    You are a solar-system productivity architect. 
    The user wants to break down a task into sub-elements.
    
    Parent Task: "{request.task_description}"
    
    Return a JSON object with a 'subtasks' list. 
    Each subtask must have:
    - 'name': The full task title.
    - 'description': A detailed paragraph describing the tasks and any resources needed to complete it.
    - 'duration': How many days will it take to complete the task. This should be a floating point number.
    
    Format (JSON):
    {{
      "subtasks": [
        {{ "name": "...", "description": "...", "duration": "..." }},
        ...
      ]
    }}

    Nothing else should be sent except this JSON output.
    """

    try:
        # Request JSON specifically from Gemini
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        
        # Convert string response to Python dictionary
        ai_data = json.loads(response.text)
        
        final_output = validate_and_correct_tasks(
            ai_data, 
            request.parent_id, 
            child_type
        )

        # 3. Send the CORRECTED data back to Godot
        return final_output

    except Exception as e:
        print(f"Error calling Gemini: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)