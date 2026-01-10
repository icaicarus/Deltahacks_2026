from fastapi import FastAPI
from pydantic import BaseModel
from ai_engine import get_subtasks

app = FastAPI()

class TaskRequest(BaseModel):
    task_name: str

@app.post("/generate")
async def generate_api(request: TaskRequest):
    # This calls the Gemini function we made
    try:
        data = get_subtasks(request.task_name)
        return data
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)