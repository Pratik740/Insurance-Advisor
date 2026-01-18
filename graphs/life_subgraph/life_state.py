from typing import Optional, Literal
from core.state import InsuranceState
from google.genai import types

class TermLifeState(InsuranceState):
    # Domain specific data
    life_cover: Optional[int]
    cover_till_age: Optional[int]
    
    raw_premiums: list = []
    semantic_data: list = []
    selected_plan_id: Optional[str]

    recommendation_reasoning: Optional[str] = None
    
    policy_facts: Optional[str] = None

    requested_premiums: list = []

    plan_options: list = []
    action_type: Literal["quick_quote", "full_reco"]
    is_complete: bool = False

def life_intake_config():
    return types.GenerateContentConfig(
        temperature=0.1,
        response_mime_type="application/json",
        response_schema={
            "type": "OBJECT",
            "properties": {
                "user_profile": {
                    "type": "OBJECT",
                    "properties": {
                        "name": {"type": "STRING", "nullable": True},
                        "age": {"type": "INTEGER", "nullable": True},
                        "income": {"type": "INTEGER", "nullable": True},
                        "gender": {"type": "STRING", "nullable": True},
                        "smoker": {"type": "BOOLEAN", "nullable": True}
                    }
                },
                "life_cover": {"type": "INTEGER", "nullable": True},
                "cover_till_age": {"type": "INTEGER", "nullable": True},
                "is_complete": {"type": "BOOLEAN"},
                "confirmation_message": {"type": "STRING"},
                "preferences_summary": {"type": "STRING"} 
            },
            "required": ["is_complete", "confirmation_message", "preferences_summary"]
        },
        system_instruction=(
            "You are a Term Life Insurance specialist. "
            "1. Extract age, income, gender, and smoker status. If the user provides a birth year (eg. 2001) then calculate the age based on current year."
            "2. Default life_cover to 10,000,000 and cover_till_age to 70 if not mentioned. "
            "3. If any core field (age, income, gender, smoker) is missing, is_complete = false. "
            "4. Craft a message confirming the defaults (1Cr @ 70 years) or the user's specific choices."
            "5. In 'preferences_summary', create a weighted search string for insurance riders or free benefits. "
            "Example: 'User values family security, children education, and accidental death protection'."
            "IMPORTANT: Your response must be a single, valid JSON object. Do not include any introductory text or markdown formatting outside the JSON."
        )
    )