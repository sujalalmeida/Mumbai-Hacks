from django.db import models
from django.contrib.auth.models import User


class SafeDecimalField(models.FloatField):
    def __init__(self, *args, decimal_places=None, max_digits=None, validators=None, **kwargs):
        super().__init__(*args, **kwargs)


class UserProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    full_name = models.CharField(max_length=100, null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, null=True, blank=True)
    height = models.FloatField(null=True, blank=True)
    weight = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.full_name or f"{self.user.username}'s Profile" if self.user else "Unnamed Profile"


class Lifestyle(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    activity_level = models.CharField(max_length=100, null=True, blank=True)
    sleep_quality = models.CharField(max_length=50, null=True, blank=True)
    stress_level = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} — Lifestyle" if self.user else "Lifestyle"


class Diet(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    diet_type = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} — {self.diet_type}" if self.user else "Diet"


class FoodAllergy(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    allergen = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} — {self.allergen}" if self.user else "Food Allergy"


class FitnessGoal(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    goal_name = models.CharField(max_length=100, default='My Goal', null=True, blank=True)
    target_weight = models.FloatField(null=True, blank=True)
    target_date = models.DateField(null=True, blank=True)
    experience_level = models.CharField(max_length=50, null=True, blank=True)
    goal_type = models.CharField(max_length=100, null=True, blank=True)
    goal_description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} — {self.goal_name}" if self.user else "Fitness Goal"


class MedicalInfo(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    condition_name = models.CharField(max_length=100, null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} — {self.condition_name}" if self.user else "Medical Info"


class WorkoutPreference(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    workout_style = models.CharField(max_length=100, null=True, blank=True)
    equipment_owned = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} — {self.workout_style}" if self.user else "Workout Preference"


class PlanSelection(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    selected_plan = models.CharField(max_length=100, null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} — {self.selected_plan}" if self.user else "Plan"
