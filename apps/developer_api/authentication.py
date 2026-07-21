from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed, Throttled
from drf_spectacular.extensions import OpenApiAuthenticationExtension

from .models import APIEndpointPolicy, APIKey, APIUsage


class APIKeyAuthentication(BaseAuthentication):
    header = "HTTP_X_API_KEY"

    def authenticate(self, request):
        secret = request.META.get(self.header)
        if not secret:
            return None

        key = APIKey.authenticate(secret)
        if not key:
            raise AuthenticationFailed("Invalid or revoked API key.")
        subscription = getattr(key.user, "api_subscription", None)
        if not subscription or not subscription.is_available:
            raise AuthenticationFailed("The API subscription is not active.")

        policy = self._policy_for(request.path)
        if not policy or not policy.allow_api_keys:
            raise AuthenticationFailed("API-key access is disabled for this endpoint.")
        if not subscription.plan.endpoint_policies.filter(pk=policy.pk).exists():
            raise AuthenticationFailed("This endpoint is not included in the current plan.")

        used = APIUsage.objects.filter(
            api_key__user=key.user,
            created_at__gte=subscription.current_period_start,
        ).count()
        if used >= subscription.plan.monthly_request_limit:
            raise Throttled(detail="The monthly API request limit has been reached.")

        request._request.mlaas_api_key = key
        request._request.mlaas_api_policy = policy
        request._request.mlaas_api_limit = subscription.plan.monthly_request_limit
        request._request.mlaas_api_used = used
        return key.user, key

    @staticmethod
    def _policy_for(path):
        policies = APIEndpointPolicy.objects.filter(is_active=True)
        return next(
            (
                policy
                for policy in sorted(
                    policies, key=lambda item: len(item.path_prefix), reverse=True
                )
                if path.startswith(policy.path_prefix)
            ),
            None,
        )


class APIKeyAuthenticationScheme(OpenApiAuthenticationExtension):
    target_class = "apps.developer_api.authentication.APIKeyAuthentication"
    name = "ApiKeyAuth"

    def get_security_definition(self, auto_schema):
        return {"type": "apiKey", "in": "header", "name": "X-API-Key"}
