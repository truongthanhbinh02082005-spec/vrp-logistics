from django.urls import path
from . import views

urlpatterns = [
    path('', views.vehicle_list, name='vehicle_list'),
    path('available/', views.available_vehicles, name='available_vehicles'),
    path('<uuid:pk>/', views.vehicle_detail, name='vehicle_detail'),
    path('<uuid:pk>/location/', views.update_vehicle_location, name='update_vehicle_location'),
    path('pack-orders/', views.pack_orders, name='pack_orders'),
]
