from django.urls import path
from . import views
from django.shortcuts import redirect

app_name = 'fit_tracker'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('chart-data/', views.chart_data, name='chart_data'),
    path('chat/', views.chatbot, name='chatbot'),
        path('accounts/login/', lambda request: redirect('/login/')),  # Temporary fix

] 