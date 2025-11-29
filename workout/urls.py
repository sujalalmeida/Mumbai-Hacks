from django.urls import path
from . import views

urlpatterns = [
    path('', views.workout_session, name='workout_session'),
    path('video_feed/', views.video_feed, name='video_feed'),
    path('toggle_camera/', views.toggle_camera, name='toggle_camera'),
    path('update_exercise/', views.update_exercise, name='update_exercise'),
    path('get_workout_stats/', views.get_workout_stats, name='get_workout_stats'),
    path('get_music_recommendations/', views.get_music_recommendations, name='get_music_recommendations'),
    path('search_youtube_music/', views.search_youtube_music, name='search_youtube_music'),
        path('connect_music_service/', views.connect_music_service, name='connect_music_service'),
                path('voice_command_handler/', views.voice_command_handler, name='voice_command_handler'),


]
