from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.contrib.sitemaps.views import sitemap
from shop.sitemaps import ProductSitemap


sitemaps = {
    "products": ProductSitemap,
}


urlpatterns = [
    # Allauth URL's
    path("accounts/", include("allauth.urls")),
    # Apps
    path("", include("shop.urls", namespace="shop")),
    path("", include("blog.urls", namespace="blog")),
    path("cart/", include("cart.urls", namespace="cart")),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    path("ckeditor5/", include("django_ckeditor_5.urls")),
]

# ERROR 404- NOT FOUND PAGE
handler404 = "shop.views.Erro404View"

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
