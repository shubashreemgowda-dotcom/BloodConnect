from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path
from dashboards.views import home
from dashboards.sitemaps import NettaruSitemap


sitemaps = {
    "site": NettaruSitemap,
}


urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),
    path('auth/', include('authentication.urls')),
    path('dashboards/', include('dashboards.urls')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),
]