from fastapi import FastAPI, HTTPException
from generate.utils import COMPANIES
from generate.premium import calculate_premium, generate_addons
from pydantic import BaseModel
import psycopg2

app = FastAPI(title="Insurance Advisor API")


def max_cover_by_income(age, annual_income):
    if age < 35:
        return annual_income * 20
    elif age < 45:
        return annual_income * 15
    elif age < 55:
        return annual_income * 10
    else:
        return annual_income * 7



# 1️⃣ Get all companies
@app.get("/insurance/term-life/companies")
def get_companies():
    return COMPANIES


# 2️⃣ Get company by plan_id
@app.get("/insurance/term-life/companies/{plan_id}")
def get_company(plan_id: str):
    company = next((c for c in COMPANIES if c["plan_id"] == plan_id), None)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


@app.post("/insurance/term-life/premium")
def premium(payload: dict):
    plan_id = payload["plan_id"]
    age = payload["age"]
    income = payload["annual_income"]
    requested_cover = payload["life_cover"]

    # 1. Fetch plan details from Postgres
    conn = get_db_connection() # Your helper function to connect to 5442
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    # Check if plan exists AND if user meets age/cover constraints in one go
    query = """
        SELECT * FROM insurance_plans 
        WHERE plan_id = %s 
          AND %s BETWEEN min_entry_age AND max_entry_age
          AND %s <= max_life_cover
    """
    cur.execute(query, (plan_id, age, requested_cover))
    plan = cur.fetchone()
    cur.close()
    conn.close()

    if not plan:
        raise HTTPException(
            status_code=404, 
            detail="Plan not found or you are not eligible based on age/cover limits."
        )

    # 2. Income validation (Logical check)
    max_allowed = max_cover_by_income(age, income)
    if requested_cover > max_allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Cover exceeds limit of ₹{max_allowed:,} for your income."
        )

    # 3. Calculation using DB values
    annual = calculate_premium(
        base_rate=float(plan["base_rate"]), # Use DB base_rate
        age=age,
        life_cover=requested_cover,
        cover_till_age=payload["cover_till_age"],
        smoker=payload.get("smoker", False),
        gender=payload["gender"],
        occupation=payload["occupation"]
    )

    return {
        "company_name": plan["company_name"],
        "plan_name": plan["plan_name"],
        "annual_premium": annual,
        "monthly_premium": round(annual / 12),
        "max_cover_allowed": max_allowed,
        "csr": float(plan["claim_settlement_ratio"]) # Bonus: Show reliability
    }


class AddonRequest(BaseModel):
    plan_id: str
    life_cover: int
    cover_till_age: int

@app.post("/insurance/term-life/benefits")
async def get_plan_benefits(payload: AddonRequest):
    # Check if plan exists
    company = next((c for c in COMPANIES if c["plan_id"] == payload.plan_id), None)
    if not company:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    # Generate dynamic benefits based on the user's specific selection
    dynamic_addons = generate_addons(payload.life_cover, payload.cover_till_age, payload.plan_id)
    
    return {
        "company_name": company["company_name"],
        "plan_name": company["plan_name"],
        "life_cover_selected": payload.life_cover,
        "benefits": dynamic_addons
    }       