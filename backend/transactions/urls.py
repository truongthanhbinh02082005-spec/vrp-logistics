from django.urls import path
from . import views

urlpatterns = [
    path('', views.transaction_list, name='transaction_list'),
    path('pending/', views.pending_transactions, name='pending_transactions'),
    path('<uuid:pk>/', views.transaction_detail, name='transaction_detail'),
    path('<uuid:pk>/confirm/', views.confirm_transaction, name='confirm_transaction'),
]
