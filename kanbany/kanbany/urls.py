from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from tasks import views

# Create a router and register our viewsets with it
router = routers.DefaultRouter()
router.register(r'tasks', views.TasksViewSet, basename='task')

# The API URLs are now determined automatically by the router
urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),
    
    # API URLs
    path('api/', include(router.urls)),
    path('api/auth/', include('rest_framework.urls', namespace='rest_framework')),
    
    # Include our tasks app URLs
    path('', include('tasks.urls')),
]
