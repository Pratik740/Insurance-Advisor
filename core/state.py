from typing import TypedDict, Annotated, Optional, Literal
from langchain_core.messages import AnyMessage
from pydantic import BaseModel, Field
from google.genai import types

def trim_messages(left: list, right: list):
    """Adds new messages but keeps only the last 5 for context."""
    combined = left + right
    # Keep the first message (often system context) + the last 5 exchanges
    if len(combined) > 6:
        return [combined[0]] + combined[-5:]
    return combined

class UserProfile(BaseModel):
    name: Optional[str] = Field(default=None, description="User's first name")
    age: Optional[int] = Field(default=None, description="User's current age")
    income: Optional[int] = Field(default=None, description="Annual income in INR")
    smoker: Optional[bool] = Field(default=None, description="Whether the user smokes")
    gender: Optional[str] = Field(default="male", description="User's gender")

class InsuranceState(TypedDict):
    # STM: Automatic conversation history
    messages: Annotated[list[AnyMessage], trim_messages]
    
    # LTM/Profile: Persistent data across nodes
    user_profile: UserProfile
    
    # Routing control
    intent: Literal["life", "health", "travel", "home"] = Field(description="Type of insurance (life/health/travel) user is looking for USE LABELS")

    user_preferences: Optional[str]


def master_config():
    return types.GenerateContentConfig(
            temperature=0.0,
            response_mime_type="application/json",
            response_schema={
                "type": "OBJECT",
                "properties": {
                    "intent": {"type": "STRING","nullable": True},
                    "user_preferences": {"type": "STRING", "nullable": True}, 
                    "user_profile": {
                        "type": "OBJECT",
                        "properties": {
                            "name": {"type": "STRING", "nullable": True},
                            "age": {"type": "INTEGER", "nullable": True},
                            "income": {"type": "INTEGER", "nullable": True},
                            "smoker": {"type": "BOOLEAN", "nullable": True},
                            "gender": {"type": "STRING", "nullable": True},
                        }
                    }
                }
            },
            system_instruction=(
                "Classify intent as life, health, travel, home.\n"
                "Extract and update only explicitly stated profile fields.\n"
                "Extract user_preferences that can be used for querying free benefits or as an addons — Summarize what the user values (e.g.'concerns about children', 'health benefits', 'immediate payout' etc. )"
                "Use null for missing values."
            )
    )

    




# state schema alignment

# trim_messages boundary
