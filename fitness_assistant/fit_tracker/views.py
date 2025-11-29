from django.shortcuts import render
from django.http import JsonResponse
from .models import FitnessData
import json
from django.db.models import Avg, Sum, Count
from django.db.models.functions import TruncDate
from .utils.ai_agent import get_fitness_suggestion


def dashboard(request):
    """
    Main dashboard view showing fitness data charts.
    """
    # Get all fitness data for rendering in the template
    fitness_data = FitnessData.objects.all().order_by('activity_date')
    
    # Get AI-powered fitness suggestion
    suggestion = get_fitness_suggestion()
    
    # Prepare context data
    context = {
        'fitness_data': fitness_data,
        'ai_suggestion': suggestion,
    }
    
    return render(request, 'fit_tracker/dashboard.html', context)


def chart_data(request):
    """
    API endpoint to get chart data in JSON format.
    This can be used for AJAX requests if needed.
    """
    # Get all fitness data ordered by date
    fitness_data = FitnessData.objects.all().order_by('activity_date')
    
    # Format data for charts
    data = {
        'labels': [str(entry.activity_date) for entry in fitness_data],
        'steps': [entry.total_steps for entry in fitness_data],
        'calories': [entry.calories for entry in fitness_data],
    }
    
    return JsonResponse(data)


def chatbot(request):
    """
    API endpoint for the fitness chatbot.
    Handles both automatic suggestions and user questions.
    """
    # If it's a GET request without a user query, render the ai.html template
    if request.method == 'GET' and request.GET.get('user_input') is None:
        return render(request, 'fit_tracker/ai.html')
    
    # Check if there's a user query in the request
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_input = data.get('user_input', None)
        except json.JSONDecodeError:
            user_input = None
    else:
        user_input = request.GET.get('user_input', None)
    
    # Get suggestion from AI agent
    suggestion = get_fitness_suggestion(user_input)
    
    # Return the suggestion as JSON
    return JsonResponse({
        'suggestion': suggestion
    })