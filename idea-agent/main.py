from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.graph import app_graph
from langchain_core.messages import HumanMessage
import uuid

app = FastAPI()

class Question(BaseModel):
    question: str
    thread_id: str = None

@app.get("/")
def read_root():
    return {"message": "Hello from Multi-Agent System!"}

@app.post("/ask")
def ask_question(q: Question):
    """
    Process a question through the multi-agent system.
    Conversation state is preserved using the thread_id.
    """
    # Generate or use existing thread_id for conversation continuity
    thread_id = q.thread_id or str(uuid.uuid4())

    config = {"configurable": {"thread_id": thread_id}}

    # Create input message
    inputs = {"messages": [HumanMessage(content=q.question)]}

    try:
        # Invoke the graph with checkpointer support
        # The graph will maintain conversation state across requests using the thread_id
        result = app_graph.invoke(inputs, config=config)

        # Get the last message from the conversation
        last_message = result['messages'][-1]

        # Determine if the conversation has ended or is waiting for more input
        # The graph returns END when it needs user input
        status = "completed"

        return {
            "response": last_message.content,
            "thread_id": thread_id,
            "status": status
        }
    except ValueError as e:
        # Handle configuration errors (missing API keys, etc.)
        error_message = str(e)
        print(f"Configuration error: {error_message}")
        raise HTTPException(
            status_code=400,
            detail=error_message
        )
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error processing question: {error_details}")
        raise HTTPException(status_code=500, detail=str(e))
