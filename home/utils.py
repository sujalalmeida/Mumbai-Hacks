# home/utils.py

def generate_personalized_plan(user_profile, fitness_goal):
    """
    Generates a personalized diet and exercise plan based on user profile and fitness goal.
    This is a simple rule-based example. You can later replace this with an ML model.
    """
    # Example rule-based logic:
    if fitness_goal.goal_type == "Weight loss":
        diet_plan = (
            "Focus on a low-carb, high-fiber diet. Incorporate lean proteins, "
            "lots of vegetables, and reduce processed sugars."
        )
        exercise_plan = (
            "30 minutes of moderate cardio (e.g., brisk walking or cycling) five days a week, "
            "combined with light strength training."
        )
    elif fitness_goal.goal_type == "Gain muscle":
        diet_plan = (
            "Increase your protein intake with lean meats, legumes, and dairy. "
            "Include complex carbohydrates for energy and healthy fats."
        )
        exercise_plan = (
            "Engage in strength training exercises (e.g., weight lifting) at least four times a week, "
            "with proper rest between sessions."
        )
    elif fitness_goal.goal_type == "Maintain":
        diet_plan = (
            "Follow a balanced diet with moderate portions of all food groups. "
            "Focus on variety and nutrient density."
        )
        exercise_plan = (
            "Incorporate a mix of cardio and strength training for overall fitness, about 3-4 days a week."
        )
    elif fitness_goal.goal_type == "Tone body":
        diet_plan = (
            "Opt for a balanced diet with a slight calorie deficit. "
            "Focus on high-fiber foods, lean proteins, and minimal processed foods."
        )
        exercise_plan = (
            "Combine strength training with cardio, focusing on high repetitions and moderate weights to enhance muscle tone."
        )
    else:
        # Default fallback plan
        diet_plan = "Follow a balanced, nutrient-rich diet."
        exercise_plan = "Engage in regular exercise with a mix of cardio and strength training."

    return diet_plan, exercise_plan
