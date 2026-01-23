import psycopg2
from psycopg2.extras import RealDictCursor

def get_eligible_plans_from_db(user_age, requested_cover, requested_age):
    """
    Connects to Postgres and returns plans where the user fits 
    within the age and coverage boundaries.
    """
    conn = psycopg2.connect(
        dbname="insuranceadvisor",
        user="postgres",
        password="postgres",
        host="localhost",
        port="5442"
    )
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            query = """
            SELECT * FROM insurance_plans 
            WHERE %s BETWEEN min_entry_age AND max_entry_age
            AND %s BETWEEN min_cover_till_age AND max_cover_till_age
            AND %s BETWEEN min_life_cover AND max_life_cover;
            """
            cur.execute(query, (user_age, requested_age, requested_cover))
            return cur.fetchall()
    finally:
        conn.close()

def get_specific_plan_from_db(target_company, user_age, requested_cover, requested_age):
    """
    Fetches the specific plan for a company, but ONLY if the user 
    meets the eligibility criteria for that plan.
    """
    conn = psycopg2.connect(
        dbname="insuranceadvisor",
        user="postgres",
        password="postgres",
        host="localhost",
        port="5442"
    )
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # We add 'company ILIKE %s' for case-insensitive matching
            query = """
            SELECT * FROM insurance_plans 
            WHERE company_name ILIKE %s
            AND %s BETWEEN min_entry_age AND max_entry_age
            AND %s BETWEEN min_cover_till_age AND max_cover_till_age
            AND %s BETWEEN min_life_cover AND max_life_cover
            LIMIT 1;
            """
            # target_company is passed first to match the first %s
            cur.execute(query, (target_company, user_age, requested_age, requested_cover))
            return cur.fetchone()
    finally:
        conn.close()

import psycopg2
from psycopg2.extras import RealDictCursor



def get_brand_performance_stats(brand_names: list):
    """
    Fetches trust metrics (CSR, Settlement Days) for a list of company names.
    Used by the Policy Expert to justify plan reliability.
    """
    if not brand_names:
        return []

    conn = psycopg2.connect(
        dbname="insuranceadvisor",
        user="postgres",
        password="postgres",
        host="localhost",
        port="5442"
    )
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # We use ANY(%s) to match the list of names in a single query
            # We select DISTINCT to avoid duplicate brand stats if multiple plans exist
            query = """
            SELECT DISTINCT 
                company_name, 
                claim_settlement_ratio AS csr, 
                avg_settlement_days,
                solvency_ratio
            FROM insurance_plans 
            WHERE company_name = ANY(%s);
            """
            cur.execute(query, (brand_names,))
            return cur.fetchall()
    except Exception as e:
        print(f"Error fetching brand stats: {e}")
        return []
    finally:
        conn.close()




# plan filtering and premium tool integration
