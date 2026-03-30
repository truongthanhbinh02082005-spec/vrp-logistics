from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('orders/', views.order_report, name='order_report'),
    path('vehicles/', views.vehicle_report, name='vehicle_report'),
    path('routes/', views.route_report, name='route_report'),
    path('performance/', views.performance_report, name='performance_report'),
]
