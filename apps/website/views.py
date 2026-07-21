from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import BlogPost, ComponentPage, HeaderMenuItem, ServicePage
from .serializers import (
    BlogPostSerializer,
    ComponentPageSerializer,
    ContactMessageSerializer,
    ContactResponseSerializer,
    HeaderMenuItemSerializer,
    ServicePageSerializer,
)


class HeaderMenuView(ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = HeaderMenuItemSerializer
    queryset = HeaderMenuItem.objects.filter(parent__isnull=True, is_active=True).prefetch_related("children__children")


class ComponentPageListView(ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = ComponentPageSerializer
    queryset = ComponentPage.objects.all()


class ComponentPageDetailView(RetrieveAPIView):
    permission_classes = (AllowAny,)
    serializer_class = ComponentPageSerializer
    queryset = ComponentPage.objects.all()
    lookup_field = "slug"


class ServicePageListView(ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = ServicePageSerializer
    queryset = ServicePage.objects.filter(is_published=True).select_related("service").prefetch_related("steps")


class ServicePageDetailView(RetrieveAPIView):
    permission_classes = (AllowAny,)
    serializer_class = ServicePageSerializer
    queryset = ServicePage.objects.filter(is_published=True).select_related("service").prefetch_related("steps")
    lookup_field = "slug"


class BlogPostListView(ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = BlogPostSerializer
    queryset = BlogPost.objects.filter(is_published=True)


class BlogPostDetailView(RetrieveAPIView):
    permission_classes = (AllowAny,)
    serializer_class = BlogPostSerializer
    queryset = BlogPost.objects.filter(is_published=True)
    lookup_field = "slug"


class ContactMessageView(CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = ContactMessageSerializer

    @extend_schema(responses={201: ContactResponseSerializer})
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            "status": "received",
            "message": "Thank you. Our team will contact you shortly.",
        }, status=status.HTTP_201_CREATED)
