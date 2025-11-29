from django.urls import path
from . import views

app_name = 'community'  # Set the app namespace for URL naming

urlpatterns = [
    path('community/', views.community_hub, name='community_hub'),
]