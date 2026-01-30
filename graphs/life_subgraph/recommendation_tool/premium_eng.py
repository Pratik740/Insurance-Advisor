from graphs.life_subgraph.life_state import TermLifeState
from graphs.life_subgraph.calc_premium import calculate_premium, max_cover_by_income
from graphs.life_subgraph.get_plans import get_eligible_plans_from_db

def premium_engine_node(state: TermLifeState):
    print("--- PREMIUM ENGINE ---")
    profile = state.get("user_profile")
    user_age = profile.get('age')
    annual_income = profile.get('income')    
    requested_cover = state.get("life_cover")
    requested_till_age = state.get("cover_till_age")

    # 1. Financial Eligibility Check
    # We cap the coverage for calculation based on the user's income
    max_allowed = max_cover_by_income(user_age, annual_income)
    actual_calc_cover = min(requested_cover, max_allowed)
    
    if actual_calc_cover < requested_cover:
        print(f"Note: Coverage capped at {actual_calc_cover} based on income multiplier.")

    # 2. Fetch Eligible Plans from Postgres
    eligible_raw_plans = get_eligible_plans_from_db(
        user_age, 
        actual_calc_cover, 
        requested_till_age
    )

    if not eligible_raw_plans:
        print("No eligible plans found in database for these criteria.")
        return {"plan_options": []}

    # 3. Calculate Premium for each plan found
    final_quotes = []
    for plan in eligible_raw_plans:
        monthly_premium = calculate_premium(
            base_rate=float(plan['base_rate']),
            age=user_age,
            life_cover=actual_calc_cover,
            cover_till_age=requested_till_age,
            smoker=profile.get('smoker'),
            gender=profile.get('gender'),
            occupation="salaried"
        )

        final_quotes.append({
            "plan_id": plan['plan_id'],
            "company_name": plan['company_name'],
            "plan_name": plan['plan_name'],
            "calculated_premium": monthly_premium,
            "csr": plan['claim_settlement_ratio'],
            "solvency": plan['solvency_ratio'],
            "settlement_days": plan['avg_settlement_days']
        })

    # Update the state with the list of quotes
    return {"raw_premiums": final_quotes}





# premium scoring edge cases

# score normalization
