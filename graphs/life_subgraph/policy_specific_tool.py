import os
import json
from langchain_core.messages import HumanMessage
from graphs.life_subgraph.life_state import TermLifeState
from graphs.master_advisor import client
from pinecone import Pinecone
from generate.life_endpoint import COMPANIES, EXCLUSION_POOL
from graphs.life_subgraph.get_plans import get_brand_performance_stats

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index("insurance-benefits")

def policy_expert_node(state: TermLifeState):
    print("\n--- POLICY EXPERT: INTELLIGENT RETRIEVAL ---")
    
    context_messages = state["messages"][-10:]
    last_msg = context_messages[-1].content

    history_str = "\n".join([f"{type(m).__name__}: {m.content}" for m in context_messages])

    plan_options = state.get("plan_options", [])

    # print(plan_options)
    
    # Map currently recommended plans for context-aware mapping
    context_summary = [
        {"rank": i+1, "plan_id": p['plan_id'], "company": p['company_name']} 
        for i, p in enumerate(plan_options)
    ]

    context_companies = list(set([p['company_name'] for p in plan_options]))

    # 2. Intent Extraction & Brand Normalization
    extraction_prompt = f"""
    User Message: "{last_msg}"
    History: {history_str}
    Top Contextual Plans (Top 10): {context_summary}
    Master Brand List: {COMPANIES}

    Task:
    1. Determine if the user is asking about the Top 10 context (e.g., "first one, second one like that").
    2. Determine if the user is asking about a specific brand globally (e.g., "What about LIC?").
    3. Normalize mentioned brands to match the Master Brand List EXACTLY.
    4. Generate a technical insurance query (e.g., 'critical illness coverage clauses').

    Return JSON ONLY:
    {{
        "mentioned_brands": ["string"], "search_query": "string"
    }}
    """
    
    extraction_res = client.models.generate_content(
        model="gemini-2.5-flash", 
        contents=extraction_prompt,
        config={"response_mime_type": "application/json"}
    )
    
    meta = json.loads(extraction_res.text)
    
    final_targets = list(set(context_companies + meta.get("mentioned_brands", [])))


    # Postgres lookup for csr and other stats
    brand_stats = []
    if final_targets:
        # Example: SELECT company_name, csr, avg_settlement_days FROM master_plans WHERE company_name IN (...)
        brand_stats = get_brand_performance_stats(final_targets)

    search_filter = {}
    if final_targets:
        search_filter = {"company": {"$in": final_targets}}

    print(f"DEBUG: Unified Search for brands: {final_targets}")

    # 4. Multi-Namespace Vector Search (Type-Aware)
    namespaces = {
        "insurance/free_benefits": "FREE BENEFIT", 
        "insurance/addons": "PAID ADD-ON/RIDER"
    }
    fact_chunks = []

    for ns, type_label in namespaces.items():
        results = index.search_records(
            namespace=ns,
            query={
                "top_k": 10,
                "inputs": {"text": meta['search_query']},
                "filter": search_filter
            }
        )
        hits = results.get("result", {}).get("hits", [])
        for hit in hits:
            m = hit['fields']

            fact_chunks.append(
                f"TYPE: {type_label} | "
                f"PLAN: {m['company']} | "
                f"TITLE: {m['title']} | "
                f"CLAUSE: {m['chunk_text']}"
            )

    # 5. Synthesis & Reasoning
    brand_stats_str = "\n".join([
        f"BRAND: {s['company_name']} | CSR: {s['csr']}% | Avg Settlement: {s['avg_settlement_days']} days | Solvency Ratio: { s['solvency_ratio']}" 
        for s in brand_stats
    ])

    if not fact_chunks:
        synthesis_content = "I couldn't find specific technical clauses for that request in our database."
    else:
        synthesis_prompt = f"""
        Answer the user's question using the technical insurance data provided.
        User: {last_msg}

        --- BRAND PERFORMANCE (POSTGRES DATA) ---
        {brand_stats_str}
        
        DATA:
        {chr(10).join(fact_chunks)}

        INSTRUCTIONS:
        - If comparing, use a clear comparative structure (e.g., Side-by-Side or Bulleted sections).
        - Distinguish clearly between FREE benefits and PAID add-ons.
        - No Hallucination:If the DATA does not contain the answer, say: "The technical documents provided do not contain specific details on [topic]. Please refer to the official Policy Wordings for this specific clause."
        - If the brand was NOT in the initial Top 10 recommendations, explain that this might be 
          due to higher premiums or eligibility criteria for the user's specific profile.
        - IF USER ASKS ABOUT EXCLUSIONS, refer to these industry-standard exclusions: {EXCLUSION_POOL}   
        """
        
        final_res = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=synthesis_prompt
        )
        synthesis_content = final_res.text

    return {"policy_facts": synthesis_content}



# # Mocking the state structure
# def test_policy_expert():
#     print("--- STARTING TEST: POLICY EXPERT NODE ---")
#     mock_state = {
#         "messages": [
#             HumanMessage(content="What are the free benefits of the second recommended plan and HDFC?")
#         ],
#         "plan_options": [
#             {
#                 "plan_id": "TATA_001", 
#                 "company_name": "Tata AIA Life Insurance", 
#                 "premium": 1200
#             },
#             {
#                 "plan_id": "SBI_99", 
#                 "company_name": "SBI Life Insurance", 
#                 "premium": 1100
#             }
#         ],
#         "policy_facts": "" # This is what the node will fill
#     }

#     # 2. Run the Node
#     try:
#         output = policy_expert_node(mock_state)
        
#         print("\n--- TEST RESULTS ---")
#         print(f"Policy Facts Generated:\n{output.get('policy_facts')}")
        
#     except Exception as e:
#         print(f"Test Failed with error: {e}")

# if __name__ == "__main__":    
#     test_policy_expert()
# hybrid search and response formatting

# policy expert response formatting
