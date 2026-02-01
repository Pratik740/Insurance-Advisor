from core.state import UserProfile, InsuranceState, master_config
from google import genai
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage

load_dotenv()
client = genai.Client()

def normalize_intent(raw: str | None) -> str | None:
    if not raw:
        return None

    raw = raw.lower()
    if "life" in raw:
        return "life"
    if "health" in raw or "medical" in raw:
        return "health"
    if "travel" in raw:
        return "travel"
    if "home" in raw or "house" in raw:
        return "home"
    return None

def master_node(state: InsuranceState):
    print("Master_Advisor_Node")

    chat_history = ""
    for msg in state["messages"]:
        role = "User" if isinstance(msg, HumanMessage) else "Assistant"
        chat_history += f"{role}: {msg.content[:500]}\n"
    
    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=chat_history,
        config=master_config()
    )

    parsed = response.parsed or {}

    prev_profile: UserProfile = state.get("user_profile") or {}

    if hasattr(prev_profile, "model_dump"):
        merged_dict = prev_profile.model_dump()
    elif hasattr(prev_profile, "dict"):
        merged_dict = prev_profile.dict()
    else:
        merged_dict = dict(prev_profile)

    # 2. Extract new data from LLM
    new_data = parsed.get("user_profile") or {}    

    # 3. MERGE (new values override old ones only if present)
    for key, val in new_data.items():
        if val is not None:
            merged_dict[key] = val

    raw_intent = parsed.get("intent")

    return {
        "intent": normalize_intent(raw_intent),
        "user_profile": merged_dict 
    }
# intent normalization and state passthrough

# profile merge logic
