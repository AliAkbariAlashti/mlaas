from django.utils import timezone
from django.db.models import Prefetch
from django.views.generic import TemplateView
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import GenericAPIView, ListCreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import APIKey, APIUsage, DocumentationBlock, DocumentationPage, DocumentationSection
from .serializers import (
    APIAccessSerializer,
    APIKeyCreatedSerializer,
    APIKeySerializer,
    CreateAPIKeySerializer,
)


class APIKeyListCreateView(ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def get_queryset(self):
        return APIKey.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        return CreateAPIKeySerializer if self.request.method == "POST" else APIKeySerializer

    @extend_schema(request=CreateAPIKeySerializer, responses={201: APIKeyCreatedSerializer})
    def post(self, request, *args, **kwargs):
        serializer = CreateAPIKeySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        key, secret = APIKey.issue(request.user, serializer.validated_data["name"])
        data = APIKeySerializer(key).data
        data["secret"] = secret
        return Response(data, status=status.HTTP_201_CREATED)


class APIKeyRevokeView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    @extend_schema(request=None, responses={204: None})
    def delete(self, request, key_id):
        key = APIKey.objects.filter(pk=key_id, user=request.user).first()
        if not key:
            return Response(status=status.HTTP_404_NOT_FOUND)
        key.is_active = False
        key.save(update_fields=("is_active",))
        return Response(status=status.HTTP_204_NO_CONTENT)


class APIAccessView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)
    serializer_class = APIAccessSerializer

    def get(self, request):
        subscription = getattr(request.user, "api_subscription", None)
        if not subscription:
            return Response({"detail": "No API subscription is assigned."}, status=404)
        used = APIUsage.objects.filter(
            api_key__user=request.user,
            created_at__gte=subscription.current_period_start,
        ).count()
        plan = subscription.plan
        return Response(
            {
                "plan": plan.name,
                "status": subscription.status,
                "monthly_request_limit": plan.monthly_request_limit,
                "requests_used": used,
                "requests_remaining": max(plan.monthly_request_limit - used, 0),
                "period_start": subscription.current_period_start,
                "period_end": subscription.current_period_end,
                "services": list(
                    plan.services.values("code", "name_en", "name_fa", "is_active")
                ),
                "endpoints": list(
                    plan.endpoint_policies.filter(is_active=True).values(
                        "name", "path_prefix", "allow_api_keys"
                    )
                ),
            }
        )


class DocumentationView(TemplateView):
    template_name = "developer_api/docs.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pages = DocumentationPage.objects.filter(is_active=True).select_related(
            "section", "service"
        ).prefetch_related(
            Prefetch("blocks", queryset=DocumentationBlock.objects.filter(is_active=True))
        )
        sections = DocumentationSection.objects.filter(is_active=True).prefetch_related(
            Prefetch("pages", queryset=pages, to_attr="visible_pages")
        )
        page_slug = self.request.GET.get("page")
        selected_page = pages.filter(slug=page_slug).first() if page_slug else pages.first()
        context.update({
            "documentation_sections": sections,
            "selected_page": selected_page,
            "swagger_url": "/api/reference/",
            "schema_url": "/api/schema/",
        })
        return context
