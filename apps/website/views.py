from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import BlogPost
from .serializers import BlogPostSerializer, ContactMessageSerializer, ContactResponseSerializer


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
