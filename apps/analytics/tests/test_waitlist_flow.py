from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from rest_framework.test import APIClient

from apps.authentication.models import User

from ..models import Project, WaitlistLead


class PrivateBetaFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(phone_number="+989120000002")
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_beta_request_gets_a_distinct_waitlisted_status(self):
        upload = SimpleUploadedFile(
            "churn.csv",
            b"customer_id,last_purchase_date\nC-1,2025-01-01\n",
            content_type="text/csv",
        )
        uploaded = self.client.post(
            "/api/v1/projects/upload/",
            {"file": upload, "title": "Churn beta", "analysis_type": "CHURN"},
            format="multipart",
        )
        self.assertEqual(uploaded.status_code, 201, uploaded.data)

        project_id = uploaded.data["project_id"]
        joined = self.client.post(f"/api/v1/projects/{project_id}/join-waitlist/")
        self.assertEqual(joined.status_code, 200, joined.data)
        self.assertEqual(joined.data["status"], "waitlisted")

        project = Project.objects.get(pk=project_id)
        self.assertEqual(project.status, Project.Status.WAITLISTED)
        self.assertTrue(WaitlistLead.objects.filter(project=project, user=self.user).exists())
        self.assertEqual(User.objects.get(pk=self.user.pk).credit_limit, 3)

        duplicate = self.client.post(f"/api/v1/projects/{project_id}/join-waitlist/")
        self.assertEqual(duplicate.status_code, 200, duplicate.data)
        self.assertEqual(WaitlistLead.objects.filter(project=project).count(), 1)
