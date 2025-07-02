from django.urls import path
from .views import check_password_strength, home

urlpatterns = [
    path('', home, name='home'),  # Home page
    path('check-password/', check_password_strength, name='check_password'),
]
