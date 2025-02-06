from django.contrib import admin
from django.urls import path, include
from listings import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'), 
    path('api/', include('listings.urls')),  # Include the app's URLs here
]
