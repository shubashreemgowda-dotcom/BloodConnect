from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path
from django.views.generic import TemplateView
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

    path(
        'robots.txt',
        TemplateView.as_view(
            template_name='robots.txt',
            content_type='text/plain'
        ),
        name='robots'
    ),
]