from collections import defaultdict
import os
from graphs.life_subgraph.life_state import TermLifeState
from graphs.master_advisor import client
from pinecone import Pinecone

# Initialize Pinecone
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index("insurance-benefits")

def semantic_engine_node(state: TermLifeState):
    print("--- SEMANTIC ENGINE: MULTI-QUERY + RRF ---")

    profile = state.get('user_profile')
    user_pref = state.get('user_preferences', "Comprehensive Protection")
    user_age = profile.get('age')
    required_cover = state.get('life_cover')
    requested_cover_age = state.get('cover_till_age')
    income = profile.get('income')
    
    # 1. Eligibility Filter (The Gatekeeper)
    eligibility_filter = {
        "$and": [
            {"min_age": {"$lte": user_age}},
            {"max_age": {"$gte": user_age}},
            {"min_cover": {"$lte": required_cover}},
            {"max_cover": {"$gte": required_cover}},
            {"max_cover_age": {"$gte": requested_cover_age}},
            {"min_cover_age": {"$lte": requested_cover_age}}
        ]
    }

    # 2. Query Expansion: Use Gemini to create 3 technical sub-queries
    expansion_prompt = f"""
    You are an insurance actuary. Expand this user preference into 3 distinct, 
    highly technical search queries for a vector database to find insurance riders.
    Preference: {user_pref}
    Return ONLY a Python list of strings.
    """
    expansion_res = client.models.generate_content(
        model="gemini-2.5-flash", 
        contents=expansion_prompt
    )
    # Simple parsing to get queries (cleaning up any markdown)
    sub_queries = [q.strip(' "-*') for q in expansion_res.text.strip().split('\n') if len(q) > 5][:3]
    if not sub_queries: sub_queries = [user_pref]

    print("Sub-Queries\n",sub_queries)

    # 3. Parallel Execution & RRF Accumulation
    k = 60
    rrf_scores = defaultdict(float)
    plan_metadata = {}
    namespaces = ["insurance/free_benefits", "insurance/addons"]

    for query_text in sub_queries:
        for ns in namespaces:
            results = index.search_records(
                namespace=ns,
                query={
                    "top_k": 20,
                    "inputs": {"text": query_text},
                    "filter": eligibility_filter
                }
            )
            
            hits = results.get("result", {}).get("hits", [])
            seen_in_query = set()

            for rank, hit in enumerate(hits, start=1):
                m = hit["fields"]
                pid = m["plan_id"]

                # RRF on Plan ID (Grouped)
                if pid not in seen_in_query:
                    rrf_scores[pid] += 1.0 / (k + rank)
                    seen_in_query.add(pid)

                # Initialize Plan Meta if new
                if pid not in plan_metadata:
                    plan_metadata[pid] = {
                        "plan_id": pid,
                        "company": m["company"],
                        "matched_chunks": []
                    }

                # --- BENEFIT CALCULATION LOGIC ---
                template = m.get("template", "")
                formula = m.get("formula_type", "static")
                mult = m.get("multiplier", 0)

                if formula == "fixed_amt":
                    val = mult
                elif formula == "percentage_of_cover":
                    val = required_cover * mult
                elif formula == "income_multiplier":
                    val = income * mult
                elif formula == "health_tier":
                    val = required_cover * 0.005 # Logic: 0.5% of cover for wellness
                else:
                    val = 0

                personalized_benefit = template.replace("{val}", f"{int(val):,}")
                
                # Format final description for the Consultant LLM
                prefix = "[FREE]" if "free_benefits" in ns else f"[ADD-ON +{int(m.get('extra_premium_pct', 0)*100)}%]"
                final_desc = f"{prefix} {m['title']}: {personalized_benefit}. {m['chunk_text']}"

                # Add to chunks if not already added (de-duplication)
                if m['title'] not in [c['title'] for c in plan_metadata[pid]["matched_chunks"]]:
                    plan_metadata[pid]["matched_chunks"].append({
                        "title": m["title"],
                        "desc": final_desc,
                        "score": hit["_score"],
                        "is_free": "free_benefits" in ns,
                        "extra_premium_pct": m.get("extra_premium_pct", 0)
                    })

    # 4. Normalize RRF for the Ranker
    max_rrf = max(rrf_scores.values()) if rrf_scores else 1.0
    final_output = []
    for pid, rrf_val in rrf_scores.items():
        entry = plan_metadata[pid]
        entry["max_semantic_score"] = round(rrf_val / max_rrf, 4)
        final_output.append(entry)

    return {"semantic_data": final_output}


# if __name__ == "__main__":
#     # 1. Mock the State
#     test_state = {
#         "user_profile": {
#             "name": "Pratik",
#             "age": 30,
#             "income": 3000000,
#             "gender": "Male",
#             "smoker": False
#         },
#         "user_preferences": "I want to secure my children's education and I am worried about road accidents because of my driving job.",
#         "life_cover": 10000000,
#         "cover_till_age": 70,
#         "messages": []
#     }

#     # 2. Run the Node
#     print(f"Testing Semantic Engine with Query: {test_state['user_preferences']}\n")
#     result = semantic_engine_node(test_state)

#     # 3. Analyze Results
#     semantic_data = result["semantic_data"]
    
#     # Sort by the new RRF score to see the winners
#     sorted_plans = sorted(semantic_data, key=lambda x: x["max_semantic_score"], reverse=True)

#     print(f"\n--- TOP 3 RETRIEVED PLANS (RRF RANKED) ---")
#     for plan in sorted_plans[:3]:
#         print(f"\nPLAN: {plan['company']} (ID: {plan['plan_id']})")
#         print(f"RRF Score: {plan['max_semantic_score']}")
#         print("Matched Riders:")
#         for chunk in plan['matched_chunks'][:4]: # Show first 4 riders
#             print(f"  - {chunk['title']}")