from django.urls import path
from . import views

# Driver-specific URL patterns
urlpatterns = [
    path('current-order/', views.driver_current_order, name='driver_current_order'),
    path('orders/', views.driver_orders, name='driver_orders'),
    path('confirm-delivery/', views.confirm_delivery, name='confirm_delivery'),
    path('delivery/failed/', views.mark_delivery_failed, name='mark_delivery_failed'),
]

