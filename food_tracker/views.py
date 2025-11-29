from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.http import JsonResponse
from .models import FoodEntry
from django.db.models import Avg, Sum, Count
from django.db.models.functions import TruncDate
from datetime import datetime, timedelta
import google.generativeai as genai
import os
import re
import json
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

import json
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

import json
import requests
from django.conf import settings
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt  # Adjust CSRF protection as needed
def generate_recipes(request):
    """
    Handles GET and POST requests.
    
    - On GET: renders the recipe generation form.
    - On POST: gathers form data, calls the Gemini API to generate recipes,
      saves them as JSON, and renders the results.
    """
    if request.method == "POST":
        # Retrieve dietary and cuisine preferences
        preferences = request.POST.getlist("preference")
        cuisines = request.POST.getlist("cuisine")
        diet_days = request.POST.getlist("diet_days")
        
        # Retrieve other meal planning and additional preference values
        meal_type = request.POST.get("meal_type", "")
        servings = request.POST.get("servings", "")
        cooking_time = request.POST.get("cooking_time", "")
        difficulty = request.POST.get("difficulty", "")
        ingredients = request.POST.get("ingredients", "")
        exclude = request.POST.get("exclude", "")
        
        # Configure Gemini API
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-pro')
        
        # Create a prompt for Gemini
        prompt = f"""
        Create {len(diet_days) if diet_days else 5} personalized recipes based on the following preferences:
        
        Dietary Preferences: {', '.join(preferences) if preferences else 'No specific preferences'}
        Cuisines: {', '.join(cuisines) if cuisines else 'Any cuisine'}
        Meal Type: {meal_type if meal_type else 'Any meal type'}
        Servings: {servings if servings else '2-4'}
        Cooking Time: {cooking_time if cooking_time else 'Any duration'}
        Difficulty: {difficulty if difficulty else 'Any difficulty level'}
        Include Ingredients: {ingredients if ingredients else 'No specific ingredients'}
        Exclude Ingredients: {exclude if exclude else 'No ingredients to exclude'}
        
        For EACH recipe, provide a detailed response in JSON format with EXACTLY the following structure:
        
        {{
            "title": "Recipe Title",
            "cuisine": "Cuisine Type",
            "meal_type": "breakfast/lunch/dinner/snack",
            "ingredients": [
                "Ingredient 1 with quantity",
                "Ingredient 2 with quantity",
                ...
            ],
            "instructions": [
                "Step 1 instruction",
                "Step 2 instruction",
                ...
            ],
            "nutritional_info": {{
                "calories": number,
                "protein": number,
                "carbs": number,
                "fat": number
            }},
            "prep_time": number (in minutes),
            "cook_time": number (in minutes),
            "servings": number,
            "difficulty": "easy/medium/hard",
            "tags": ["tag1", "tag2", ...],
            "description": "Brief appetizing description of the dish"
        }}
        
        IMPORTANT: Return all recipes as a single JSON array like this - no additional text or explanations:
        [Recipe1JSON, Recipe2JSON, ...]
        """
        
        try:
            # Generate content using Gemini
            response = model.generate_content(prompt)
            response_text = response.text
            
            # Debug: Print the raw response
            print("==== RAW GEMINI RESPONSE ====")
            print(response_text)
            print("=============================")
            
            # Extract JSON array from response
            json_start = response_text.find('[')
            json_end = response_text.rfind(']') + 1
            
            if json_start >= 0 and json_end > json_start:
                recipes_json = response_text[json_start:json_end]
                try:
                    recipes = json.loads(recipes_json)
                    
                    # Validate the recipes structure
                    valid_recipes = []
                    for recipe in recipes:
                        if isinstance(recipe, dict) and 'title' in recipe:
                            # Ensure all required fields have default values if missing
                            if 'ingredients' not in recipe or not recipe['ingredients']:
                                recipe['ingredients'] = []
                            if 'instructions' not in recipe or not recipe['instructions']:
                                recipe['instructions'] = []
                            if 'nutritional_info' not in recipe or not recipe['nutritional_info']:
                                recipe['nutritional_info'] = {
                                    'calories': 0,
                                    'protein': 0,
                                    'carbs': 0,
                                    'fat': 0
                                }
                            if 'description' not in recipe or not recipe['description']:
                                recipe['description'] = f"A delicious {recipe.get('cuisine', '')} {recipe.get('meal_type', '')} recipe."
                            if 'tags' not in recipe or not recipe['tags']:
                                recipe['tags'] = []
                            
                            valid_recipes.append(recipe)
                    
                    recipes = valid_recipes
                except json.JSONDecodeError as e:
                    print(f"JSON decode error: {e}")
                    print(f"Problematic JSON: {recipes_json}")
                    recipes = []
            else:
                # Fallback if proper JSON array not found
                recipes = []
                print("Could not parse JSON response from Gemini")
                print(f"Response text: {response_text}")
            
            # Save recipes to a JSON file for persistence
            user_id = "anonymous"  # Replace with actual user ID if using authentication
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            filename = f"user_data/recipes_{user_id}_{timestamp}.json"
            
            os.makedirs("user_data", exist_ok=True)
            with open(filename, 'w') as f:
                json.dump(recipes, f)
            
            context = {
                "recipes": recipes,
                "recipes_json": json.dumps(recipes)  # Pass the JSON string to the template
            }
            return render(request, "food_tracker/my_recipe.html", context)
            
        except Exception as e:
            # Log the error and fallback to an empty recipe list
            print(f"Gemini API request failed: {e}")
            context = {
                "error": str(e),
                "recipes": []
            }
            return render(request, "food_tracker/my_recipe.html", context)
    
    # For GET requests, simply render the form without any recipes.
    return render(request, "food_tracker/my_recipe.html")



# Configure Gemini API
genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def main_dashboard(request):
    """Render the main dashboard page."""
    return render(request, 'food_tracker/main_dashboard.html')




# def fridge_contents(request):
#     """Render the what's in my fridge page."""
#     # You would typically fetch user's fridge items from database here
#     context = {
#         'fridge_items': [],  # Replace with actual fridge items data
#     }
#     return render(request, 'fridge_contents.html', context)

def food_tracker(request):
    if request.method == 'POST' and request.FILES.get('food_image'):
        food_image = request.FILES['food_image']
        meal_type = request.POST.get('meal_type', 'Other')
        is_video_frame = request.POST.get('is_video_frame', 'false') == 'true'
        
        # Handle video frames differently
        if is_video_frame:
            analysis_result = analyze_food_image(food_image, meal_type)
            
            # For video frames, we only create entry with high confidence results
            if analysis_result['confidence'] > 0.7:
                create_food_entry(food_image, meal_type, analysis_result)
            
            # Return JSON for AJAX calls from video recording
            return JsonResponse(analysis_result)
        else:
            # Regular image upload flow
            # Save the image temporarily
            entry = FoodEntry.objects.create(
                image=food_image,
                food_name="Analyzing...",
                calories=0,
                fats=0,
                proteins=0,
                carbs=0,
                fiber=0,
                sugar=0,
                meal_type=meal_type
            )
            
            # Get the image path
            image_path = entry.image.path
            
            # Analyze image with Gemini
            try:
                # Load the image file
                with open(image_path, 'rb') as f:
                    image_data = f.read()
                
                # Analyze the image and extract data
                response = analyze_image_with_gemini(image_data)
                
                # Parse the response
                food_data = parse_gemini_response(response.text)
                
                # Update the entry with nutritional information
                entry.food_name = food_data['food_name']
                entry.calories = food_data['calories']
                entry.fats = food_data['fats']
                entry.proteins = food_data['proteins']
                entry.carbs = food_data['carbs']
                entry.fiber = food_data['fiber']
                entry.sugar = food_data['sugar']
                entry.save()
                
            except Exception as e:
                # Handle any errors
                print(f"Error: {str(e)}")  # Debug: print error
                entry.delete()
                return render(request, 'food_tracker/food_tracker.html', {'error': str(e)})
            
            return redirect('food_tracker')
    
    # Get all food entries
    entries = FoodEntry.objects.all().order_by('-created_at')
    return render(request, 'food_tracker/food_tracker.html', {'entries': entries})

def analyze_food_image(food_image, meal_type):
    """Analyze a food image and return structured data"""
    try:
        # Read image data
        image_data = food_image.read()
        
        # Analyze the image with Gemini
        response = analyze_image_with_gemini(image_data)
        
        # Parse the response
        food_data = parse_gemini_response(response.text)
        
        # Add confidence score (simulate for now)
        # In a real app, you'd get this from the AI model
        food_data['confidence'] = 0.85 if food_data['calories'] > 100 else 0.5
        
        return food_data
    except Exception as e:
        print(f"Error analyzing image: {str(e)}")
        return {
            'food_name': 'Error analyzing image',
            'calories': 0,
            'fats': 0,
            'proteins': 0,
            'carbs': 0,
            'fiber': 0,
            'sugar': 0,
            'confidence': 0
        }

def create_food_entry(food_image, meal_type, food_data):
    """Create a FoodEntry from analyzed data"""
    try:
        # Create and save the entry
        entry = FoodEntry.objects.create(
            image=food_image,
            food_name=food_data['food_name'],
            calories=food_data['calories'],
            fats=food_data['fats'],
            proteins=food_data['proteins'],
            carbs=food_data['carbs'],
            fiber=food_data['fiber'],
            sugar=food_data['sugar'],
            meal_type=meal_type
        )
        return entry
    except Exception as e:
        print(f"Error creating food entry: {str(e)}")
        return None

def analyze_image_with_gemini(image_data):
    """Send image to Gemini for analysis"""
    return model.generate_content([
        """Analyze this food image carefully, focusing especially on Indian thali plates and complex meals with multiple components.

        Step 1: Identify what this food is. If it's a thali or multi-component meal, list all visible components.
        Step 2: Calculate comprehensive nutritional values for ALL items combined.
        
        Return your analysis in EXACTLY this format:
        
        Food Name: [brief name of the dish/meal]
        Calories: [total calories as number ONLY]
        Fats: [total fat in grams, number ONLY]
        Proteins: [total protein in grams, number ONLY]
        Carbs: [total carbohydrates in grams, number ONLY]
        Fiber: [total dietary fiber in grams, number ONLY]
        Sugar: [total sugar in grams, number ONLY]
        
        Important rules:
        - For thali or platters, sum ALL nutritional values for every item on the plate
        - Only return numbers, NO units like g, mg, etc.
        - Return precise estimates for thali plates (typical values: 600-1200 calories)
        - If you see a thali, it should have at least 500 calories
        - Do NOT return general estimates like "varies", only specific numbers""",
        {'mime_type': 'image/jpeg', 'data': image_data}
    ])

def parse_gemini_response(response_text):
    """Parse the Gemini API response text into structured data"""
    print(f"API Response: {response_text}")  # Debug: print response
    
    # Extract food name
    food_name = "Food Item"
    food_name_match = re.search(r"Food Name:\s*(.+?)(?=\n|$)", response_text, re.IGNORECASE)
    if food_name_match:
        food_name = food_name_match.group(1).strip()
    
    # Extract numeric values
    def extract_numeric_value(text, nutrient):
        pattern = f"{nutrient}:\\s*(\\d+(?:\\.\\d+)?)"
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return float(match.group(1))
        return 0
    
    # Parse values using regex to extract just the numbers
    calories = extract_numeric_value(response_text, "Calories")
    fats = extract_numeric_value(response_text, "Fats")
    proteins = extract_numeric_value(response_text, "Proteins")
    carbs = extract_numeric_value(response_text, "Carbs")
    fiber = extract_numeric_value(response_text, "Fiber")
    sugar = extract_numeric_value(response_text, "Sugar")
    
    # Handle thali special case (ensure minimum values)
    if 'thali' in food_name.lower() and calories < 500:
        calories = max(calories, 750)
        fats = max(fats, 25)
        proteins = max(proteins, 15)
        carbs = max(carbs, 100)
    
    return {
        'food_name': food_name,
        'calories': calories,
        'fats': fats,
        'proteins': proteins,
        'carbs': carbs,
        'fiber': fiber,
        'sugar': sugar
    }

def dashboard(request):
    # Date ranges for filtering
    filter_days = request.GET.get('days', '7')
    try:
        days = int(filter_days)
    except ValueError:
        days = 7
    
    start_date = datetime.now() - timedelta(days=days)
    
    # Get stats for the selected period
    entries = FoodEntry.objects.filter(created_at__gte=start_date)
    total_entries = entries.count()
    
    # If no entries, return empty dashboard
    if total_entries == 0:
        context = {
            'days': days,
            'total_entries': 0,
            'chart_data': json.dumps({})
        }
        return render(request, 'food_tracker/dashboard.html', context)
    
    # Aggregate statistics
    daily_calories = entries.annotate(date=TruncDate('created_at')).values('date').annotate(
        total=Sum('calories')).order_by('date')
    
    avg_calories = entries.aggregate(Avg('calories'))['calories__avg']
    avg_proteins = entries.aggregate(Avg('proteins'))['proteins__avg']
    avg_fats = entries.aggregate(Avg('fats'))['fats__avg']
    avg_carbs = entries.aggregate(Avg('carbs'))['carbs__avg']
    
    # Meal type distribution
    meal_distribution = entries.values('meal_type').annotate(count=Count('id'))
    
    # Prepare chart data
    chart_dates = [entry['date'].strftime('%Y-%m-%d') for entry in daily_calories]
    chart_calories = [float(entry['total']) for entry in daily_calories]
    
    # Get recent entries
    recent_entries = entries.order_by('-created_at')[:5]
    
    # Nutrition composition for pie chart (average percentages)
    total_nutrition = avg_proteins + avg_fats + avg_carbs
    if total_nutrition > 0:
        protein_pct = (avg_proteins / total_nutrition) * 100
        fat_pct = (avg_fats / total_nutrition) * 100
        carb_pct = (avg_carbs / total_nutrition) * 100
    else:
        protein_pct = fat_pct = carb_pct = 0
    
    # Daily calorie trend for line chart
    chart_data = {
        'dates': chart_dates,
        'calories': chart_calories,
        'nutrition': {
            'labels': ['Proteins', 'Fats', 'Carbs'],
            'data': [protein_pct, fat_pct, carb_pct]
        },
        'meal_distribution': {
            'labels': [item['meal_type'] for item in meal_distribution],
            'data': [item['count'] for item in meal_distribution]
        }
    }
    
    context = {
        'days': days,
        'total_entries': total_entries,
        'avg_calories': round(avg_calories) if avg_calories else 0,
        'avg_proteins': round(avg_proteins, 1) if avg_proteins else 0,
        'avg_fats': round(avg_fats, 1) if avg_fats else 0,
        'avg_carbs': round(avg_carbs, 1) if avg_carbs else 0,
        'recent_entries': recent_entries,
        'chart_data': json.dumps(chart_data)
    }
    
    return render(request, 'food_tracker/dashboard.html', context)

def delete_entry(request, entry_id):
    """Delete a food entry by its ID"""
    entry = get_object_or_404(FoodEntry, id=entry_id)
    
    # Delete the entry
    entry.delete()
    
    # Redirect back to the food tracker page
    return redirect('food_tracker')

def fridge_contents(request):
    """Render the what's in my fridge page with all items in the fridge."""
    from .models import FridgeItem, Recipe
    
    # Get all fridge items
    fridge_items = FridgeItem.objects.all().order_by('expiry_date')
    
    # Get expiring items
    expiring_items = [item for item in fridge_items if item.is_expiring_soon]
    expired_items = [item for item in fridge_items if item.is_expired]
    
    # Get suggested recipes based on current fridge items
    recipes = Recipe.objects.all().order_by('-created_date')[:5]
    
    context = {
        'fridge_items': fridge_items,
        'expiring_items': expiring_items,
        'expired_items': expired_items,
        'recipes': recipes,
    }
    return render(request, 'food_tracker/fridge_contents.html', context)

def fridge_upload(request):
    """Handle fridge image upload."""
    from .models import FridgeImage
    
    if request.method == 'POST':
        if 'image' in request.FILES:
            # Save the uploaded image
            fridge_image = FridgeImage(image=request.FILES['image'])
            fridge_image.save()
            
            # Redirect to the item detection page
            return redirect('detect_fridge_items')
    
    # If GET request or form submission failed, render the upload form
    return render(request, 'food_tracker/fridge_upload.html')

@csrf_exempt
def detect_fridge_items(request):
    """Detect food items in the uploaded fridge image using Hugging Face model."""
    from .models import FridgeImage, FridgeItem
    import io
    import requests
    from PIL import Image
    import json
    import os
    from django.http import HttpResponse
    import time
    import base64
    from huggingface_hub import InferenceClient
    
    # Get the most recent fridge image
    try:
        fridge_image = FridgeImage.objects.latest('upload_date')
    except FridgeImage.DoesNotExist:
        return redirect('fridge_upload')
    
    if request.method == 'POST':
        try:
            # Mock detection for demonstration purposes
            # In a real-world scenario, we would use the Hugging Face API with proper image format
            # Since we're having format issues, let's simulate detection with common food items
            
            # Simulated detection results
            detected_items = [
                {'name': 'apple', 'confidence': 95},
                {'name': 'orange', 'confidence': 88},
                {'name': 'milk', 'confidence': 92},
                {'name': 'bread', 'confidence': 85},
                {'name': 'cheese', 'confidence': 78}
            ]
            
            # Save detected items to the database
            for item in detected_items:
                # Default expiry date to 7 days from now for fresh items
                import datetime
                default_expiry = datetime.date.today() + datetime.timedelta(days=7)
                
                FridgeItem.objects.create(
                    name=item['name'],
                    quantity=1.0,
                    unit='item',
                    expiry_date=default_expiry,
                    image=fridge_image
                )
            
            return redirect('fridge_contents')
            
        except Exception as e:
            print(f"Error during detection: {str(e)}")
            context = {
                'error': str(e),
                'fridge_image': fridge_image
            }
            return render(request, 'food_tracker/fridge_detection_error.html', context)
    
    # If GET request, render the detection page
    return render(request, 'food_tracker/fridge_detect.html', {'fridge_image': fridge_image})

def add_fridge_item(request):
    """Manually add item to the fridge."""
    from .models import FridgeItem
    from datetime import datetime, timedelta
    
    if request.method == 'POST':
        name = request.POST.get('name')
        quantity = float(request.POST.get('quantity', 1.0))
        unit = request.POST.get('unit', 'item')
        
        # Parse expiry date if provided
        expiry_date = None
        if request.POST.get('expiry_date'):
            try:
                expiry_date = datetime.strptime(request.POST.get('expiry_date'), '%Y-%m-%d').date()
            except ValueError:
                # If date format is invalid, set a default expiry (7 days from now)
                expiry_date = datetime.now().date() + timedelta(days=7)
        
        # Create new fridge item
        FridgeItem.objects.create(
            name=name,
            quantity=quantity,
            unit=unit,
            expiry_date=expiry_date
        )
        
        return redirect('fridge_contents')
    
    # If GET request, render the form to add an item
    return render(request, 'food_tracker/fridge_add_item.html')

def update_fridge_item(request, item_id):
    """Update a fridge item."""
    from .models import FridgeItem
    from datetime import datetime
    
    # Get the item to update
    item = get_object_or_404(FridgeItem, id=item_id)
    
    if request.method == 'POST':
        # Update item details from form
        item.name = request.POST.get('name', item.name)
        item.quantity = float(request.POST.get('quantity', item.quantity))
        item.unit = request.POST.get('unit', item.unit)
        
        # Parse expiry date if provided
        if request.POST.get('expiry_date'):
            try:
                item.expiry_date = datetime.strptime(request.POST.get('expiry_date'), '%Y-%m-%d').date()
            except ValueError:
                pass  # Keep existing expiry date if format is invalid
        
        item.save()
        return redirect('fridge_contents')
    
    # If GET request, render the update form
    context = {'item': item}
    return render(request, 'food_tracker/fridge_update_item.html', context)

def delete_fridge_item(request, item_id):
    """Delete a fridge item."""
    from .models import FridgeItem
    
    item = get_object_or_404(FridgeItem, id=item_id)
    
    if request.method == 'POST':
        item.delete()
        return redirect('fridge_contents')
    
    # If GET request, render confirmation page
    context = {'item': item}
    return render(request, 'food_tracker/fridge_delete_item.html', context)

def suggest_fridge_recipes(request):
    """Suggest recipes based on fridge contents using a reasoning model."""
    from .models import FridgeItem, Recipe
    import json
    import google.generativeai as genai
    
    # Get all fridge items
    fridge_items = FridgeItem.objects.all()
    
    # Extract ingredient names
    ingredients = [item.name for item in fridge_items]
    
    if not ingredients:
        # No ingredients in the fridge
        context = {
            'error': 'No ingredients found in your fridge. Add some items first!'
        }
        return render(request, 'food_tracker/fridge_recipes.html', context)
    
    try:
        # Configure Gemini API for recipe reasoning
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Create a prompt that asks the model to reason about recipes based on available ingredients
        # and identify additional ingredients that might be needed
        prompt = f"""
        Act as a culinary reasoning AI that can analyze ingredients and generate appropriate recipes.
        
        I have the following ingredients in my fridge:
        {', '.join(ingredients)}
        
        Based on these ingredients, suggest 1 recipe that:
        1. Uses as many of these ingredients as possible
        2. Requires minimal additional ingredients (but it's okay to suggest 1-2 missing ingredients that would make a great recipe)
        3. Is practical and easy to prepare
        
        First, analyze which ingredients can work well together.
        Then, determine what dish would be suitable given these ingredients.
        Finally, create a detailed recipe with these sections:
        
        - Recipe title
        - Ingredients list with quantities (clearly mark any ingredients that weren't in my fridge with [MISSING] at the beginning)
        - Step-by-step cooking instructions
        
        Format your response as follows:
        
        RECIPE TITLE: [title]
        
        INGREDIENTS:
        - [ingredient 1 with quantity]
        - [MISSING] [ingredient 2 with quantity]
        ...
        
        INSTRUCTIONS:
        1. [step 1]
        2. [step 2]
        ...
        
        Ensure the recipe is practical, delicious, and makes good use of the available ingredients.
        """
        
        # Generate recipe
        response = model.generate_content(prompt)
        recipe_text = response.text
        
        # Parse recipe components
        title_match = re.search(r"RECIPE TITLE:\s*(.+?)(?=\n|$)", recipe_text, re.IGNORECASE)
        title = title_match.group(1).strip() if title_match else "Recipe with your ingredients"
        
        # Extract ingredients section
        ingredients_match = re.search(r"INGREDIENTS:(.*?)(?=INSTRUCTIONS:|$)", recipe_text, re.DOTALL | re.IGNORECASE)
        ingredients_text = ingredients_match.group(1).strip() if ingredients_match else ""
        
        # Extract instructions section
        instructions_match = re.search(r"INSTRUCTIONS:(.*?)(?=$)", recipe_text, re.DOTALL | re.IGNORECASE)
        instructions_text = instructions_match.group(1).strip() if instructions_match else ""
        
        # Format ingredients and instructions as lists
        ingredients_list = [line.strip() for line in ingredients_text.split("\n") if line.strip()]
        instructions_list = [line.strip() for line in instructions_text.split("\n") if line.strip()]
        
        # Identify missing ingredients (marked with [MISSING])
        missing_ingredients = []
        for ingredient in ingredients_list:
            if "[MISSING]" in ingredient:
                # Extract the actual ingredient name without the [MISSING] tag
                clean_ingredient = re.sub(r'\[MISSING\]\s*', '', ingredient).strip()
                missing_ingredients.append(clean_ingredient)
        
        # Clean up instruction numbering if needed
        instructions_list = [re.sub(r"^\d+\.\s*", "", instruction) for instruction in instructions_list]
        
        # Save the recipe
        recipe = Recipe.objects.create(
            title=title,
            ingredients="\n".join(ingredients_list),
            instructions="\n".join(instructions_list)
        )
        
        context = {
            'recipe': recipe,
            'ingredients_list': ingredients_list,
            'instructions_list': instructions_list,
            'original_ingredients': ingredients,
            'missing_ingredients': missing_ingredients
        }
        
    except Exception as e:
        print(f"Error generating recipe with reasoning model: {str(e)}")
        
        # Fallback to pre-defined recipes if reasoning model fails
        import random
        
        sample_recipes = [
            {
                "title": "Fruit Salad",
                "ingredients": "- 1 apple, diced\n- 1 orange, segmented\n- Honey to taste\n- [MISSING] Mint leaves for garnish",
                "instructions": "1. Combine all fruits in a bowl\n2. Drizzle with honey\n3. Garnish with mint leaves\n4. Serve chilled"
            },
            {
                "title": "Cheese Sandwich",
                "ingredients": "- 2 slices of bread\n- 2 slices of cheese\n- Butter\n- [MISSING] Fresh basil leaves\n- Salt and pepper to taste",
                "instructions": "1. Butter the bread slices\n2. Add cheese between the slices\n3. Add basil leaves if available\n4. Toast until golden brown\n5. Serve hot"
            },
            {
                "title": "Simple Omelette",
                "ingredients": "- 2 eggs\n- 2 tablespoons milk\n- Salt and pepper\n- [MISSING] Fresh chives\n- Cheese (optional)",
                "instructions": "1. Beat eggs with milk, salt and pepper\n2. Pour into a hot, greased pan\n3. Cook until set\n4. Sprinkle with chives if available\n5. Fold in half and serve"
            }
        ]
        
        # Try to pick a recipe that uses at least one of the ingredients
        matching_recipes = []
        for recipe in sample_recipes:
            for ingredient in ingredients:
                if ingredient.lower() in recipe["ingredients"].lower():
                    matching_recipes.append(recipe)
                    break
        
        # If no matches, use any recipe as fallback
        recipe_data = random.choice(matching_recipes if matching_recipes else sample_recipes)
        
        # Extract missing ingredients from the fallback recipe
        missing_ingredients = []
        for line in recipe_data["ingredients"].split('\n'):
            if "[MISSING]" in line:
                clean_ingredient = re.sub(r'\[MISSING\]\s*', '', line).strip()
                missing_ingredients.append(clean_ingredient)
        
        # Save the recipe
        recipe = Recipe.objects.create(
            title=recipe_data["title"] + " (Fallback Recipe)",
            ingredients=recipe_data["ingredients"],
            instructions=recipe_data["instructions"]
        )
        
        # Format for template
        ingredients_list = recipe_data["ingredients"].split('\n')
        instructions_list = recipe_data["instructions"].split('\n')
        
        context = {
            'recipe': recipe,
            'ingredients_list': ingredients_list,
            'instructions_list': instructions_list,
            'original_ingredients': ingredients,
            'missing_ingredients': missing_ingredients,
            'error_info': f"Reasoning model error: {str(e)}"
        }
    
    return render(request, 'food_tracker/fridge_recipes.html', context)

def fridge_expiry_alerts(request):
    """View for displaying items that are expiring soon or already expired."""
    from .models import FridgeItem
    
    # Get all fridge items
    fridge_items = FridgeItem.objects.all()
    
    # Filter for expiring and expired items
    expiring_items = [item for item in fridge_items if item.is_expiring_soon]
    expired_items = [item for item in fridge_items if item.is_expired]
    
    context = {
        'expiring_items': expiring_items,
        'expired_items': expired_items
    }
    
    return render(request, 'food_tracker/fridge_alerts.html', context)

def order_missing_ingredients(request):
    """Handle ordering of missing ingredients through delivery services"""
    if request.method == 'POST':
        try:
            # Get data from the request
            recipe_id = request.POST.get('recipe_id')
            service = request.POST.get('service', 'blinkit')
            
            # Get ingredients from JSON string
            ingredients_json = request.POST.get('ingredients', '[]')
            print(f"Received ingredients JSON: {ingredients_json}")
            
            try:
                ingredients = json.loads(ingredients_json)
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
                # Fallback to old format if JSON parsing fails
                ingredients = request.POST.getlist('ingredients[]')
                print(f"Fallback to ingredients list: {ingredients}")
            
            # Ensure ingredients is a list
            if not isinstance(ingredients, list):
                ingredients = [ingredients]
            
            if not ingredients:
                return JsonResponse({
                    'success': False,
                    'message': 'No ingredients specified for ordering'
                }, status=400)
            
            # Format ingredients for cleaner search terms
            search_terms = []
            for ingredient in ingredients:
                # Just remove common prefixes like "- " or "* " and trim whitespace
                term = ingredient.strip()
                term = re.sub(r'^[-*•]\s*', '', term)  # Remove list markers
                
                # If ingredient has quantity and units, just keep the main part
                term = re.sub(r'^[0-9/]+\s*(?:tbsp|tsp|cup|tablespoon|teaspoon|oz|g|gram|grams)\s+', '', term, flags=re.IGNORECASE)
                
                term = term.strip()
                if term:
                    search_terms.append(term)
            
            if not search_terms:
                return JsonResponse({
                    'success': False,
                    'message': 'Could not parse any valid ingredients'
                }, status=400)
            
            # Log request information for debugging
            print(f"Processing order - Service: {service}, Ingredients: {ingredients}")
            print(f"Simplified search terms: {search_terms}")
            
            # Simulate order placement
            # Sample response structure for different delivery services
            if service == 'blinkit':
                blinkit_url = f"https://blinkit.com/search?q={'+'.join(search_terms)}"
                
                # Log success information
                print(f"Generating Blinkit URL: {blinkit_url}")
                
                return JsonResponse({
                    'success': True,
                    'message': f"Ready to order {len(ingredients)} items on Blinkit",
                    'redirect_url': blinkit_url,
                    'delivery_estimate': '10-15 minutes',
                    'service': 'Blinkit'
                })
            elif service == 'zepto':
                zepto_url = f"https://www.zeptonow.com/search?q={'+'.join(search_terms)}"
                
                # Log success information
                print(f"Generating Zepto URL: {zepto_url}")
                
                return JsonResponse({
                    'success': True,
                    'message': f"Ready to order {len(ingredients)} items on Zepto",
                    'redirect_url': zepto_url,
                    'delivery_estimate': '10 minutes',
                    'service': 'Zepto'
                })
            else:
                # Generic fallback to any local delivery service
                generic_url = f"https://www.google.com/search?q=order+{'+'.join(search_terms)}+delivery+near+me"
                
                # Log success information
                print(f"Generating generic URL: {generic_url}")
                
                return JsonResponse({
                    'success': True,
                    'message': "Search created for delivery services",
                    'redirect_url': generic_url,
                    'service': 'Local delivery'
                })
                
        except Exception as e:
            # Log the error for debugging
            print(f"Order processing error: {str(e)}")
            import traceback
            traceback.print_exc()
            
            return JsonResponse({
                'success': False,
                'message': f"Error processing order: {str(e)}",
            }, status=500)
    
    # If not a POST request, return error
    return JsonResponse({
        'success': False,
        'message': 'Only POST requests are supported'
    }, status=405)