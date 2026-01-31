import json
from graphs.life_subgraph.life_state import TermLifeState
from graphs.master_advisor import client
from generate.life_endpoint import COMPANIES
from graphs.life_subgraph.calc_premium import calculate_premium, max_cover_by_income
from graphs.life_subgraph.get_plans import get_specific_plan_from_db
from langchain_core.messages import HumanMessage, AIMessage

def quick_premium_node(state: TermLifeState):
    print("\n--- PREMIUM CALCULATOR ---\n")
    
    context_messages = state["messages"][-10:]
    last_msg = context_messages[-1].content

    history_str = "\n".join([f"{type(m).__name__}: {m.content}" for m in context_messages])

    profile = state.get("user_profile")
    user_age = profile.get('age')
    annual_income = profile.get('income')    
    requested_cover = state.get("life_cover")
    requested_till_age = state.get("cover_till_age")

    max_allowed = max_cover_by_income(user_age, annual_income)
    actual_calc_cover = min(requested_cover, max_allowed)
    
    # 1. Extraction: Use Gemini to find the company/plan being asked about
    extraction_prompt = f"""
    User Message: "{last_msg}"
    History: {history_str}
    Available Brands: {COMPANIES}
    Identify all the insurance companies mentioned names for a premium check. 
    Normalize them to match the Master Brand List.

    Return JSON ONLY:
    {{
        "brands": ["Brand 1", "Brand 2"]
    }}
    If none found, return an empty list.
    """

    extraction_res = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=extraction_prompt,
        config={"response_mime_type": "application/json"}
    )

    try:
        target_brands = json.loads(extraction_res.text).get("brands", [])
    except:
        target_brands = []

    if not target_brands:
        return {"policy_facts": "I couldn't identify which companies you're asking about. Could you please specify a brand like HDFC or Tata AIA?"}

   # 2. Loop through brands and calculate
    new_quotes = []
    response_parts = []

    print(f"DEBUG: Unified Calculation for brands: {target_brands}")

    
    for brand in target_brands:
        # DB Search with fuzzy matching logic handled inside get_specific_plan_from_db
        plan = get_specific_plan_from_db(target_company=brand, user_age=user_age, requested_cover=requested_cover, requested_age=requested_till_age) 
        
        if plan:
            monthly_premium = calculate_premium(
                base_rate=float(plan['base_rate']),
                age=user_age,
                life_cover=actual_calc_cover,
                cover_till_age=requested_till_age,
                smoker=profile.get('smoker'),
                gender=profile.get('gender'),
                occupation="salaried"
            )
            
            # Store structured data for state
            new_quotes.append({
                "company": plan['company_name'],
                "monthly_premium": monthly_premium,
                "sum_assured": actual_calc_cover,
                "cover_till_age": requested_till_age
            })
            
            # Build string for immediate display
            response_parts.append(
                f"**{plan['company_name']}**\n"
                f"- Monthly Premium: ₹{monthly_premium:,}/mo\n"
                f"- Sum Assured: ₹{actual_calc_cover:,}"
            )
        else:
            response_parts.append(f" I couldn't find an eligible plan for **{brand}** in our database.")

    # 3. Construct Final Output
    final_response = "### Requested Premium Details\n\n" + "\n\n".join(response_parts)
    final_response += f"\n\n*Note: Quotes are for a {user_age}y/o {profile.get('gender')}. Final premium is subject to medical underwriting.*"

    return {
        "requested_premiums": new_quotes
    }


# def test_quick_premium():
#     print("--- STARTING TEST: QUICK PREMIUM NODE ---")
    
#     # 1. Setup Mock State
#     mock_state = {
#         "messages": [
#             HumanMessage(content="What is the premium for HDFC Life and Tata AIA?")
#         ],
#         "user_profile": {
#             "age": 30,
#             "gender": "Male",
#             "smoker": False,
#             "income": 1500000  # 15 Lakhs
#         },
#         "life_cover": 10000000, # 1 Crore
#         "cover_till_age": 75,
#         "requested_premiums": []
#     }

#     # 2. Run the Node
#     try:
#         output = quick_premium_node(mock_state)
        
#         print("\n--- TEST RESULTS ---")
#         print(f"Number of Quotes Found: {len(output.get('requested_premiums', []))}")
        
#         for quote in output.get('requested_premiums', []):
#             print(f"\nCompany: {quote['company']}")
#             print(f"Premium: ₹{quote['monthly_premium']:,}/mo")
#             print(f"Cover: ₹{quote['sum_assured']:,}")
            
#     except Exception as e:
#         print(f"Test Failed with error: {e}")

# if __name__ == "__main__":
#     test_quick_premium()
# premium tool integration

# plan_id validation
