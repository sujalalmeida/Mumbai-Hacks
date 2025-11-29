# # core/forms.py
# from django import forms
# from django.contrib.auth.models import User
# from django.contrib.auth.forms import AuthenticationForm

# class SignUpForm(forms.ModelForm):
#     password = forms.CharField(widget=forms.PasswordInput)

#     class Meta:
#         model = User
#         fields = ['username', 'email', 'password']

# class LoginForm(AuthenticationForm):
#     username = forms.CharField()
#     password = forms.CharField(widget=forms.PasswordInput)
# core/forms.py
from django import forms
from .models import (
    UserProfile, Lifestyle, Diet, FoodAllergy, FitnessGoal,
    MedicalInfo, WorkoutPreference, PlanSelection
)
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['full_name', 'dob', 'gender', 'height', 'weight']

class LifestyleForm(forms.ModelForm):
    class Meta:
        model = Lifestyle
        fields = ['activity_level', 'sleep_quality', 'stress_level']

class DietForm(forms.ModelForm):
    class Meta:
        model = Diet
        fields = ['diet_type']

class FoodAllergyForm(forms.ModelForm):
    class Meta:
        model = FoodAllergy
        fields = ['allergen']

class FitnessGoalForm(forms.ModelForm):
    class Meta:
        model = FitnessGoal
        exclude = ['user']

class MedicalInfoForm(forms.ModelForm):
    class Meta:
        model = MedicalInfo
        fields = ['condition_name', 'notes']

class WorkoutPreferenceForm(forms.ModelForm):
    class Meta:
        model = WorkoutPreference
        fields = ['workout_style', 'equipment_owned']

class PlanSelectionForm(forms.ModelForm):
    class Meta:
        model = PlanSelection
        fields = ['selected_plan', 'start_date']

class SignUpForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

class LoginForm(AuthenticationForm):
    pass  # Extend if custom login fields needed
