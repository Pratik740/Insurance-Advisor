from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from langchain_core.messages import HumanMessage
from langgraph.types import Command
from core.persistence import get_checkpointer
from graphs.master import get_graph
from langgraph.errors import GraphRecursionError
import uvicorn
import uuid
import json

# --- Pydantic Models ---
class ChatRequest(BaseModel):
    message: str
    thread_id: Optional[str] = None

# (ChatResponse model removed as we are now streaming raw SSE events)

# --- App Setup (FastAPI Object)---
app = FastAPI(title="Insurance Advisor API")

# Setup CORS for the upcoming React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health_check():
    return {"status": "ok", "service": "Agentic Insurance Advisor"}

@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    # Determine the thread_id
    current_thread_id = req.thread_id
    if not current_thread_id:
        current_thread_id = str(uuid.uuid4())
    
    config = {
        "configurable": {"thread_id": current_thread_id},
        "recursion_limit": 15
    }

    async def event_generator():
        try:
            with get_checkpointer() as checkpointer:
                checkpointer.setup()
                graph = get_graph(checkpointer)

                # Check if this thread is currently paused/interrupted
                stateSnapshot = graph.get_state(config)
                
                # If there are next nodes to execute, it implies the graph is suspended
                if stateSnapshot.next:
                    inputs = Command(resume=req.message)
                else:
                    inputs = {"messages": [HumanMessage(content=req.message)]}

                final_response_text = ""
                is_interrupted = False

                # Run the graph dynamically collecting outputs
                for namespace, chunk in graph.stream(inputs, config=config, subgraphs=True):
                    # Check for Human-in-the-Loop interruptions
                    if "__interrupt__" in chunk:
                        is_interrupted = True
                        interrupt_data = chunk["__interrupt__"][0].value
                        
                        display_msg = interrupt_data.get("message") or interrupt_data.get("instruction") or "Clarification required."
                        
                        # Yield the interrupt as the final message
                        payload = json.dumps({"response": display_msg, "thread_id": current_thread_id})
                        yield f"event: message\ndata: {payload}\n\n"
                        break
                    
                    # Process standard nodes to stream statuses
                    for node_name, node_output in chunk.items():
                        # Stream the node name to the frontend loaders
                        status_payload = json.dumps({"node": node_name})
                        yield f"event: status\ndata: {status_payload}\n\n"

                        # Handle both dictionary output structure and direct object structures to find AIMessages
                        messages = None
                        if isinstance(node_output, dict) and "messages" in node_output:
                            messages = node_output["messages"]
                        elif hasattr(node_output, "messages"):
                            messages = getattr(node_output, "messages")
                            
                        if messages:
                            last_msg = messages[-1] if isinstance(messages, list) else messages
                            
                            if hasattr(last_msg, "content") and type(last_msg).__name__ == "AIMessage":
                                if str(last_msg.content).strip():
                                    final_response_text = str(last_msg.content)

                # If the graph finished without interruption, yield the final accumulated AI text
                if not is_interrupted and final_response_text:
                    payload = json.dumps({"response": final_response_text, "thread_id": current_thread_id})
                    yield f"event: message\ndata: {payload}\n\n"

        except GraphRecursionError:
            error_payload = json.dumps({"error": "The orchestrator looped too many times."})
            yield f"event: error\ndata: {error_payload}\n\n"
        except Exception as e:
            error_payload = json.dumps({"error": str(e)})
            yield f"event: error\ndata: {error_payload}\n\n"

    # Return the generator wrapped in a StreamingResponse 
    return StreamingResponse(event_generator(), media_type="text/event-stream")

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
