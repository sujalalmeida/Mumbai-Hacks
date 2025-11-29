from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import JsonResponse
from . import views

from .forms import SignUpForm, LoginForm, UserProfileForm, FitnessGoalForm
from .models import (
    UserProfile, FitnessGoal, Lifestyle, Diet, FoodAllergy,
    MedicalInfo, WorkoutPreference, PlanSelection
)

from django.contrib.auth.models import User
from fitness_assistant.fit_tracker.models import FitnessData
from fitness_assistant.fit_tracker.utils.ai_agent import get_fitness_suggestion


def landing_page(request):
    # Get all fitness data for rendering in the template
    fitness_data = FitnessData.objects.all().order_by('activity_date')
    
    # Get AI-powered fitness suggestion
    suggestion = get_fitness_suggestion()
    
    context = {
        "page_title": "Fitness Assistant Landing Page",
        "site_name": "AuraFitness",
        "workouts": ["Strength", "Cardio", "Yoga", "HIIT"],
        "user_count": "2,500+",
        "hero_image": "/static/images/fitness-hero.jpg",
        "stats_range": range(4),
        "fitness_data": fitness_data,
        "ai_suggestion": suggestion,
    }
    return render(request, 'home/landing.html', context)


def signup_view(request):
    form = SignUpForm(request.POST or None)
    if form.is_valid():
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])
        user.save()
        return redirect('login')
    return render(request, 'home/signup.html', {'form': form})


def login_view(request):
    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        return redirect('user_details')
    return render(request, 'home/login.html', {'form': form})


@login_required
def get_started(request):
    return render(request, 'home/landing.html')


@login_required
def challenge_view(request):
    return render(request, 'home/challenge.html')



@login_required
def user_details_view(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            return redirect('show_plan')
    else:
        form = UserProfileForm()
    return render(request, 'home/user_details.html', {'form': form})


@login_required
def set_goal_view(request):
    if request.method == 'POST':
        form = FitnessGoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user
            goal.save()
            return redirect('plans')
    else:
        form = FitnessGoalForm()
    return render(request, 'home/set_goal.html', {'form': form})


@login_required
def plans_view(request):
    profile = UserProfile.objects.filter(user=request.user).order_by('-created_at').first()
    goal = FitnessGoal.objects.filter(user=request.user).order_by('-id').first()

    if not profile or not goal:
        return redirect('onboarding')

    plan = generate_personalized_plan(profile, goal)

    context = {
        'profile': profile,
        'goal': goal,
        'plan': plan,
    }
    return render(request, 'home/plans.html', context)


@login_required
def dashboard_view(request):
    profile = UserProfile.objects.filter(user=request.user).order_by('-created_at').first()
    goal = FitnessGoal.objects.filter(user=request.user).order_by('-id').first()

    if not profile:
        return redirect('user_details')

    diet_plan, exercise_plan = generate_diet_and_exercise(profile, goal)

    context = {
        'user_profile': profile,
        'fitness_goal': goal,
        'diet_plan': diet_plan,
        'exercise_plan': exercise_plan,
    }
    return render(request, 'home/dashboard.html', context)


def generate_personalized_plan(profile, goal_instance=None):
    goal_text = goal_instance.goal_type.lower() if goal_instance and goal_instance.goal_type else ''
    activity = getattr(profile, 'activity_level', '').lower()

    if goal_text == 'weight loss':
        return "Do 30 minutes of cardio daily and follow a low-calorie, high-protein diet."
    elif goal_text == 'gain muscle':
        return "Engage in strength training 4-5 days per week and increase your protein intake."
    elif goal_text == 'flexibility':
        return "Incorporate yoga and stretching routines into your weekly schedule."
    else:
        return "Follow a balanced routine that includes cardio, strength training, and flexibility exercises."


def generate_diet_and_exercise(profile, goal_instance):
    goal_text = goal_instance.goal_type.lower() if goal_instance and goal_instance.goal_type else ''

    if goal_text == 'weight loss':
        return "Low-carb meals with high fiber", "Cardio sessions combined with HIIT workouts"
    elif goal_text == 'gain muscle':
        return "High-protein meals with a slight calorie surplus", "Strength training focusing on compound lifts"
    elif goal_text == 'flexibility':
        return "Anti-inflammatory foods and plenty of water", "Yoga and mobility exercises"
    else:
        return "Balanced diet with a mix of macronutrients", "General fitness routine with cardio and strength training"


@login_required
def onboarding_view(request):
    if request.method == 'POST':
        try:
            user = request.user

            def cv(key):
                val = request.POST.get(key)
                return val or None

            # only create new entries (don't use update_or_create if multiple allowed)
            UserProfile.objects.create(
                user=user,
                full_name=cv('full_name'),
                dob=cv('dob'),
                gender=cv('gender'),
                height=cv('height'),
                weight=cv('weight'),
            )

            Lifestyle.objects.create(
                user=user,
                activity_level=cv('activity_level'),
                sleep_quality=cv('sleep_quality'),
                stress_level=cv('stress_level'),
            )

            Diet.objects.create(
                user=user,
                diet_type=cv('diet_type'),
            )

            for allergen in request.POST.getlist('allergen'):
                if allergen:
                    FoodAllergy.objects.create(user=user, allergen=allergen)

            FitnessGoal.objects.create(
                user=user,
                goal_type=cv('goal_type'),
                goal_description=cv('goal_description'),
                target_weight=cv('target_weight'),
                target_date=cv('target_date'),
                experience_level=cv('experience_level'),
            )

            MedicalInfo.objects.create(
                user=user,
                condition_name=cv('condition_name'),
                notes=cv('notes'),
            )

            WorkoutPreference.objects.create(
                user=user,
                workout_style=cv('workout_style'),
                equipment_owned=cv('equipment_owned'),
            )

            PlanSelection.objects.create(
                user=user,
                selected_plan=cv('selected_plan'),
                start_date=cv('start_date'),
            )

            messages.success(request, "Onboarding completed successfully!")
            return redirect('plans')

        except Exception as e:
            messages.error(request, f"Error: {e}")

    return render(request, 'home/onboarding.html')


@login_required
def show_plan_view(request):
    import json
    import os
    import uuid
    import google.generativeai as genai
    from datetime import datetime
    
    # Define the path to save JSON files
    json_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'user_data')
    os.makedirs(json_dir, exist_ok=True)
    
    if request.method == 'POST':
        try:
            # Get the user's data from the form
            user_data = {
                'user_id': request.user.id,
                'username': request.user.username,
                'full_name': request.POST.get('full_name', ''),
                'email': request.POST.get('email', ''),
                'dob': request.POST.get('dob', ''),
                'gender': request.POST.get('gender', ''),
                'height': request.POST.get('height', ''),
                'weight': request.POST.get('weight', ''),
                'submission_date': datetime.now().isoformat()
            }
            
            # Generate a unique filename
            filename = f"{request.user.username}_{uuid.uuid4().hex[:8]}.json"
            filepath = os.path.join(json_dir, filename)
            
            # Save the data to a JSON file
            with open(filepath, 'w') as f:
                json.dump(user_data, f, indent=4)
            
            # Configure Gemini API
            try:
                # Replace with your actual API key - for demo purposes we're using a placeholder
                # IMPORTANT: In production, use environment variables for API keys
                GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY', 'your-api-key')
                genai.configure(api_key=GOOGLE_API_KEY)
                
                # Create a diet and workout plan using Gemini
                model = genai.GenerativeModel('gemini-pro')
                
                prompt = f"""
                Create a personalized diet and workout plan for a user with the following characteristics:
                - Name: {user_data['full_name']}
                - Gender: {user_data['gender']}
                - Height: {user_data['height']} cm
                - Weight: {user_data['weight']} kg
                - Date of Birth: {user_data['dob']}
                
                Please structure your response in the following format:
                1. Brief introduction about the importance of personalized fitness and nutrition plans
                2. A weekly diet plan with meal suggestions (breakfast, lunch, dinner, snacks)
                3. A weekly workout routine with specific exercises
                4. Tips for staying motivated
                
                Keep each section concise and easy to understand for a beginner. Emphasize balance and sustainability.
                """
                
                response = model.generate_content(prompt)
                generated_plan = response.text
                
                # For demonstration, create a structured plan if API key is not available
            except Exception as e:
                print(f"Gemini API error: {e}")
                # Fallback plan if API fails
                generated_plan = f"""
                # Personalized Plan for {user_data['full_name']}
                
                ## Introduction
                A personalized approach to fitness and nutrition is key for sustainable results. This plan is tailored to your specific body measurements and goals.
                
                ## Diet Plan
                
                ### Breakfast
                - Greek yogurt with berries and honey
                - Whole grain toast with avocado
                - Omelette with vegetables
                
                ### Lunch
                - Grilled chicken salad with olive oil dressing
                - Quinoa bowl with roasted vegetables
                - Brown rice with steamed fish and broccoli
                
                ### Dinner
                - Baked salmon with sweet potato
                - Turkey stir-fry with mixed vegetables
                - Lentil soup with a side of green salad
                
                ### Snacks
                - Handful of nuts
                - Apple with peanut butter
                - Protein smoothie
                
                ## Workout Plan
                
                ### Monday: Upper Body
                - Push-ups: 3 sets of 10
                - Dumbbell rows: 3 sets of 12
                - Shoulder press: 3 sets of 10
                
                ### Tuesday: Cardio
                - 30 minutes jogging or brisk walking
                - 10 minutes jumping jacks
                - 10 minutes high knees
                
                ### Wednesday: Rest
                - Light stretching or yoga
                
                ### Thursday: Lower Body
                - Squats: 3 sets of 15
                - Lunges: 3 sets of 10 each leg
                - Calf raises: 3 sets of 20
                
                ### Friday: Full Body
                - Burpees: 3 sets of 10
                - Mountain climbers: 3 sets of 20
                - Plank: 3 sets of 30 seconds
                
                ### Weekend: Active Recovery
                - Light activity like walking, swimming, or cycling
                - Stretching and mobility exercises
                
                ## Motivation Tips
                1. Set small, achievable goals
                2. Track your progress regularly
                3. Find a workout buddy for accountability
                4. Mix up your routine to avoid boredom
                5. Celebrate your accomplishments, no matter how small
                """
            
            context = {
                'user_data': user_data,
                'plan': generated_plan,
                'plan_date': datetime.now().strftime('%B %d, %Y')
            }
            
            messages.success(request, "Your plan has been created successfully!")
            return render(request, 'home/show_plan.html', context)
            
        except Exception as e:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'error': str(e)}, status=400)
            messages.error(request, f"Something went wrong: {e}")

    profile = UserProfile.objects.filter(user=request.user).first()
    goal    = FitnessGoal.objects.filter(user=request.user).first()

    if not profile:
        return redirect('user_details')

    plan = generate_personalized_plan(profile, goal)
    context = {
        'plan': plan,
        'profile': profile,
    }
    return render(request, 'home/show_plan.html', context)

@login_required
def profile_view(request):
    return render(request, 'home/profile.html')
           
@login_required
def profile_view(request):
    return render(request, 'home/profile.html')
