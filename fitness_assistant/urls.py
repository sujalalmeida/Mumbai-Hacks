"""
URL configuration for fitness_assistant project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # mount your workout app at /session/
    path('admin/', admin.site.urls),
    path('session/', include('workout.urls')),
    # your landing page, if any
    path('', include('home.urls')),  # or whatever your landing is
    path('fit/', include('fitness_assistant.fit_tracker.urls')),
        path('community/', include('community.urls')),  # Replace 'fitness_community' with your app name


    path('food-tracker/', include('food_tracker.urls')),  # Changed underscore to hyphen
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # Add this for serving media files
