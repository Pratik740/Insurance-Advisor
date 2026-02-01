from graphs.life_subgraph.main import life_subgraph
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.postgres import PostgresSaver
from langchain_core.messages import HumanMessage, AnyMessage, AIMessage
from graphs.master_advisor import master_node
from core.state import InsuranceState
from core.persistence import get_checkpointer
from langgraph.types import interrupt, Command

def intent_router(state: InsuranceState):
    print("Intent Router")
    intent = state.get("intent")

    print(state["user_profile"], state["intent"])
    if intent == "life":
        return "life"
    if intent == "health":
        return "health"
    if intent == "travel":
        return "travel"

    return "ambiguous"

def health_stub(state: InsuranceState):
    print("Health Insurance")
    return state

def travel_stub(state: InsuranceState):
    print("Travel Insurance")
    return state

def hitl_clarify_intent(state: InsuranceState):
    ans =  interrupt({
        "type": "ambiguous",
        "reason": "User is fucking stupid and doesn't know how to write a clear input",
        "questions": ["Are you looking for life, health or travel insurance?"],
        "instruction": "Please specify the label? life / health / travel."
    })
    return {
        "messages": [HumanMessage(content=ans)]
    }


# Build Graph
builder = StateGraph(InsuranceState)

builder.add_node("master_node",master_node)
builder.add_node("life", life_subgraph)
builder.add_node("health", health_stub)
builder.add_node("travel", travel_stub)
builder.add_node("hitl_intent", hitl_clarify_intent)

builder.add_edge(START,"master_node")
builder.add_conditional_edges(
    "master_node",
    intent_router,{
        "life": "life",
        "health": "health",
        "travel": "travel",
        "ambiguous": "hitl_intent",
    }
)
builder.add_edge("life", END)
builder.add_edge("health", END)
builder.add_edge("travel", END)
builder.add_edge("hitl_intent", "master_node")

config = {
    "configurable": {
        "thread_id": "pratik-session-4" # Created: ["pratik-session-1", "pratik-session-2", "pratik-session-3"]
    }    
}

with get_checkpointer() as checkpointer:
    checkpointer.setup()
    graph = builder.compile(checkpointer=checkpointer)

    current_input = {
        "messages": [
            HumanMessage(content="yes, i would like to calculate the monthly premium for this cover amount in royal sundaram and wanna see how it is as a company, is it reliable?")
        ]
    }

    while True:
            interrupted = False
            # subgraphs=True is mandatory to catch the 'interrupt' inside the life node
            for namespace, message in graph.stream(current_input, config=config, subgraphs=True):
                
                if "__interrupt__" in message:
                    interrupt_data = message["__interrupt__"][0].value
                    
                    # Handles both intent_hitl (instruction) and intake_hitl (message)
                    display_msg = interrupt_data.get("message") or interrupt_data.get("instruction")
                    print(f"\n[AI Advisor]: {display_msg}")
                    
                    answer = input("> ").strip()

                    # We RESUME with the raw string answer. 
                    # This string is what 'ans = interrupt(...)' returns in the node code.
                    current_input = Command(resume=answer)
                    interrupted = True
                    break
                
                # Print the flow for debugging
                # print(f"Node: {namespace} | State Updated")

            if not interrupted:
                # If the graph reaches END, we wait for a brand new user message
                print("\n--- Session Complete ---")
                break
                












# intent router edge cases

# hitl intent passthrough
