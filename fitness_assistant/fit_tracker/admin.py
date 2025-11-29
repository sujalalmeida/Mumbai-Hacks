from django.contrib import admin
from .models import FitnessData

@admin.register(FitnessData)
class FitnessDataAdmin(admin.ModelAdmin):
    list_display = ('id_from_fitbit', 'activity_date', 'total_steps', 'total_distance', 'calories')
    list_filter = ('activity_date', 'id_from_fitbit')
    search_fields = ('id_from_fitbit', 'activity_date')
    ordering = ('-activity_date',) 