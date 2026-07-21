from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from rest_framework.test import APIClient

from apps.authentication.models import User

from ..models import Dataset, Project, RunEvent
from ..tasks import run_analysis_task


class DatasetAndRunLifecycleTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(phone_number="+989120000090")
        self.other_user = User.objects.create_user(phone_number="+989120000091")
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    @staticmethod
    def csv_upload(name="orders.csv"):
        return SimpleUploadedFile(
            name,
            b"invoice,product,quantity\n1,Coffee,1\n1,Cake,1\n2,Coffee,1\n2,Cake,1\n",
            content_type="text/csv",
        )

    def test_dataset_can_be_uploaded_listed_and_is_private(self):
        created = self.client.post(
            "/api/v1/datasets/",
            {"name": "July orders", "file": self.csv_upload()},
            format="multipart",
        )
        self.assertEqual(created.status_code, 201, created.data)
        self.assertEqual(created.data["detected_columns"], ["invoice", "product", "quantity"])
        self.assertEqual(created.data["validation_status"], Dataset.ValidationStatus.VALID)
        self.assertEqual(created.data["runs_count"], 0)

        listed = self.client.get("/api/v1/datasets/")
        self.assertEqual(listed.status_code, 200)
        self.assertEqual(len(listed.data), 1)

        self.client.force_authenticate(self.other_user)
        hidden = self.client.get(f"/api/v1/datasets/{created.data['id']}/")
        self.assertEqual(hidden.status_code, 404)

    @patch("apps.analytics.views.run_analysis_task.delay")
    def test_legacy_upload_creates_dataset_and_run_timeline(self, delay):
        uploaded = self.client.post(
            "/api/v1/projects/upload/",
            {"file": self.csv_upload(), "title": "Basket run", "analysis_type": "MARKET_BASKET"},
            format="multipart",
        )
        self.assertEqual(uploaded.status_code, 201, uploaded.data)
        project = Project.objects.select_related("dataset").get(pk=uploaded.data["project_id"])
        self.assertEqual(project.dataset.detected_columns, ["invoice", "product", "quantity"])
        self.assertEqual(list(project.events.values_list("stage", flat=True)), [RunEvent.Stage.CREATED])

        with self.captureOnCommitCallbacks(execute=True):
            started = self.client.post(
                f"/api/v1/projects/{project.id}/start/",
                {"mapping": {
                    "invoice_id_column": "invoice",
                    "product_name_column": "product",
                    "quantity_column": "quantity",
                }},
                format="json",
            )
        self.assertEqual(started.status_code, 202, started.data)
        delay.assert_called_once_with(str(project.id))

        run_analysis_task.run(str(project.id))
        project.refresh_from_db()
        project.dataset.refresh_from_db()
        self.assertEqual(project.status, Project.Status.SUCCESS)
        self.assertIsNotNone(project.started_at)
        self.assertIsNotNone(project.completed_at)
        self.assertGreaterEqual(project.duration_seconds, 0)
        self.assertEqual(project.dataset.row_count, 4)

        events = self.client.get(f"/api/v1/projects/{project.id}/events/")
        self.assertEqual(events.status_code, 200)
        self.assertEqual(
            [event["stage"] for event in events.data],
            [
                "CREATED", "MAPPING", "QUEUED", "LOADING", "PREPROCESSING",
                "FEATURE_ENGINEERING", "MODEL_EXECUTION", "EVALUATING",
                "RESULT_GENERATION", "COMPLETED",
            ],
        )
