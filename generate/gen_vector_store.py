from pinecone import Pinecone
import os
from dotenv import load_dotenv
import random, json

# Initialize client
load_dotenv()
key = os.getenv("PINECONE_API_KEY")
pc = Pinecone(api_key=key)

index_name = "insurance-benefits"

# Create index if it doesn't exist
if not pc.has_index(index_name):
    pc.create_index_for_model(
        name=index_name,
        cloud="aws",
        region="us-east-1",
        embed={
            "model":"llama-text-embed-v2",
            "field_map":{"text": "chunk_text"}
        }
    )

dense_index = pc.Index(index_name)

FREE_BENEFITS_CATALOG = [
    {"id": "health", "title": "Free Health Benefits", "type": "Wellness", "formula_type": "health_tier", "template": "Complimentary wellness up to ₹{val}/yr.", "desc": "Includes free annual health checkups, dental cleanings, and heart health screenings."},
    {"id": "terminal", "title": "Terminal Illness Early Payout", "type": "Accelerated", "formula_type": "percentage_of_cover", "multiplier": 0.25, "template": "Accelerated payout of ₹{val} upon terminal diagnosis.", "desc": "Get 25% of your life cover early if diagnosed with a terminal or incurable illness."},
    {"id": "premium_holiday", "title": "Premium Holiday", "type": "Flexibility", "formula_type": "static", "template": "Skip premiums for 1 year.", "desc": "Stop paying premiums for up to 12 months during job loss or financial crisis without losing cover."},
    {"id": "insta_claim", "title": "Insta-Claim Support", "type": "Immediate Relief", "formula_type": "fixed_amt", "multiplier": 200000, "template": "Immediate ₹{val} payout within 48 hours.", "desc": "Provides urgent cash relief to families for funeral costs and immediate needs post-demise."},
    {"id": "grief_support", "title": "Grief Counseling Support", "type": "Wellness", "formula_type": "static", "template": "Professional grief counseling for nominees.", "desc": "Mental health and emotional support sessions for family members to cope with loss."},
    {"id": "second_opinion", "title": "Global Medical Second Opinion", "type": "Wellness", "formula_type": "static", "template": "Access to international specialists.", "desc": "Expert medical opinions from top global doctors for complex surgery or critical illness diagnosis."}
]

PAID_ADDONS_CATALOG = [ 
    {"id": "adb", "title": "Accidental Death Benefit", "extra_premium_pct": 0.15, "formula_type": "percentage_of_cover", "multiplier": 1.0, "template": "Additional ₹{val} paid on accidental death.", "desc": "Extra sum assured paid to nominees if death is caused by an accident (road, rail, or air)."},
    {"id": "ci", "title": "Critical Illness Rider", "extra_premium_pct": 0.25, "formula_type": "fixed_list", "template": "Lump sum payout for 36 critical illnesses.", "desc": "Lump sum cash payout upon first diagnosis of Cancer, Heart Attack, or Kidney Failure."},
    {"id": "wop", "title": "Waiver of Premium", "extra_premium_pct": 0.10, "formula_type": "static", "template": "Policy continues for free if disabled.", "desc": "All future premiums are waived if the insured person is diagnosed with a critical illness or disability."},
    {"id": "child_edu", "title": "Child Education Rider", "extra_premium_pct": 0.12, "formula_type": "income_multiplier", "multiplier": 3.0, "template": "Dedicated ₹{val} buffer for child's education.", "desc": "Specific financial support meant for children's higher education fees and school expenses."},
    {"id": "tpd", "title": "Total Permanent Disability", "extra_premium_pct": 0.18, "formula_type": "percentage_of_cover", "multiplier": 0.5, "template": "₹{val} payout if disabled.", "desc": "Provides a lump sum if an accident leads to total permanent disability like loss of limbs or sight."}
]

def populate_from_json(file_path):
    # Load your life.json
    with open(file_path, 'r') as f:
        companies = json.load(f)

    print(f"Starting population for {len(companies)} companies...")

    for plan in companies:
        plan_id = plan["plan_id"]
        company_name = plan["company_name"]
        
        # 1. Extract Eligibility Constraints for Filtering
        eligibility = {
            "min_age": int(plan["min_entry_age"]),
            "max_age": int(plan["max_entry_age"]),
            "min_cover_age": int(plan["min_cover_till_age"]),
            "max_cover_age": int(plan["max_cover_till_age"]),
            "min_cover": int(plan["min_life_cover"]),
            "max_cover": int(plan["max_life_cover"])
        }

        # 2. Randomly select 3-4 Benefits and 2-3 Addons
        selected_free = random.sample(FREE_BENEFITS_CATALOG, random.randint(3, 4))
        selected_paid = random.sample(PAID_ADDONS_CATALOG, random.randint(2, 3))

        # 3. Format Free Benefits Records
        free_records = []
        for item in selected_free:
            # chunk_text is used for semantic search (Integrated Inference)
            free_records.append({
                "_id": f"{plan_id}_{item['id']}",
                "chunk_text": f"{company_name} {item['title']}: {item['desc']}",
                "plan_id": plan_id,
                "company": company_name,
                "title": item['title'],
                "formula_type": item['formula_type'],
                "template": item['template'],
                "multiplier": item.get('multiplier', 0),
                **eligibility
            })

        # 4. Format Addons Records
        addon_records = []
        for item in selected_paid:
            addon_records.append({
                "_id": f"{plan_id}_{item['id']}",
                "chunk_text": f"{company_name} {item['title']} Add-on Rider: {item['desc']}",
                "plan_id": plan_id,
                "company": company_name,
                "title": item['title'],
                "formula_type": item['formula_type'],
                "template": item['template'],
                "multiplier": item.get('multiplier', 0),
                "extra_premium_pct": item['extra_premium_pct'],
                **eligibility
            })

        # 5. Upsert to respective namespaces
        if free_records:
            dense_index.upsert_records(namespace="insurance/free_benefits", records=free_records)
        if addon_records:
            dense_index.upsert_records(namespace="insurance/addons", records=addon_records)

        print(f"Processed {company_name} ({plan_id})")

    print("\n--- DONE ---")
    print(f"Namespaces populated: 'insurance/free_benefits' and 'insurance/addons'")




populate_from_json('../data/term_life_companies.json')
stats = dense_index.describe_index_stats()
print(stats)

# vector store population edge cases
