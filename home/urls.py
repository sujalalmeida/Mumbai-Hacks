# core/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('',                 views.landing_page,    name='landing'),
    path('signup/',          views.signup_view,     name='signup'),
    path('login/',           views.login_view,      name='login'),
    path('get-started/',     views.get_started,     name='get_started'),
    path('user-details/',    views.user_details_view, name='user_details'),
    path('set-goal/',        views.set_goal_view,   name='set_goal'),
    path('onboarding/',      views.onboarding_view, name='onboarding'),
    path('plans/',           views.plans_view,      name='plans'),
    path('show-plan/',       views.show_plan_view,  name='show_plan'),
    path('dashboard/',       views.dashboard_view,  name='dashboard'),
    path('profile/',       views.profile_view,  name='profile'),
    path('challenge/',       views.challenge_view,  name='challenge'),


]
