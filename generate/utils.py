import json
from pathlib import Path

# Project root = InsuranceAdvisor/
BASE_DIR = Path(__file__).resolve().parent.parent

DATA_FILE = BASE_DIR / "data" / "term_life_companies.json"

def load_companies():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

COMPANIES = load_companies()
