from django.urls import path

from .views import BlogPostDetailView, BlogPostListView, ContactMessageView

urlpatterns = [
    path("blog/", BlogPostListView.as_view(), name="blog-list"),
    path("blog/<slug:slug>/", BlogPostDetailView.as_view(), name="blog-detail"),
    path("contact/", ContactMessageView.as_view(), name="contact"),
]
