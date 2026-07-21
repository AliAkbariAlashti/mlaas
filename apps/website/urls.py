from django.urls import path

from .views import (
    BlogPostDetailView,
    BlogPostListView,
    ComponentPageDetailView,
    ComponentPageListView,
    ContactMessageView,
    HeaderMenuView,
    ServicePageDetailView,
    ServicePageListView,
)

urlpatterns = [
    path("navigation/", HeaderMenuView.as_view(), name="navigation"),
    path("components/", ComponentPageListView.as_view(), name="component-list"),
    path("components/<slug:slug>/", ComponentPageDetailView.as_view(), name="component-detail"),
    path("products/", ServicePageListView.as_view(), name="product-list"),
    path("products/<slug:slug>/", ServicePageDetailView.as_view(), name="product-detail"),
    path("blog/", BlogPostListView.as_view(), name="blog-list"),
    path("blog/<slug:slug>/", BlogPostDetailView.as_view(), name="blog-detail"),
    path("contact/", ContactMessageView.as_view(), name="contact"),
]
