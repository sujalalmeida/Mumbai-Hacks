import datetime
from typing import Optional, List, Dict, Any
from django.db.models import Avg

from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_community.llms import Ollama

from ..models import FitnessData


def format_fitness_data(fitness_data) -> str:
    """
    Format fitness data into a readable string for the LLM.
    """
    if not fitness_data:
        return "No fitness data available for the last 7 days."
    
    formatted_data = "Here is your fitness data for the last 7 days:\n\n"
    
    for entry in fitness_data:
        formatted_data += (
            f"Date: {entry.activity_date}\n"
            f"Steps: {entry.total_steps} steps\n"
            f"Distance: {entry.total_distance:.2f} km\n"
            f"Very Active Minutes: {entry.very_active_minutes} minutes\n"
            f"Lightly Active Minutes: {entry.lightly_active_minutes} minutes\n"
            f"Calories Burned: {entry.calories} calories\n\n"
        )
    
    return formatted_data


def get_fitness_insights(fitness_data) -> Dict[str, Any]:
    """
    Extract key insights from fitness data.
    """
    if not fitness_data:
        return {
            "has_data": False,
            "message": "No fitness data available for analysis."
        }
    
    # Initialize insights dictionary
    insights = {
        "has_data": True,
        "total_days": len(fitness_data),
        "average_steps": 0,
        "average_calories": 0,
        "total_steps": 0,
        "total_calories": 0,
        "days_below_step_goal": 0,
        "step_goal": 10000,  # Default step goal, can be customized
        "trend": "steady"
    }
    
    # Calculate averages and totals
    insights["total_steps"] = sum(entry.total_steps for entry in fitness_data)
    insights["total_calories"] = sum(entry.calories for entry in fitness_data)
    
    if insights["total_days"] > 0:
        insights["average_steps"] = insights["total_steps"] / insights["total_days"]
        insights["average_calories"] = insights["total_calories"] / insights["total_days"]
        
        # Check if steps are below goal
        insights["days_below_step_goal"] = sum(1 for entry in fitness_data if entry.total_steps < insights["step_goal"])
        
        # Determine trend (if enough data points)
        if insights["total_days"] >= 3:
            # Check if steps are increasing, decreasing, or staying steady
            first_half = fitness_data[:len(fitness_data)//2]
            second_half = fitness_data[len(fitness_data)//2:]
            
            avg_first_half = sum(entry.total_steps for entry in first_half) / len(first_half)
            avg_second_half = sum(entry.total_steps for entry in second_half) / len(second_half)
            
            if avg_second_half > avg_first_half * 1.1:  # 10% increase
                insights["trend"] = "improving"
            elif avg_second_half < avg_first_half * 0.9:  # 10% decrease
                insights["trend"] = "declining"
    
    return insights


def get_fitness_suggestion(user_input: Optional[str] = None) -> str:
    """
    Generate a fitness suggestion based on the user's recent fitness data.
    If user_input is provided, generate a response tailored to the query.
    Otherwise, generate a default suggestion or summary.
    """
    # Get the last 7 days of fitness data
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=7)
    
    fitness_data = list(FitnessData.objects.filter(
        activity_date__gte=start_date,
        activity_date__lte=end_date
    ).order_by('activity_date'))
    
    # If no data available, return a default message
    if not fitness_data:
        return "I don't see any fitness data for the past week. Start tracking your activities to get personalized suggestions!"
    
    # Format the fitness data for the LLM
    formatted_data = format_fitness_data(fitness_data)
    
    # Extract insights from the fitness data
    insights = get_fitness_insights(fitness_data)
    
    # Create LLM instance
    llm = Ollama(model="llama3.2")
    
    # Create different prompts based on whether user input was provided
    if user_input:
        # For user queries, include the query in the prompt
        prompt_template = PromptTemplate(
            input_variables=["fitness_data", "average_steps", "average_calories", "days_below_step_goal", "total_days", "trend", "user_input"],
            template="""
            You are a specialized fitness assistant that analyzes fitness data and provides personalized advice. 
            You ONLY answer questions related to fitness, health, exercise, nutrition, and the user's fitness data.
            
            If the user asks about topics outside fitness and health (like politics, technology unrelated to fitness, entertainment, etc.), 
            ALWAYS respond with: "I'm a specialized fitness assistant. That question is outside my expertise. I'd be happy to help with questions about your fitness data or general fitness advice."
            
            {fitness_data}
            
            Additional insights:
            - Average steps per day: {average_steps:.0f}
            - Average calories burned per day: {average_calories:.0f}
            - Days below step goal (10,000 steps): {days_below_step_goal} out of {total_days}
            - Overall trend: {trend}
            
            The user asks: {user_input}
            
            When responding to fitness-related questions:
            1. Provide a helpful, encouraging, and personalized response based on their fitness data
            2. ALWAYS use clear formatting to make your answers easy to read:
               - Use bullet points (with "-" or "*") for lists of items, exercises, or food options
               - Use numbered lists for steps in a process or routine
               - Use line breaks to separate different sections
               - For meal plans, workout schedules, or any structured information, clearly label each section
            3. Always prioritize factual, science-based information
            4. Include specific, actionable advice when possible
            5. Keep your tone positive and motivational
            
            Remember: 
            - Format complex information in clear lists with bullet points, not paragraphs
            - For meal plans, organize by meal (Breakfast, Lunch, Dinner) with bullet points for foods
            - For workout plans, organize by day or exercise with clear structure
            - If the query is unrelated to fitness or health, respond ONLY with the standard message about being a specialized fitness assistant
            """
        )
        
        chain = LLMChain(llm=llm, prompt=prompt_template)
        response = chain.invoke({
            "fitness_data": formatted_data, 
            "average_steps": insights["average_steps"],
            "average_calories": insights["average_calories"],
            "days_below_step_goal": insights["days_below_step_goal"],
            "total_days": insights["total_days"],
            "trend": insights["trend"],
            "user_input": user_input
        })
    else:
        # For automatic suggestions, use a prompt focused on generating insights and recommendations
        prompt_template = PromptTemplate(
            input_variables=["fitness_data", "average_steps", "average_calories", "days_below_step_goal", "total_days", "trend"],
            template="""
            You are a specialized fitness assistant that analyzes fitness data and provides personalized advice.
            You ONLY discuss topics related to fitness, health, exercise, and nutrition.
            
            {fitness_data}
            
            Additional insights:
            - Average steps per day: {average_steps:.0f}
            - Average calories burned per day: {average_calories:.0f}
            - Days below step goal (10,000 steps): {days_below_step_goal} out of {total_days}
            - Overall trend: {trend}
            
            Based on this data, provide a detailed, personalized fitness insight or suggestion. Be specific, encouraging, and actionable.
            If they're doing well, acknowledge it. If there are areas for improvement, suggest one or two achievable steps they could take.
            
            ALWAYS structure your response with clear formatting:
            - Start with a personalized greeting or observation about their data
            - Use bullet points for any list of suggestions or recommendations
            - Use clear headings if providing multiple types of suggestions (e.g., "Activity Recommendations:" followed by bullet points)
            - End with an encouraging statement
            
            Your response should be well-structured and organized, using up to 4-6 sentences with appropriate line breaks and bullet points.
            Make it conversational yet informative.
            """
        )
        
        chain = LLMChain(llm=llm, prompt=prompt_template)
        response = chain.invoke({
            "fitness_data": formatted_data, 
            "average_steps": insights["average_steps"],
            "average_calories": insights["average_calories"],
            "days_below_step_goal": insights["days_below_step_goal"],
            "total_days": insights["total_days"],
            "trend": insights["trend"]
        })
    
    # Extract the text from the LLMChain response
    suggestion = response.get("text", "").strip()
    
    # If for some reason we get an empty response, provide a fallback
    if not suggestion:
        if insights["trend"] == "improving":
            suggestion = f"Great job! You're averaging {insights['average_steps']:.0f} steps daily and your trend is improving. Keep up the good work!"
        elif insights["trend"] == "declining":
            suggestion = f"Your step count has been decreasing lately, averaging {insights['average_steps']:.0f} steps daily. Try adding a short 10-minute walk to your routine to get back on track."
        else:
            suggestion = f"You've been consistent with an average of {insights['average_steps']:.0f} steps per day. Try to reach 10,000 steps daily for optimal health benefits."
    
    return suggestion 