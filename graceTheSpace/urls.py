from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('adminPanel/', include('adminPanel.urls')),
    path('', include('mainWebsite.urls')),
]