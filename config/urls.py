from django.contrib import admin
from django.urls import include, path
from dashboards.views import home

urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),
    path('auth/', include('authentication.urls')),
    path('dashboards/', include('dashboards.urls')),
]