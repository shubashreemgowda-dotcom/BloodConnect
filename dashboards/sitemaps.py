from django.contrib.sitemaps import Sitemap


class NettaruSitemap(Sitemap):
    changefreq = "weekly"
    priority = 1.0
    protocol = "https"

    def items(self):
        return ["/"]

    def location(self, item):
        return item