"""Flask Application for Diet & Nutrition Tips and Calculators."""

from flask import Flask, render_template, request, jsonify
from diet_calculator import (
    calculate_bmi,
    calculate_bmr,
    calculate_tdee,
    calculate_target_calories,
    calculate_macros,
    calculate_water_intake,
    generate_meal_plan,
    TIPS_DATABASE
)

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/api/tips", methods=["GET"])
def get_tips():
    category = request.args.get("category")
    if category and category in TIPS_DATABASE:
        return jsonify({"category": category, "tips": TIPS_DATABASE[category]}), 200
    return jsonify({"tips": TIPS_DATABASE}), 200

@app.route("/api/calculate", methods=["POST"])
def calculate_nutrition():
    data = request.get_json() or {}
    
    try:
        weight = float(data.get("weight", 0))
        height = float(data.get("height", 0))
        age = int(data.get("age", 0))
        gender = str(data.get("gender", "male"))
        activity_level = str(data.get("activity_level", "sedentary"))
        goal = str(data.get("goal", "maintenance"))
        diet_type = str(data.get("diet_type", "balanced"))
        
        if weight <= 0 or height <= 0 or age <= 0:
            return jsonify({"error": "Weight, height, and age must be positive values."}), 400
        
        bmi_info = calculate_bmi(weight, height)
        bmr = calculate_bmr(weight, height, age, gender)
        tdee = calculate_tdee(bmr, activity_level)
        target_calories = calculate_target_calories(tdee, goal)
        macros = calculate_macros(target_calories, diet_type)
        water_intake_l = calculate_water_intake(weight)
        
        tips = TIPS_DATABASE.get(goal, TIPS_DATABASE.get("general_health"))
        
        response_data = {
            "success": True,
            "bmi": bmi_info["bmi"],
            "bmi_classification": bmi_info["classification"],
            "bmr": bmr,
            "tdee": tdee,
            "target_calories": target_calories,
            "water_intake_liters": water_intake_l,
            "macros": macros,
            "recommended_tips": tips
        }
        return jsonify(response_data), 200
    except (ValueError, TypeError) as e:
        return jsonify({"error": f"Invalid input payload: {str(e)}"}), 400

@app.route("/api/meal-plan", methods=["POST"])
def create_meal_plan():
    data = request.get_json() or {}
    try:
        target_calories = float(data.get("calories", 2000))
        diet_type = str(data.get("diet_type", "balanced"))
        if target_calories <= 500:
            return jsonify({"error": "Calorie target must be greater than 500."}), 400
        plan = generate_meal_plan(target_calories, diet_type)
        return jsonify({"success": True, "meal_plan": plan}), 200
    except (ValueError, TypeError) as e:
        return jsonify({"error": f"Invalid input payload: {str(e)}"}), 400

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
