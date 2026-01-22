import random 

def generate_addons(life_cover, cover_till_age, plan_id):
    """
    Generates a list of 3-4 realistic add-ons based on life cover and policy duration.
    """
    if plan_id:
        random.seed(plan_id)
    addons = []
    
    # 1. Free health benefits (Scales with life cover)
    # Calculation: ~0.3% of life cover, capped between 5k and 50k
    health_benefit_amt = min(max(5000, (life_cover // 1000) * 3), 50000)
    addons.append({
        "title": "Free Health Benefits",
        "description": f"Complimentary health check-ups and wellness benefits up to ₹{health_benefit_amt:,}/yr.",
        "type": "Wellness"
    })

    # 2. Early payout on terminal illness
    # 50% payout capped at 2 Crores
    terminal_payout_limit = min(life_cover // 2, 20_00_00_000)
    addons.append({
        "title": "Terminal Illness Early Payout",
        "description": f"Accelerated payout of 50% (up to ₹{terminal_payout_limit:,}) on diagnosis of terminal illness; remaining 50% paid on death.",
        "type": "Accelerated Benefit"
    })

    # 3. Premium Deferral (Always applicable after 5 years)
    addons.append({
        "title": "Premium Holiday",
        "description": "Option to defer premiums for 12 months after 5 policy years without interest. Available every 5-year gap.",
        "type": "Flexibility"
    })

    # 4. Immediate payout on claim intimation
    # Calculation: ~3% of life cover, capped at 10 Lakhs
    immediate_payout = min(max(100000, (life_cover // 100) * 3), 10_00_000)
    addons.append({
        "title": "Insta-Claim Support",
        "description": f"Immediate payout of ₹{immediate_payout:,} upon receipt of death claim intimation for interim family support.",
        "type": "Immediate Relief"
    })

    # 5. Future Premium Waiver (Terminal Illness)
    addons.append({
        "title": "Waiver of Premium (TI)",
        "description": "All future premiums are waived off once a Terminal Illness claim is paid, while the life cover continues.",
        "type": "Protection"
    })

    # 6. Return of Premium (Conditional on age)
    if cover_till_age >= 90:
        addons.append({
            "title": "Special Maturity Benefit",
            "description": "Return of all base premiums paid if the life assured survives till the policy maturity (Age 90+).",
            "type": "Return of Premium"
        })

    # 7. Additional Real-world: Child Education Support
    edu_support = life_cover // 10 # 10% of cover
    addons.append({
        "title": "Child Education Cover",
        "description": f"Additional lump sum of ₹{edu_support:,} provided specifically for children's education upon death claim.",
        "type": "Targeted Benefit"
    })

    num_to_select = 4 # Or use a fixed number to avoid variation
    selected = random.sample(addons, k=num_to_select)
    
    # Reset seed to None so other random calls in the app stay truly random
    random.seed(None)     
    return selected



    
# premium calculation edge cases
