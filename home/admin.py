from django.contrib import admin
from .models import (
    UserProfile,
    FitnessGoal,
    Lifestyle,
    Diet,
    FoodAllergy,
    MedicalInfo,
    WorkoutPreference,
    PlanSelection
)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user_display',
        'full_name',
        'gender',
        'height',
        'weight',
        'get_activity_level'
    )

    def user_display(self, obj):
        return obj.user.username if obj.user else "—"
    user_display.short_description = 'User'

    def get_activity_level(self, obj):
        if obj.user:
            lifestyle = obj.user.lifestyle_set.first()
            return lifestyle.activity_level if lifestyle and lifestyle.activity_level else '—'
        return '—'
    get_activity_level.short_description = 'Activity Level'


@admin.register(FitnessGoal)
class FitnessGoalAdmin(admin.ModelAdmin):
    list_display = (
        'user_display',
        'goal_name',
        'goal_type',
        'experience_level',
        'target_weight',
        'target_date'
    )

    def user_display(self, obj):
        return obj.user.username if obj.user else "—"
    user_display.short_description = 'User'


@admin.register(Lifestyle)
class LifestyleAdmin(admin.ModelAdmin):
    list_display = (
        'user_display',
        'activity_level',
        'sleep_quality',
        'stress_level'
    )

    def user_display(self, obj):
        return obj.user.username if obj.user else "—"
    user_display.short_description = 'User'


@admin.register(Diet)
class DietAdmin(admin.ModelAdmin):
    list_display = (
        'user_display',
        'diet_type'
    )

    def user_display(self, obj):
        return obj.user.username if obj.user else "—"
    user_display.short_description = 'User'


@admin.register(FoodAllergy)
class FoodAllergyAdmin(admin.ModelAdmin):
    list_display = (
        'user_display',
        'allergen'
    )

    def user_display(self, obj):
        return obj.user.username if obj.user else "—"
    user_display.short_description = 'User'


@admin.register(MedicalInfo)
class MedicalInfoAdmin(admin.ModelAdmin):
    list_display = (
        'user_display',
        'condition_name',
        'notes'
    )

    def user_display(self, obj):
        return obj.user.username if obj.user else "—"
    user_display.short_description = 'User'


@admin.register(WorkoutPreference)
class WorkoutPreferenceAdmin(admin.ModelAdmin):
    list_display = (
        'user_display',
        'workout_style',
        'equipment_owned'
    )

    def user_display(self, obj):
        return obj.user.username if obj.user else "—"
    user_display.short_description = 'User'


@admin.register(PlanSelection)
class PlanSelectionAdmin(admin.ModelAdmin):
    list_display = (
        'user_display',
        'selected_plan',
        'start_date'
    )

    def user_display(self, obj):
        return obj.user.username if obj.user else "—"
    user_display.short_description = 'User'
