from django.utils import timezone

from .models import APIKey, APIUsage


class APIUsageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        key = getattr(request, "mlaas_api_key", None)
        policy = getattr(request, "mlaas_api_policy", None)
        if key and policy:
            APIUsage.objects.create(
                api_key=key,
                endpoint_policy=policy,
                method=request.method,
                path=request.path[:500],
                status_code=response.status_code,
            )
            APIKey.objects.filter(pk=key.pk).update(last_used_at=timezone.now())
            limit = request.mlaas_api_limit
            response["X-RateLimit-Limit"] = str(limit)
            response["X-RateLimit-Remaining"] = str(
                max(limit - request.mlaas_api_used - 1, 0)
            )
        return response
