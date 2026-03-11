from graphs.life_subgraph.life_state import TermLifeState
from graphs.master_advisor import client
import json
from langchain_core.messages import AIMessage


def merger_node(state: TermLifeState):
    print("\n--- MERGER: EXPERT ADVISOR SYNTHESIS ---\n")
    
    context_messages = state["messages"][-10:]
    last_msg = context_messages[-1].content

    history_str = "\n".join([f"{type(m).__name__}: {m.content}" for m in context_messages])

    # Gather intelligence from all tools
    recommendations = state.get("recommendation_reasoning")
    policy_facts = state.get("policy_facts")
    requested_quotes = state.get("requested_premiums", [])
    profile = state.get("user_profile", {})

    # Construct the Knowledge Context
    context = ""
    if recommendations:
        context += f"\nRECOMMENDED PLANS ANALYSIS:\n{recommendations}"
    if policy_facts:
        context += f"\nTECHNICAL POLICY DATA & COMPARISONS:\n{policy_facts}"
    if requested_quotes:
        context += f"\nSPECIFIC QUOTES REQUESTED:\n{json.dumps(requested_quotes)}"

    synthesis_prompt = f"""
    ROLE: You are a Senior Life Insurance Advisor (Actuary Persona).
    USER PROFILE: {profile}
    USER MESSAGE: "{last_msg}"
    HISTORY: {history_str}
    
    CONTEXT DATA FROM RESEARCH TOOLS:
    {context}

    YOUR TASK:
    1. Respond to the user's latest query using the CONTEXT DATA provided.
    2. If the user is asking about recommended plans, use the 'RECOMMENDED PLANS ANALYSIS'.
    3. If they asked for a specific quote, incorporate the 'SPECIFIC QUOTES' data.
    4. DYNAMIC LENGTH RULE:
       - If CONTEXT DATA is provided: Give a detailed, data-driven response (tables, analysis, reasoning).
       - If CONTEXT DATA is "NO TOOL DATA": Be extremely concise and conversational (4-5 sentences). Do not lecture the user.
    5. If no data is found in the context (Generic Query), answer based on general insurance knowledge (CSR, Claim settlement, MWP Act, etc.).
    6. Maintain a professional, empathetic, and data-driven tone. Avoid fluff; be direct.
    
    GUIDELINES:
    - If explaining recommendations, highlight WHY they fit the user's income/age.
    - ALWAYS format policy quotes, product features, and policy comparisons in strict Markdown tables. Do not present plan details as plain text. Use columns like Company, Plan Name, Term, Cover Amount, Premium, etc.
    - Always end with a helpful next step (e.g., "Would you like to see the riders for these plans?").

    STRATEGIC FOLLOW-UP RULES:
    You must end your response with 2-3 specific question that guides the user to a tool we support:
    1. If you just gave a quote: Suggest checking 'Why' this plan is good or its 'Technical Benefits' (Target: policy_expert).
    2. If you just gave a recommendation list: Suggest 'Calculating a specific premium' or 'Policy benefits (Free benefits or Paid addons) related ' for one of them (Target: quick_premium).
    3. If the user updated their profile: Suggest 'Generating a fresh comparison' for the new amount (Target: recommendation).
    4. If the user is confused: Suggest explaining 'CSR' or the 'MWP Act' (Target: general knowledge).
    5. It should be related to the final response generated. 

    NEVER suggest a follow-up that requires external documents (like "Read the PDF") because we don't support that yet.
    """

    res = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=synthesis_prompt
    )

    # Return the final expert response as an AIMessage
    print(res.text)
    return {
        "messages": [AIMessage(content=res.text)],
        "recommendation_reasoning": None,
        "policy_facts": None,
        "requested_premiums": None,
        "action_type": None
    }
# final result formatting and message handling

# merger response formatting

# empty context handling
