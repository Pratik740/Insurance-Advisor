import json
import random
from pathlib import Path
from generate.premium import generate_addons

COMPANIES = [
    "Life Insurance Corporation of India (LIC)",
    "SBI Life Insurance",
    "HDFC Life Insurance",
    "ICICI Prudential Life Insurance",
    "Tata AIA Life Insurance",
    "Bajaj Allianz Life Insurance",
    "Max Life Insurance",
    "Kotak Mahindra Life Insurance",
    "Aditya Birla Sun Life Insurance",
    "PNB MetLife India Insurance",
    "IndiaFirst Life Insurance",
    "Exide Life Insurance",
    "Shriram Life Insurance",
    "Sahara India Life Insurance",
    "Reliance Nippon Life Insurance",
    "HDFC ERGO General Insurance",
    "ICICI Lombard General Insurance",
    "Tata AIG General Insurance",
    "Bajaj Allianz General Insurance",
    "SBI General Insurance",
    "Go Digit General Insurance",
    "Acko General Insurance",
    "Star Health & Allied Insurance",
    "Care Health Insurance",
    "Niva Bupa Health Insurance",
    "Aditya Birla Health Insurance",
    "ManipalCigna Health Insurance",
    "Future Generali India Insurance",
    "IFFCO Tokio General Insurance",
    "Reliance General Insurance",
    "Royal Sundaram General Insurance",
    "Cholamandalam MS General Insurance",
    "Liberty General Insurance",
    "National Insurance Co. Ltd.",
    "The New India Assurance Co. Ltd.",
    "The Oriental Insurance Co. Ltd.",
    "United India Insurance Co. Ltd.",
    "Allianz",
    "AXA",
    "MetLife",
    "Cigna",
    "Generali",
    "Sumitomo Mitsui Insurance",
    "AIG",
    "Liberty Mutual"
]

PLAN_NAME_POOL = [
    "Pure Term Life Plan",
    "Secure Life Term Plan",
    "Smart Protect Term Plan",
    "Life Shield Term Assurance",
    "Prime Term Protection Plan"
]

FEATURE_POOL = [
    "Death benefit payout",
    "Tax benefit under Section 80C",
    "Life-stage cover enhancement",
    "Flexible premium payment options"
]

EXCLUSION_POOL = [
    "Suicide within first 12 months",
    "Fraudulent non-disclosure",
    "War or terrorism-related death",
    "High Risk activities like adventure sports"
]

RIDER_POOL = [
    "Accidental Death Benefit Rider",
    "Critical Illness Rider"
]


def generate_company(index, company_name):
    return {
        "company_name": company_name,
        "plan_id": f"COMP_{index:03d}",
        "plan_name": random.choice(PLAN_NAME_POOL),
        "claim_settlement_ratio": round(random.uniform(97.0, 99.8), 2),

        "min_entry_age": 18,
        "max_entry_age": random.choice([50, 55, 57]),

        "min_cover_till_age": 60,
        "max_cover_till_age": random.choice([80, 85, 90, 95]),

        "min_life_cover": 50_00_000,
        "max_life_cover": random.choice([
            1_00_00_000,
            2_00_00_000,
            5_00_00_000,
            10_00_00_000
        ]),
        "base_rate": round(random.uniform(0.8, 1.05), 2),

        "solvency_ratio": round(random.uniform(1.6, 2.5), 2),
        "avg_claim_settlement_days": random.choice([1, 2, 3, 5, 7]),
        "digital_purchase_discount": random.choice([5, 10, 15]),
        
        "features": FEATURE_POOL,
        "exclusions": EXCLUSION_POOL,
        "optional_riders": random.sample(RIDER_POOL, k=2),
    }


def generate_companies():
    return [
        generate_company(i + 1, name)
        for i, name in enumerate(COMPANIES)
    ]


if __name__ == "__main__":
    BASE_DIR = Path(__file__).resolve().parent.parent
    DATA_DIR = BASE_DIR / "data"
    DATA_DIR.mkdir(exist_ok=True)

    output_file = DATA_DIR / "term_life_companies.json"

    companies = generate_companies()

    with open(output_file, "w") as f:
        json.dump(companies, f, indent=2)

    print(f"Generated {len(companies)} companies with exactly ONE term life plan each")
