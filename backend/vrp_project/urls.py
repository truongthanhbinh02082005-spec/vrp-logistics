from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('authentication.urls')),
    path('api/warehouses/', include('warehouses.urls')),
    path('api/vehicles/', include('vehicles.urls')),
    path('api/orders/', include('orders.urls')),
    path('api/transport/', include('transport.urls')),
    path('api/reports/', include('reports.urls')),
    path('api/transactions/', include('transactions.urls')),
    path('api/benchmark/', include('benchmark.urls')),
    path('api/driver/', include('authentication.driver_urls')),
    
    # Catch-all for React Router
    re_path(r'^.*$', TemplateView.as_view(template_name='index.html')),
]
