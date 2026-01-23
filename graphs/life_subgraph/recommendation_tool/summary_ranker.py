from graphs.life_subgraph.life_state import TermLifeState

def summary_ranker_node(state: TermLifeState):
    print("--- JOINING & RANKING RESULTS ---")
       
    # Separate Premium results from Semantic results
    raw_premiums = state.get('raw_premiums',[])
    semantic_hits = state.get('semantic_data',[])

    if not raw_premiums:
        print("No premium data found to rank.")
        return {"plan_options": []}
        
    # Map plan_id -> max_semantic_score for easy lookup
    semantic_map = {item['plan_id']: item for item in semantic_hits}

    # 2. Price Normalization
    # We need the min/max premium to scale prices between 0 and 1
    all_prices = [p['calculated_premium'] for p in raw_premiums]
    min_p, max_p = min(all_prices), max(all_prices)

    all_sem_scores = [item['max_semantic_score'] for item in semantic_hits]
    max_s = max(all_sem_scores) if all_sem_scores else 1.0
    min_s = min(all_sem_scores) if all_sem_scores else 0.0

    final_list = []

    for p in raw_premiums:
        pid = p['plan_id']
        sem_info = semantic_map.get(pid)
        
        # Normalize Price: Cheaper (min_p) gets 1.0, Expensive (max_p) gets 0.0
        # Formula: 1 - ((price - min) / (max - min))
        price_score = 1.0 if max_p == min_p else 1 - ((p['calculated_premium'] - min_p) / (max_p - min_p))
        
        # --- Handle Semantic Scoring ---
        if sem_info is not None:
            raw_sem = sem_info['max_semantic_score']

            if max_s == min_s:
                norm_semantic = 1.0 if max_s > 0 else 0.0
            else:
                norm_semantic = (raw_sem - min_s) / (max_s - min_s)

            matched_chunks = sem_info.get('matched_chunks', [])
        else:
            # Plan exists but no semantic match for user query
            norm_semantic = 0.0
            matched_chunks = []

        # 3. Weighted Total Score (60% Features, 40% Price)
        total_score = (norm_semantic * 0.6) + (price_score * 0.4)

        final_list.append({
            **p,
            "total_score": round(total_score, 3),
            "semantic_score": round(norm_semantic, 3),
            "price_score": round(price_score, 3),
            "matched_chunks": matched_chunks
        })

    # 4. Sort by Total Score
    final_list.sort(key=lambda x: x['total_score'], reverse=True)
    # for plan in final_list[:10]:
    #     print(plan)

    # Return the top 10 recommendations
    return {
        "plan_options": final_list[:10],
        "semantic_data": None,
        "raw_premiums": None
    }
# ranking logic and score aggregation
