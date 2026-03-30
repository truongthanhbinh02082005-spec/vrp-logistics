from django.urls import path
from . import views

urlpatterns = [
    path('instances/', views.list_instances, name='benchmark_list'),
    path('run/', views.run_benchmark, name='benchmark_run'),
    path('run-all/', views.run_all_benchmarks, name='benchmark_run_all'),
]
