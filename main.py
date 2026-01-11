import os
import json
from google import genai
from google.genai import types  # For schema configuration
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from create_godot_output import validate_and_correct_tasks

# --- CONFIGURATION ---
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env file")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env file")

client = genai.Client(api_key=api_key)

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

def get_valid_ai_json(prompt, max_retries=3):
    """
    Calls Gemini using the new SDK and verifies JSON format.
    Retries up to max_retries if logic or format fails.
    """
    for attempt in range(max_retries):
        try:
            print(f"AI Attempt {attempt + 1}...")
            
            # New SDK call format
            response = client.models.generate_content(
                model="gemini-2.5-flash-lite", 
                contents=types.Part.from_text(text=prompt),
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            
            
            
            # Parse the text response
            data = json.loads(response.text)
            
            # Validation: Ensure it contains the list we need
            if "subtasks" in data and isinstance(data["subtasks"], list):
                print("Successfully received valid JSON.")
                return data
            else:
                print("Missing 'subtasks' list. Retrying...")
                
        except Exception as e:
            print(f"Attempt {attempt + 1} failed with error: {e}")
            
    return None

# --- MAIN ENDPOINT ---
@app.post("/generate")
async def generate_solar_system(request: GodotTaskRequest):
    child_type = get_child_type(request.parent_type)
    
    # The prompt forces Gemini to behave as a structured data generator
    scale_hint = {
        "blackhole": "major project phases",
        "star": "specific actionable tasks",
        "planet": "micro-steps and checklists"
    }.get(request.parent_type, "tasks")

    prompt = f"""
    ROLE: You are an expert Project Management Architect specializing in granular task decomposition.
    
    CONTEXT: The user is utilizing a 2D solar system productivity tool. 
    You are breaking down a parent node of type '{request.parent_type}' into its constituent '{scale_hint}'.
    
    TASK TO BREAK DOWN: "{request.task_description}"
    
    OBJECTIVE: Generate 3 to 7 logical, sequential, and highly specific sub-elements.
    
    CONSTRAINTS for JSON fields:
    1. 'name': Clear, concise, and action-oriented (e.g., "Procure materials" instead of "Materials").
    2. 'description': Provide a 3-4 sentence paragraph. It must include:
       - The specific goal of this subtask.
       - A list of necessary resources, tools, or software.
       - A 'pro-tip' for efficiency.
    3. 'duration': A realistic estimate in days. 
       - Use 0.1 for tasks taking ~45 mins.
       - Use 0.5 for half-days.
       - Ensure the total duration of all subtasks is logically consistent with the parent task.

    OUTPUT FORMAT:
    Return ONLY a valid JSON object. Do not include markdown formatting, backticks, or preamble.
    {{
      "subtasks": [
        {{
          "name": "String",
          "description": "String",
          "duration": Float
        }}
      ]
    }}
    """

    # Convert string response to Python dictionary
    ai_data = get_valid_ai_json(prompt, max_retries=5)

    if ai_data is None:
    # If we failed all 5 times, return a 500 error to Godot
        raise HTTPException(
            status_code=500, 
            detail="AI failed to generate a valid task structure after 5 attempts."
        )
    
    try:
        final_output = validate_and_correct_tasks(
            ai_data, 
            request.parent_id, 
            child_type
        )
        return final_output

    except Exception as e:
        print(f"Error in logic_processor: {e}")
        raise HTTPException(status_code=500, detail="Error in logic processing script.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)