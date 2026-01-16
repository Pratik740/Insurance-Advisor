import json
import psycopg2
from psycopg2.extras import execute_values

def migrate_json_to_postgres():
    # 1. Load your existing data
    with open("../data/term_life_companies.json", "r") as f:
        data = json.load(f)

    # 2. Connect to your Postgres DB
    conn = psycopg2.connect(
        dbname="insuranceadvisor",
        user="postgres",
        password="postgres",
        host="localhost",
        port="5442"
    )
    cur = conn.cursor()

    # 3. Prepare the insert query
    query = """
    INSERT INTO insurance_plans (
        plan_id, company_name, plan_name, claim_settlement_ratio, 
        min_entry_age, max_entry_age, min_cover_till_age, max_cover_till_age,
        min_life_cover, max_life_cover, base_rate, solvency_ratio,
        avg_settlement_days, digital_purchase_discount
    ) VALUES %s
    ON CONFLICT (plan_id) DO UPDATE SET
        company_name = EXCLUDED.company_name,
        base_rate = EXCLUDED.base_rate;
    """

    # 4. Format data for bulk insertion
    values = [
        (
            item['plan_id'], item['company_name'], item['plan_name'], item['claim_settlement_ratio'],
            item['min_entry_age'], item['max_entry_age'], item['min_cover_till_age'], item['max_cover_till_age'],
            item['min_life_cover'], item['max_life_cover'], item['base_rate'], item['solvency_ratio'],
            item['avg_claim_settlement_days'], item['digital_purchase_discount']
        ) for item in data
    ]

    # 5. Execute and Commit
    execute_values(cur, query, values)
    conn.commit()
    
    print(f"Successfully migrated {len(values)} plans to PostgreSQL.")
    cur.close()
    conn.close()

if __name__ == "__main__":
    migrate_json_to_postgres()