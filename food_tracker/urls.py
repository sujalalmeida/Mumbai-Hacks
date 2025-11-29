from django.urls import path
from . import views

urlpatterns = [
    # Main dashboard and sidebar options
    path('nutrition/', views.main_dashboard, name='main_dashboard'),
    path('my_receipes/', views.generate_recipes, name='my_receipes'),
    # path('calorie-detection/', views.calorie_detection, name='calorie_detection'),
    path('fridge/', views.fridge_contents, name='fridge_contents'),
    
    # Food tracker related URLs
    path('food-tracker/', views.food_tracker, name='food_tracker'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('delete-entry/<int:entry_id>/', views.delete_entry, name='delete_entry'),
    
    # Fridge feature related URLs
    path('fridge/upload/', views.fridge_upload, name='fridge_upload'),
    path('fridge/detect-items/', views.detect_fridge_items, name='detect_fridge_items'),
    path('fridge/add-item/', views.add_fridge_item, name='add_fridge_item'),
    path('fridge/update-item/<int:item_id>/', views.update_fridge_item, name='update_fridge_item'),
    path('fridge/delete-item/<int:item_id>/', views.delete_fridge_item, name='delete_fridge_item'),
    path('fridge/suggest-recipes/', views.suggest_fridge_recipes, name='suggest_fridge_recipes'),
    path('fridge/expiry-alerts/', views.fridge_expiry_alerts, name='fridge_expiry_alerts'),
    
    # Delivery service integration
    path('fridge/order-ingredients/', views.order_missing_ingredients, name='order_missing_ingredients'),
]