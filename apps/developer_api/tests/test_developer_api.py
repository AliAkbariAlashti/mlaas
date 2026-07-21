from django.urls import reverse
from rest_framework.test import APIClient, APITestCase

from apps.analytics.models import AnalysisService
from apps.authentication.models import User
from apps.developer_api.models import (
    APIEndpointPolicy,
    APIKey,
    APIPlan,
    APISubscription,
    APIUsage,
    DocumentationPage,
    DocumentationSection,
)


class APIKeyModelTests(APITestCase):
    def test_secret_is_hashed_and_can_be_authenticated(self):
        user = User.objects.create_user("09120000001")
        key, secret = APIKey.issue(user, "Production")

        self.assertNotEqual(secret, key.secret_hash)
        self.assertNotIn(secret, key.prefix)
        self.assertEqual(APIKey.authenticate(secret), key)
        self.assertIsNone(APIKey.authenticate("invalid"))


class APIKeyAccessTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user("09120000002")
        self.service = AnalysisService.objects.create(
            code="TEST_API",
            name_en="Test API",
            name_fa="Test API",
            is_active=True,
            result_kind=AnalysisService.ResultKind.RFM,
        )
        self.policy = APIEndpointPolicy.objects.get(path_prefix="/api/v1/dashboard/")
        self.plan = APIPlan.objects.create(name="API Test", monthly_request_limit=1)
        self.plan.services.add(self.service)
        self.plan.endpoint_policies.add(self.policy)
        APISubscription.objects.create(user=self.user, plan=self.plan)
        self.key, self.secret = APIKey.issue(self.user, "Test")

    def test_key_access_records_usage_and_enforces_quota(self):
        client = APIClient()
        response = client.get("/api/v1/dashboard/", HTTP_X_API_KEY=self.secret)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["X-RateLimit-Remaining"], "0")
        self.assertEqual(APIUsage.objects.filter(api_key=self.key).count(), 1)

        throttled = client.get("/api/v1/dashboard/", HTTP_X_API_KEY=self.secret)
        self.assertEqual(throttled.status_code, 429)

    def test_admin_can_disable_api_key_access_for_endpoint(self):
        self.policy.allow_api_keys = False
        self.policy.save(update_fields=("allow_api_keys",))

        response = APIClient().get(
            "/api/v1/dashboard/", HTTP_X_API_KEY=self.secret
        )
        self.assertIn(response.status_code, {401, 403})


class APIKeyManagementTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user("09120000003")
        self.client.force_authenticate(self.user)

    def test_customer_can_create_list_and_revoke_key(self):
        created = self.client.post(
            reverse("developer-api-keys"), {"name": "Production"}, format="json"
        )
        self.assertEqual(created.status_code, 201)
        self.assertTrue(created.data["secret"].startswith("mlaas_live_"))

        listed = self.client.get(reverse("developer-api-keys"))
        self.assertEqual(len(listed.data), 1)
        self.assertNotIn("secret", listed.data[0])

        revoked = self.client.delete(
            reverse("developer-api-key-revoke", args=(created.data["id"],))
        )
        self.assertEqual(revoked.status_code, 204)
        self.assertFalse(APIKey.objects.get(pk=created.data["id"]).is_active)


class DocumentationTests(APITestCase):
    def test_public_docs_render_seeded_bilingual_service_content(self):
        response = self.client.get(reverse("developer-documentation"), {"page": "rfm-segmentation"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "RFM Segmentation")
        self.assertContains(response, "بخش‌بندی RFM")
        self.assertContains(response, "What the report shows")
        self.assertContains(response, "گزارش چه چیزی نشان می‌دهد")
        self.assertContains(response, "customer_id,invoice_date,invoice_id,total_amount")

    def test_documentation_hierarchy_is_admin_managed(self):
        self.assertGreaterEqual(DocumentationSection.objects.filter(is_active=True).count(), 5)
        self.assertEqual(DocumentationPage.objects.filter(service__isnull=False, is_active=True).count(), 10)
