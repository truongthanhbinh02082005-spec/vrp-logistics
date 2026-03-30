from django.urls import path
from . import views

urlpatterns = [
    path('', views.warehouse_list, name='warehouse_list'),
    path('<uuid:pk>/', views.warehouse_detail, name='warehouse_detail'),
]
