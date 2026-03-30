from django.urls import path
from . import views

urlpatterns = [
    path('', views.order_list, name='order_list'),
    path('bulk/', views.bulk_create_orders, name='bulk_create_orders'),  # Bulk import API
    path('pending/', views.pending_orders, name='pending_orders'),
    path('stats/warehouse/<uuid:warehouse_id>/', views.warehouse_stats, name='warehouse_stats'),
    path('capacity/<uuid:warehouse_id>/', views.warehouse_capacity, name='warehouse_capacity'),  # Check remaining capacity
    path('<uuid:pk>/', views.order_detail, name='order_detail'),
    path('<uuid:pk>/status/', views.update_order_status, name='update_order_status'),
    path('<uuid:pk>/assign/', views.assign_order, name='assign_order'),
    path('delete-all/', views.delete_all_orders, name='delete_all_orders'),
]
