from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),    # Handles login, logout, and user dashboards.
    path('documents/', include('documents.urls')),   # Handles client document management.
]
