from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.graph import app_graph
from app.database import save_conversation_metadata, create_solution
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
import uuid

app = FastAPI()

class Question(BaseModel):
    question: str
    thread_id: str = None
    user_id: int = 2  # Default user_id, should be passed from frontend
    project_id: int = None
    ai_provider: str = None  # OpenAI or Anthropic
    ai_api_key: str = None  # API key passed from Laravel

@app.get("/")
def read_root():
    return {"message": "Hello from Multi-Agent System!"}

@app.post("/ask")
def ask_question(q: Question):
    """
    Process a question through the multi-agent system.
    Conversation state is preserved using the thread_id.
    Messages are stored in Redis, metadata in MySQL.
    """
    # Generate or use existing thread_id for conversation continuity
    thread_id = q.thread_id or str(uuid.uuid4())
    is_new_conversation = q.thread_id is None

    config = {
        "configurable": {
            "thread_id": thread_id,
            "user_id": q.user_id,
            "ai_provider": q.ai_provider,
            "ai_api_key": q.ai_api_key,
        }
    }

    # Self-healing: Check for dangling tool calls in the state
    # This fixes "BadRequestError: An assistant message with 'tool_calls' must be followed by tool messages"
    try:
        current_state = app_graph.get_state(config)
        if current_state.values and current_state.values.get('messages'):
            messages = current_state.values['messages']
            # Look for AIMessage with tool_calls that don't have corresponding ToolMessages
            for i in range(len(messages) - 1, -1, -1):
                msg = messages[i]
                if isinstance(msg, AIMessage) and hasattr(msg, 'tool_calls') and msg.tool_calls:
                    # Check if the next messages contain responses for all tool calls
                    tool_call_ids = {tc['id'] for tc in msg.tool_calls}

                    # Look ahead to find ToolMessages that respond to these calls
                    responded_ids = set()
                    for j in range(i + 1, len(messages)):
                        if isinstance(messages[j], ToolMessage):
                            responded_ids.add(messages[j].tool_call_id)
                        elif isinstance(messages[j], (AIMessage, HumanMessage)):
                            # Stop looking if we hit another AI or Human message
                            break

                    # Find missing responses
                    missing_ids = tool_call_ids - responded_ids

                    if missing_ids:
                        print(f"Found {len(missing_ids)} dangling tool calls in thread {thread_id}. Injecting ToolMessages to fix state.")
                        # Inject ToolMessages for all missing tool calls
                        tool_messages = []
                        for tool_call in msg.tool_calls:
                            if tool_call['id'] in missing_ids:
                                tool_msg = ToolMessage(
                                    tool_call_id=tool_call['id'],
                                    content="Tool execution failed or timed out previously. Resuming conversation.",
                                    name=tool_call.get('name', 'unknown_tool')
                                )
                                tool_messages.append(tool_msg)

                        if tool_messages:
                            app_graph.update_state(config, {"messages": tool_messages})

                    # Only check the most recent AIMessage with tool_calls
                    break
    except Exception as e:
        print(f"Error checking/fixing state: {e}")

    # Create input message
    inputs = {"messages": [HumanMessage(content=q.question)]}

    try:
        # Invoke the graph with checkpointer support
        # The graph will maintain conversation state across requests using the thread_id
        # Messages are automatically saved to Redis by RedisSaver
        result = app_graph.invoke(inputs, config=config)

        # Get the last message from the conversation
        last_message = result['messages'][-1]

        # Count total messages in this conversation
        message_count = len(result['messages'])

        # Generate title from first user message for new conversations
        title = None
        if is_new_conversation:
            # Use first 50 characters of the question as title
            title = q.question[:50] + ("..." if len(q.question) > 50 else "")

        # Save conversation metadata to MySQL
        conversation_data = save_conversation_metadata(
            user_id=q.user_id,
            thread_id=thread_id,
            title=title,
            message_count=message_count,
            project_id=q.project_id
        )

        # Create solution for new conversations
        if is_new_conversation and conversation_data:
            create_solution(
                conversation_id=conversation_data.get('id'),
                user_id=q.user_id,
                title=title or "New Solution",
                description=f"Solution for: {q.question[:100]}",
                project_id=q.project_id
            )

        # Extract requirements/solution from tool calls to return to Laravel
        # This avoids deadlock by letting Laravel handle the persistence
        requirements_data = None
        solution_data = None
        
        for msg in result['messages']:
            # Check if this is an AIMessage with tool calls
            if hasattr(msg, 'tool_calls') and msg.tool_calls:
                for tool_call in msg.tool_calls:
                    tool_name = tool_call.get('name')
                    tool_args = tool_call.get('args', {})
                    
                    # Capture requirements if save_requirements was called
                    if tool_name == 'save_requirements' and 'requirements' in tool_args:
                        requirements_data = tool_args['requirements']
                    
                    # Capture solution if save_solution was called
                    elif tool_name == 'save_solution' and 'solution' in tool_args:
                        solution_data = tool_args['solution']

        # Determine if the conversation has ended or is waiting for more input
        # The graph returns END when it needs user input
        status = "completed"

        return {
            "response": last_message.content,
            "thread_id": thread_id,
            "status": status,
            "message_count": message_count,
            "requirements": requirements_data,
            "solution": solution_data
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

@app.get("/conversation/{thread_id}")
def get_conversation(thread_id: str):
    """
    Retrieve conversation history for a given thread_id from Redis checkpoint.
    """
    try:
        from app.graph import app_graph
        
        # Get the state for this thread
        config = {"configurable": {"thread_id": thread_id}}
        
        # Get the current state from checkpointer
        state = app_graph.get_state(config)
        
        if not state or not state.values.get('messages'):
            return {
                "thread_id": thread_id,
                "messages": [],
                "message_count": 0
            }
        
        # Convert messages to serializable format
        # Filter out tool messages and internal orchestration
        messages = []
        for msg in state.values['messages']:
            msg_class = msg.__class__.__name__

            # Skip tool result messages (they have a 'name' attribute set)
            if hasattr(msg, 'name') and msg.name:
                continue

            # Skip AI messages that are calling tools (internal orchestration)
            if msg_class == "AIMessage" and hasattr(msg, 'tool_calls') and msg.tool_calls:
                continue

            # Only include conversational HumanMessage and AIMessage
            if msg_class in ["HumanMessage", "AIMessage"]:
                messages.append({
                    "role": "user" if msg_class == "HumanMessage" else "assistant",
                    "content": msg.content,
                    "timestamp": getattr(msg, 'timestamp', None)
                })
        
        return {
            "thread_id": thread_id,
            "messages": messages,
            "message_count": len(messages)
        }
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error retrieving conversation: {error_details}")
        raise HTTPException(status_code=500, detail=str(e))
