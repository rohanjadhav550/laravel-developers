from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Question(BaseModel):
    question: str

@app.get("/")
def read_root():
    return {"message": "Hello from Idea Agent!"}

@app.post("/ask")
def ask_question(q: Question):
    # Placeholder for AI processing logic
    return {"response": f"You asked: {q.question}. This is a mock response from the AI agent."}
