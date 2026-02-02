import random 

def max_cover_by_income(age, annual_income):
    if age < 35:
        return annual_income * 20
    elif age < 45:
        return annual_income * 15
    elif age < 55:
        return annual_income * 10
    else:
        return annual_income * 7


def calculate_premium(
    base_rate,
    age,
    life_cover,
    cover_till_age,
    smoker=False,
    gender="male",
    occupation="salaried"
):
    age_factor = 1 + max(0, age - 25) * 0.03
    cover_factor = life_cover / 10_000_000

    tenure = cover_till_age - age
    tenure_factor = 1 + max(0, tenure - 30) * 0.01

    smoker_multiplier = 1.3 if smoker else 1.0
    gender_mult = 0.95 if gender.lower() == "female" else 1.0

    occupation_mult = {
        "salaried": 1.0,
        "self_employed": 1.05
    }.get(occupation, 1.0)

    if(cover_till_age >= 85):
        tenure_factor *= 1.25

    premium = (
        base_rate *
        age_factor *
        cover_factor *
        tenure_factor *
        smoker_multiplier *
        gender_mult *
        occupation_mult *
        10_000 
    )

    return round(premium/12)
# calc_premium edge cases

# occupation factor handling
