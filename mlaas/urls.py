from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from apps.developer_api.views import DocumentationView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/schema/", SpectacularAPIView.as_view(), name="api-schema"),
    path("api/docs/", DocumentationView.as_view(), name="developer-documentation"),
    path("api/reference/", SpectacularSwaggerView.as_view(url_name="api-schema"), name="swagger-ui"),
    path("api/v1/auth/", include("apps.authentication.urls")),
    path("api/v1/user/", include("apps.authentication.profile_urls")),
    path("api/v1/developer/", include("apps.developer_api.urls")),
    path("api/v1/website/", include("apps.website.urls")),
    path("api/v1/", include("apps.analytics.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += staticfiles_urlpatterns()
