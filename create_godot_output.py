import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv

# 1. Load your API key securely from the .env file
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# 2. Initialize the Gemini Client
client = genai.Client(api_key=api_key)

def generate_subtasks(task_description, p_id, p_type):
    # Mapping logic: Stars have planets, Planets have moons
    child_type = "planet" if p_type == "star" else "moon"
    
    # System instructions guide the AI to use your specific model
    system_instr = (
        f"Break the user's task into 3 sub-tasks. "
        f"Return a JSON object with 'subtasks' (array), 'parent_id' ({p_id}), "
        f"and 'subtasks_type' ('{child_type}'). "
        "Each subtask needs: 'name', 'description', 'color', and 'distance' (1-3)."
    )

    # 2. Generate Content with JSON Mode
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=f"Task: {task_description}",
        config=types.GenerateContentConfig(
            system_instruction=system_instr,
            response_mime_type="application/json",
        ),
    )

    # 3. Output the Result
    # This matches your specific model exactly
    final_output = json.loads(response.text)
    
    # Save to file for Godot to ingest
    with open("to_godot.json", "w") as f:
        json.dump(final_output, f, indent=4)
    
    return final_output

# Execution
data = generate_subtasks("Fix the engine", 102, "star")
print(json.dumps(data, indent=2))