from django.urls import path

from .views import APIAccessView, APIKeyListCreateView, APIKeyRevokeView


urlpatterns = [
    path("access/", APIAccessView.as_view(), name="developer-api-access"),
    path("keys/", APIKeyListCreateView.as_view(), name="developer-api-keys"),
    path("keys/<int:key_id>/", APIKeyRevokeView.as_view(), name="developer-api-key-revoke"),
]
