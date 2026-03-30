from django.urls import path
from . import views

urlpatterns = [
    path('routes/', views.route_list, name='route_list'),
    path('routes/delete-all/', views.delete_all_routes, name='delete_all_routes'),
    path('routes/<uuid:pk>/', views.route_detail, name='route_detail'),
    path('routes/<uuid:pk>/start/', views.start_route, name='start_route'),
    path('routes/<uuid:pk>/complete/', views.complete_route, name='complete_route'),
    path('routes/<uuid:route_pk>/stops/<uuid:stop_pk>/', views.update_stop_status, name='update_stop_status'),
    path('optimize/', views.optimize_routes, name='optimize_routes'),
    path('distance-matrix/', views.distance_matrix_view, name='distance_matrix'),
]
