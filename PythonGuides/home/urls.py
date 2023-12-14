from django.urls import path
from .views import *

urlpatterns = [
    path('', register, name='register'),
    path('signup',signup),
    path('login',login,name='login'),
    path('location',save_location),
]