"""Pure functions and data for BMI, BMR, TDEE, macronutrients, and meal planning."""

ACTIVITY_MULTIPLIERS = {
    "sedentary": 1.2,
    "light": 1.375,
    "moderate": 1.55,
    "active": 1.725,
    "very_active": 1.9
}

DIET_MACRO_RATIOS = {
    "balanced": {"protein": 0.30, "carbs": 0.40, "fat": 0.30},
    "low_carb": {"protein": 0.35, "carbs": 0.20, "fat": 0.45},
    "high_protein": {"protein": 0.40, "carbs": 0.35, "fat": 0.25},
    "keto": {"protein": 0.25, "carbs": 0.05, "fat": 0.70}
}

TIPS_DATABASE = {
    "weight_loss": [
        "Prioritize high-volume, low-calorie foods such as leafy greens, cucumbers, and berries.",
        "Drink a glass of water 20-30 minutes before every meal to boost satiety.",
        "Ensure every meal contains at least 25-30 grams of lean protein to preserve lean muscle mass.",
        "Limit liquid sugars and hidden calories found in dressings and sweet beverages."
    ],
    "general_health": [
        "Aim for at least 5 portions of diverse colored fruits and vegetables daily.",
        "Replace refined grains with whole grains (quinoa, oats, brown rice) for sustained energy.",
        "Include fermented foods like kefir, yogurt, or kimchi for optimal gut microbiome health.",
        "Cook with healthy unsaturated fats such as extra virgin olive oil and avocado oil."
    ],
    "hydration": [
        "Drink at least 30-35 ml of water per kilogram of body weight daily.",
        "Electrolyte balance is vital: keep sodium, potassium, and magnesium replenished during workouts.",
        "Start your morning with 500ml of room-temperature water to jumpstart metabolism."
    ],
    "superfoods": [
        "Chia & Flax Seeds: High in Omega-3 fatty acids and soluble dietary fiber.",
        "Blueberries: Rich in anthocyanin antioxidants that fight oxidative cellular stress.",
        "Wild Salmon: Excellent source of EPA/DHA and bioavailable complete protein.",
        "Spinach & Kale: Dense with folate, vitamin K, iron, and lutein."
    ]
}

SAMPLE_FOODS = {
    "breakfast": [
        {"name": "Oatmeal with Greek Yogurt & Berries", "calories": 380, "protein": 28, "carbs": 48, "fat": 7},
        {"name": "Scrambled Eggs with Avocado & Whole Grain Toast", "calories": 420, "protein": 24, "carbs": 30, "fat": 22},
        {"name": "Keto Spinach & Cheese Omelet", "calories": 390, "protein": 26, "carbs": 4, "fat": 30}
    ],
    "lunch": [
        {"name": "Grilled Chicken Breast Salad with Quinoa & Olive Oil", "calories": 520, "protein": 45, "carbs": 40, "fat": 18},
        {"name": "Tuna Wrap with Hummus, Spinach and Bell Peppers", "calories": 460, "protein": 38, "carbs": 42, "fat": 14},
        {"name": "Keto Salmon Bowl with Avocado, Cucumber & Sesame", "calories": 550, "protein": 42, "carbs": 8, "fat": 38}
    ],
    "dinner": [
        {"name": "Baked Salmon Fillet with Asparagus and Sweet Potato", "calories": 560, "protein": 44, "carbs": 45, "fat": 20},
        {"name": "Lean Beef Stir-Fry with Broccoli, Snap Peas and Brown Rice", "calories": 580, "protein": 48, "carbs": 50, "fat": 16},
        {"name": "Grilled Turkey Cutlets with Zucchini Noodles and Pesto", "calories": 480, "protein": 46, "carbs": 10, "fat": 26}
    ],
    "snack": [
        {"name": "Handful of Mixed Almonds and Walnuts", "calories": 180, "protein": 6, "carbs": 6, "fat": 16},
        {"name": "Cottage Cheese with Sliced Cucumber and Black Pepper", "calories": 150, "protein": 20, "carbs": 6, "fat": 4},
        {"name": "Whey/Plant Protein Shake with Almond Milk", "calories": 170, "protein": 25, "carbs": 5, "fat": 3}
    ]
}

def calculate_bmi(weight_kg: float, height_cm: float) -> dict:
    if weight_kg <= 0 or height_cm <= 0:
        raise ValueError("Weight and height must be positive numbers.")
    
    height_m = height_cm / 100.0
    bmi = round(weight_kg / (height_m ** 2), 2)
    
    if bmi < 18.5:
        classification = "Underweight"
    elif 18.5 <= bmi < 25.0:
        classification = "Normal"
    elif 25.0 <= bmi < 30.0:
        classification = "Overweight"
    else:
        classification = "Obese"
        
    return {"bmi": bmi, "classification": classification}

def calculate_bmr(weight_kg: float, height_cm: float, age: int, gender: str) -> float:
    if weight_kg <= 0 or height_cm <= 0 or age <= 0:
        raise ValueError("Weight, height, and age must be positive values.")
    
    gender_norm = gender.strip().lower()
    if gender_norm in ["male", "m"]:
        bmr = (10.0 * weight_kg) + (6.25 * height_cm) - (5.0 * age) + 5.0
    elif gender_norm in ["female", "f"]:
        bmr = (10.0 * weight_kg) + (6.25 * height_cm) - (5.0 * age) - 161.0
    else:
        raise ValueError("Gender must be 'male' or 'female'.")
        
    return round(bmr, 2)

def calculate_tdee(bmr: float, activity_level: str) -> float:
    norm_level = activity_level.strip().lower()
    if norm_level not in ACTIVITY_MULTIPLIERS:
        norm_level = "sedentary"
    multiplier = ACTIVITY_MULTIPLIERS[norm_level]
    return round(bmr * multiplier, 2)

def calculate_target_calories(tdee: float, goal: str) -> float:
    norm_goal = goal.strip().lower()
    if norm_goal in ["weight_loss", "fat_loss", "cut"]:
        target = max(1200.0, tdee - 500.0)
    elif norm_goal in ["muscle_gain", "bulk", "gain"]:
        target = tdee + 400.0
    else:
        target = tdee
    return round(target, 2)

def calculate_macros(target_calories: float, diet_type: str = "balanced") -> dict:
    norm_diet = diet_type.strip().lower()
    ratios = DIET_MACRO_RATIOS.get(norm_diet, DIET_MACRO_RATIOS["balanced"])
    
    protein_cals = target_calories * ratios["protein"]
    carbs_cals = target_calories * ratios["carbs"]
    fat_cals = target_calories * ratios["fat"]
    
    protein_g = round(protein_cals / 4.0, 1)
    carbs_g = round(carbs_cals / 4.0, 1)
    fat_g = round(fat_cals / 9.0, 1)
    
    return {
        "diet_type": norm_diet,
        "protein_g": protein_g,
        "carbs_g": carbs_g,
        "fat_g": fat_g,
        "protein_calories": round(protein_cals, 1),
        "carbs_calories": round(carbs_cals, 1),
        "fat_calories": round(fat_cals, 1),
        "percentage": {
            "protein": int(ratios["protein"] * 100),
            "carbs": int(ratios["carbs"] * 100),
            "fat": int(ratios["fat"] * 100)
        }
    }

def calculate_water_intake(weight_kg: float) -> float:
    if weight_kg <= 0:
        return 2.5
    return round(weight_kg * 0.035, 2)

def generate_meal_plan(target_calories: float, diet_type: str = "balanced") -> dict:
    diet_key = diet_type.strip().lower()
    idx = 2 if diet_key == "keto" else (1 if diet_key in ["low_carb", "high_protein"] else 0)
    
    breakfast = SAMPLE_FOODS["breakfast"][idx % len(SAMPLE_FOODS["breakfast"])]
    lunch = SAMPLE_FOODS["lunch"][idx % len(SAMPLE_FOODS["lunch"])]
    dinner = SAMPLE_FOODS["dinner"][idx % len(SAMPLE_FOODS["dinner"])]
    snack = SAMPLE_FOODS["snack"][idx % len(SAMPLE_FOODS["snack"])]
    
    base_meals = [breakfast, lunch, dinner, snack]
    sum_cals = sum(m["calories"] for m in base_meals)
    ratio = target_calories / max(sum_cals, 1.0)
    
    scaled_meals = []
    meal_names = ["Breakfast", "Lunch", "Dinner", "Snack"]
    for label, meal in zip(meal_names, base_meals):
        scaled_meals.append({
            "meal": label,
            "item": meal["name"],
            "calories": round(meal["calories"] * ratio),
            "protein_g": round(meal["protein"] * ratio, 1),
            "carbs_g": round(meal["carbs"] * ratio, 1),
            "fat_g": round(meal["fat"] * ratio, 1)
        })
        
    total_cals = sum(m["calories"] for m in scaled_meals)
    total_p = sum(m["protein_g"] for m in scaled_meals)
    total_c = sum(m["carbs_g"] for m in scaled_meals)
    total_f = sum(m["fat_g"] for m in scaled_meals)
    
    return {
        "target_calories": target_calories,
        "actual_calories": total_cals,
        "total_protein_g": round(total_p, 1),
        "total_carbs_g": round(total_c, 1),
        "total_fat_g": round(total_f, 1),
        "meals": scaled_meals
    }
