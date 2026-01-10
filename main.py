import os
import google.generativeai as genai
from dotenv import load_dotenv
import json

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Create the model with a specific system instruction
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash", # Use flash for speed/lower latency
    system_instruction="You are a productivity assistant. The user provides a task. You break it down into 3 to 5 actionable subtasks. You must return the response as a JSON object with a 'subtasks' key containing a list of strings."
)

def get_subtasks(task_name: str):
    prompt = f"Break down this task: {task_name}"
    # We force the response to be JSON
    response = model.generate_content(
        prompt,
        generation_config={"response_mime_type": "application/json"}
    )
    
    return json.loads(response.text)

# Quick Test
if __name__ == "__main__":
    print(get_subtasks("Build a wooden bookshelf"))