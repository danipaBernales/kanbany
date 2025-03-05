from django.contrib import admin
from django.urls import path, include

urlpatterns = [    
    # Django Admin
    path('admin/', admin.site.urls),
    
    # Include tasks app URLs
    path('', include('tasks.urls')),
]
