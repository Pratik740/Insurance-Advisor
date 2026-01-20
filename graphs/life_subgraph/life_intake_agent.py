from graphs.life_subgraph.life_state import TermLifeState, life_intake_config
from langchain_core.messages import HumanMessage, AnyMessage, AIMessage
from langgraph.types import interrupt
from graphs.master_advisor import client
import json


def life_intake_agent(state: TermLifeState):
    print("\n--- LIFE INTAKE AGENT ---")
    
    current_values = {
        "life_cover": state.get("life_cover"),
        "cover_till_age": state.get("cover_till_age"),
        "profile": state.get("user_profile")
    }
    
    # print("Last input: ", state["messages"][-1].content)
    chat_history = ""
    for msg in state["messages"]:
        role = "User" if isinstance(msg, HumanMessage) else "Assistant"
        chat_history += f"{role}: {msg.content}\n"

    system_instruction = f"""
    You are a State Management Expert for an Insurance Graph.
    
    CURRENT STATE IN DATABASE:
    {json.dumps(current_values, indent=2)}

    USER CONVERSATION:
    {chat_history}

    TASK:
    1. Look at the User's LATEST message. 
    2. If the user requests a change (e.g., "Increase cover to 5Cr"), update the state.
    3. If the user's latest message doesn't mention a value, RETAIN the values from 'CURRENT STATE IN DATABASE'.
    4. NEVER revert to defaults (like 1Cr) if a value already exists in the Database.
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=chat_history,
        config=life_intake_config()
    )
    # print(f"DEBUG: Input Tokens = {response.usage_metadata.prompt_token_count}")
        
    p = response.parsed

    print("Parsed Response: ", p, flush=True)

    # 1. Update Profile (Clean merge)
    # Since p["user_profile"] matches the shape of state["user_profile"]
    new_profile_data = p.get("user_profile", {})
    current_profile = state.get("user_profile")

    updated_profile_dict = current_profile.dict() if hasattr(current_profile, 'dict') else dict(current_profile)

    for key, val in new_profile_data.items():
        if val is not None:
            updated_profile_dict[key] = val

    # 2. Check if we have everything and user has confirmed defaults
    # print(updated_profile_dict, flush=True)
    if p["is_complete"]:
        return {
        "user_profile": updated_profile_dict,
        "user_preferences": p.get("preferences_summary"),
        "is_complete": True,
        "life_cover": p.get("life_cover") or 10000000,
        "cover_till_age": p.get("cover_till_age") or 70
    }

    #TRIGGER HITL
    ans = interrupt({
        "message": p["confirmation_message"],
        "current_data": p
    })
        
    return {
        "user_profile": updated_profile_dict,
        "messages": [HumanMessage(content=ans)],
        "is_complete": False
    }
    

def check_intake_status(state: TermLifeState):

    if state.get("is_complete"):
        print("--- INTAKE COMPLETE ---")
        goal = state.get("action_type")
        
        if goal == "quick_quote":
            print("\nRouting to Quick Premium Tool...")
            return "quick_premium_node"
        
        print("\nLaunching Parallel Recommendation Engines (Fan-out)...")
        return ["premium_engine", "semantic_engine"]
    
    return "intake_agent"