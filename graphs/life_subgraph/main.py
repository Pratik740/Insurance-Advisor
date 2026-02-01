from langgraph.graph import StateGraph, START, END
from graphs.life_subgraph.life_state import TermLifeState
from graphs.master_advisor import client
from graphs.life_subgraph.recommendation_tool.premium_eng import premium_engine_node
from graphs.life_subgraph.recommendation_tool.semantic_eng import semantic_engine_node
from graphs.life_subgraph.recommendation_tool.summary_ranker import summary_ranker_node
from graphs.life_subgraph.recommendation_tool.consultant import consultant_reasoner_node
from graphs.life_subgraph.life_intake_agent import life_intake_agent, check_intake_status
from graphs.life_subgraph.premium_tool import quick_premium_node
from graphs.life_subgraph.merger_node import merger_node
from graphs.life_subgraph.policy_specific_tool import policy_expert_node
from langgraph.types import Command
from google.genai import errors



def life_supervisor(state: TermLifeState):
    print("\n--- SUPERVISOR NODE ---")

    context_messages = state["messages"][-10:]
    last_msg = context_messages[-1].content

    history_str = "\n".join([f"{type(m).__name__}: {m.content}" for m in context_messages])

    reco_done = bool(state.get("recommendation_reasoning"))
    facts_done = bool(state.get("policy_facts"))
    premiums_done = bool(state.get("requested_premiums"))

    print(reco_done, facts_done, premiums_done)
    
    prompt = f"""
    You are an Insurance Expert Orchestrator. Analyze the user query and current progress to decide the NEXT single step.
    Message: "{last_msg}"
    History: {history_str}

    PROGRESS:
    - Full Recommendation Ready: {reco_done}
    - Specific Policy Facts/Riders Found: {facts_done}
    - Specific Premium Quotes Calculated: {premiums_done}

    STRICT OPERATIONAL RULES:
    1. A tool is EXHAUSTED if its status is True. NEVER return a tool name if its task is already True.
    2. If the user's request requires multiple tools, only pick ONE that is currently 'False'.
    3. If all relevant tools for the user's query are already 'True', you MUST exit to 'merger'.
    4. If the user query asks for information that is already marked as 'True' in TASK STATUS, your only valid output is 'merger'.

    RULES:
    1. GOAL CHECK: If all the required information (Recommendation, Facts or Premiums) is ALREADY PRESENT in the PROGRESS section, return 'merger' immediately.
    2. If the user wants a new quote, provides personal details or is starting out and Result Present' is False : return 'recommendation'.
    3. If the user asks for details, benefits,company's performance, riders, or "why" regarding plans already shown and 'Facts Present' is False : return 'policy_expert'.
    4. If the user asks for the price/premium of a SPECIFIC company (e.g. "What is HDFC premium?"): return 'quick_premium'.
    5. If it's a generic greeting or general insurance questions or conversational fluff (e.g. "What is CSR?"): return 'merger'.
    6. If the user is just PROVIDING or UPDATING information (like cover amount, age, or income) without asking a specific question: return 'merger'. 
       The Intake Agent will have already updated the state; no further calculation is needed yet.

    TOOL CAPABILITIES:
    - 'quick_premium': Calculates NEW prices for specific brands based on age/sum assured. Cannot handle policy cancellations or payments.
    - 'policy_expert': Searches technical plan features, riders, and company stats (CSR). Cannot provide actual PDF downloads or personal policy account details.
    - 'recommendation': Ranks top plans based on profile.
    - 'merger': This is the FINAL RESOLUTION node. Use it if:
        1. All requested information (Premiums/Facts) is already present in PROGRESS.
        2. The user's question is generic (e.g., "What is a nominee?", "Explain CSR").
        3. The user is just chatting, greeting, or saying "thank you".
        4. The user's request is OUT-OF-SCOPE (e.g., asking for PDFs, logging in, or non-insurance topics). 
           The merger will handle the "I cannot do that" response gracefully.

    STRICT OPERATIONAL LOGIC:
    - MISSION: Identify ONLY the immediate data requested by the user. 
    - ELIMINATION RULE 1: If the user did not explicitly ask for a comparison, ranking, or "best plan," NEVER return 'recommendation'.
    - ELIMINATION RULE 2: If the user asked only for a price for a specific brand and the PREMIUMS_FETCHED boolean is True, you MUST return 'merger'.
    - ELIMINATION RULE 3: Do NOT fill booleans just because they are False. Only fill a boolean if the USER message requires it.
    - ELIMINATION RULE 4: If you find yourself thinking "I should also show them..." STOP. Only provide what was asked.

    DECISION TREE:
    1. Is the user's specific question already answered by the data in [FACTS] or [PREMIUMS]? 
       - YES -> 'merger'
    2. Is the user's question about price/premium? 
       - YES (and Boolean is False) -> 'quick_premium'
    3. Is the user's question about company performance/stats/riders?
       - YES (and Boolean is False) -> 'policy_expert'
    4. Is the user asking for a broad "best plan" suggestion for their profile?
       - YES -> 'recommendation'
    5. EVERYTHING ELSE -> 'merger'

    NOTE:
    1. If the user query requires multiple tools, pick the most logical one to run FIRST. You will be called again after it finishes.
    2. NEVER RERUN THE SAME TOOL AGAIN. ALWAYS CHECK WHAT ALL INFORMATION ARE PRESENT AND WHAT NOT AND THEN DECIDE THE NEXT STEP. 
    3. There is no need of running each tool everytime, intelligently decide which tool should be run next as per the user query.

    OUT-OF-SCOPE RULE:
    If the user asks for:
    1. Actual PDF downloads/brochure files.
    2. Modifying an existing real-world policy.
    3. Payment, banking, or technical support for a website.
    4. Anything not related to Life Insurance advice.
    ... Then return 'merger' immediately and do NOT call any other tool

    Return ONLY: 'quick_premium', 'recommendation', 'policy_expert', or 'merger'.
    """
    
    try:
        res = client.models.generate_content(model="gemini-3-flash-preview", contents=prompt)
    except errors.ServerError:
        # Fallback to the rock-solid production model
        print("Gemini 3 overloaded, falling back to Gemini 1.5 Flash...")
        res = client.models.generate_content(model="gemini-2.5-flash-lite", contents=prompt)

    decision = res.text.strip().lower()

    if "quick_premium" in decision:
        # If the user is agreeing to a NEW suggn (like 3Cr, ), 
    # force them back through the intake agent to update the variables
        if not state.get("is_complete"):
            return Command(goto="intake_agent", update={"action_type": "quick_quote"})
        return Command(goto="quick_premium_node", update={"action_type": "quick_quote"})

    if "recommendation" in decision:
        if not state.get("is_complete"):
            return Command(goto="intake_agent", update={"action_type": "full_reco"})
        return Command(goto=["premium_engine", "semantic_engine"], update={"action_type": "full_reco"})
    
    if "policy_expert" in decision:
        return Command(goto="policy_expert")
    
    return Command(goto="merger_node")


life_builder = StateGraph(TermLifeState)

life_builder.add_node("supervisor", life_supervisor)

# Recommendation
life_builder.add_node("intake_agent", life_intake_agent)

life_builder.add_node("quick_premium_node", quick_premium_node) 

life_builder.add_node("premium_engine", premium_engine_node)
life_builder.add_node("semantic_engine", semantic_engine_node)
life_builder.add_node("summary_ranker", summary_ranker_node)
life_builder.add_node("consultant_reasoner", consultant_reasoner_node)

life_builder.add_node("policy_expert", policy_expert_node)

life_builder.add_node("merger_node", merger_node)



life_builder.add_edge(START, "supervisor")

# Parallel Fan-out 
life_builder.add_conditional_edges(
    "intake_agent",
    check_intake_status,
    {
        "intake_agent": "intake_agent",
        "quick_premium_node": "quick_premium_node",
        "premium_engine": "premium_engine",
        "semantic_engine": "semantic_engine"
    }
)

# Parallel Fan-in 
life_builder.add_edge("premium_engine", "summary_ranker")
life_builder.add_edge("semantic_engine", "summary_ranker")
life_builder.add_edge("summary_ranker", "consultant_reasoner")
life_builder.add_edge("consultant_reasoner", "supervisor")

life_builder.add_edge("quick_premium_node", "supervisor")

life_builder.add_edge("policy_expert", "supervisor")

life_builder.add_edge("merger_node", END)


life_subgraph = life_builder.compile()
# smarter routing and exhaustion rules

# supervisor and merger edge cases

# supervisor tool exhaustion check
