from google.genai import types
from graphs.master_advisor import client
from graphs.life_subgraph.life_state import TermLifeState
from langchain_core.messages import HumanMessage, AIMessage


def consultant_reasoner_node(state: TermLifeState):
    print('\n Consultant Node')
    
    # 1. Prepare data for the prompt
    profile = state.get("user_profile")
    user_pref = state.get("user_preferences", "Not specified")
    top_plans = state.get("plan_options", [])
    target_cover = state.get("life_cover")
    target_age = state.get("cover_till_age")
    
    # Format the plans into a readable list for the LLM
    plans_context = ""
    for idx, plan in enumerate(top_plans):
        chunks_str = ""
        for c in plan.get('matched_chunks', []):
            short_desc = (c['desc'][:200] + '...') if len(c['desc']) > 200 else c['desc']
            chunks_str += f"- {short_desc} (Extra Cost: {c['extra_premium_pct']*100}%)\n"

        plans_context += (
            f"P{idx+1}: {plan['company_name']} | ₹{plan['calculated_premium']}/mo | CSR: {plan['csr']}% | Score: {plan['total_score']}\n"
            f"Riders: {chunks_str}\n"
        )

    # 2. Define the System Prompt
    system_instruction = (
        "You are a specialized Insurance Actuary and Advisor. Your goal is to guide the user toward the best life insurance "
        "by balancing personal goals with financial reliability. You MUST calculate the 'Final Quoted Price' by "
        "adding the costs of all recommended PAID ADD-ONS to the base premium."
    )

    # 3. Define the User Prompt
    user_prompt = f"""
    Hello! I need you to analyze these top 10 life insurance plans for our client, {profile.get('name')}.
    
    ### CLIENT PROFILE:
    - Age: {profile.get('age')}
    - Gender: {profile.get('gender')}
    - Income: ₹{profile.get('income')} LPA
    - Smoker: {"Yes" if profile.get('smoker') else "No"}
    - Requested Cover: ₹{target_cover:,}
    - Coverage Duration: Until age {target_age}
    - Primary Goal/Preference: "{user_pref}"

    ### TOP CALCULATED PLANS:
    {plans_context}

    ### YOUR TASK:
    1. **Personalized Opening**: Start by acknowledging {profile.get('name')}'s specific goal (e.g., '{user_pref}').
    2. **Re-rank and present the TOP 3 plans that best suit the user's intent. 
    3. **For the #1 choice, write a personalized reasoning explaining WHY each specifically for his preference, even if it's not the absolute cheapest. 
    4. **The Trade-offs**: Compare the top 2-3 plans. Mention 'Premium' vs. 'CSR (Trustworthiness)'. 

    ### FORMATTING:
    - Use Markdown (bolding and bullet points).
    - Keep the tone empathetic, professional, and clear.
    - Avoid insurance jargon where possible.
    """

    # 4. Generate Response
    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.3
        )
    )
    
    # print(f"DEBUG: Input Tokens = {response.usage_metadata.prompt_token_count}")
    print("RESPONSE:\n", response.text)

    memory_context = "Recommended Top 5 Plans:\n"
    for p in top_plans:
        # Get the top 2 rider names only, no descriptions
        riders = [c['desc'].split(':')[0][:20] for c in p.get('matched_chunks', [])[:2]]
        rider_tags = ", ".join(riders)
        
        plan_desc = f"- {p['company_name']} ({p['plan_name']}): ₹{p['calculated_premium']}/mo. " \
                    f"Key: {rider_tags if rider_tags else 'Pure Term'}. CSR: {p['csr']}%."
        
        memory_context += plan_desc + "\n"

    full_response = response.text
    history_summary = (
        f"Assistant analyzed life plans for {profile.get('name')}.\n"
        f"{memory_context}\n"
        "Decision Logic: Prioritized CSR and user preference for " + user_pref
    )

    return {
        "recommendation_reasoning": response.text,
        "messages": [AIMessage(content=history_summary)] 
    }
# reranking and top-k handling

# top-k rerank limit
