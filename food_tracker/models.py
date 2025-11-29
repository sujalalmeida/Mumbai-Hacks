from django.db import models
from django.utils import timezone
from datetime import timedelta

# Create your models here.

class FoodEntry(models.Model):
    image = models.ImageField(upload_to='food_images/')
    food_name = models.CharField(max_length=255, default="Food Item")
    calories = models.FloatField()
    fats = models.FloatField()
    proteins = models.FloatField()
    carbs = models.FloatField(default=0)
    fiber = models.FloatField(default=0)
    sugar = models.FloatField(default=0)
    meal_type = models.CharField(max_length=50, default="Other", choices=[
        ("Breakfast", "Breakfast"),
        ("Lunch", "Lunch"),
        ("Dinner", "Dinner"),
        ("Snack", "Snack"),
        ("Other", "Other")
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.food_name} - {self.created_at}"

class FridgeImage(models.Model):
    """Model to store the image of the fridge"""
    image = models.ImageField(upload_to='fridge_images/')
    upload_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Fridge Image - {self.upload_date}"

class FridgeItem(models.Model):
    """Model to store items in the fridge"""
    name = models.CharField(max_length=255)
    quantity = models.FloatField(default=1.0)
    unit = models.CharField(max_length=50, default="item")
    added_date = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateField(null=True, blank=True)
    image = models.ForeignKey(FridgeImage, on_delete=models.SET_NULL, null=True, blank=True, related_name='detected_items')
    
    def __str__(self):
        return f"{self.name} - Expires: {self.expiry_date}"
    
    @property
    def days_until_expiry(self):
        """Calculate days until expiry"""
        if not self.expiry_date:
            return None
        
        days = (self.expiry_date - timezone.now().date()).days
        return days
    
    @property
    def days_since_expiry(self):
        """Calculate positive days since expiry for expired items"""
        if not self.expiry_date:
            return None
        
        days = (self.expiry_date - timezone.now().date()).days
        return abs(days) if days < 0 else 0
    
    @property
    def is_expiring_soon(self):
        """Check if item is expiring in the next 3 days"""
        days = self.days_until_expiry
        return days is not None and days <= 3 and days >= 0
    
    @property
    def is_expired(self):
        """Check if item is expired"""
        days = self.days_until_expiry
        return days is not None and days < 0

class Recipe(models.Model):
    """Model to store recipes"""
    title = models.CharField(max_length=255)
    ingredients = models.TextField()
    instructions = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
