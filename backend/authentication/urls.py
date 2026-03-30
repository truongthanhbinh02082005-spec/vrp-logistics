from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('logout/', views.logout, name='logout'),
    path('users/', views.user_list, name='user_list'),
    path('drivers/', views.driver_list, name='driver_list'),
    path('users/<uuid:pk>/', views.user_detail, name='user_detail'),
]
