To handle this architecture cleanly, the Django project follows a decoupled, **scalable modular app pattern** optimized for background task processing.

It splits the codebase into clean applications: `authentication` (for user profiles and OTP), `analytics` (for keeping track of analysis records, mapping states, and waitlist leads), and a dedicated Python package directory (`ml_engines`) where the core data science code lives—separate from standard web logic.

Here is the exact production-ready directory tree and setup configuration.

---

## 📂 Project Directory Structure

```text
ai_analytics_backend/
│
├── manage.py
├── requirements.txt
├── README.md
│
├── ai_analytics/                 # Project Configuration Root
│   ├── __init__.py
│   ├── settings.py               # Database, Redis, Celery, and Auth configuration
│   ├── urls.py                   # Master API routing panel
│   ├── wsgi.py
│   └── celery_app.py             # Celery architecture initialization
│
├── apps/                         # Modular Application Directory
│   ├── __init__.py
│   │
│   ├── authentication/           # Users, Profiles, and OTP Core
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py             # Custom User model (phone_number, credit_limit)
│   │   ├── serializers.py        # OTPSerializer, ProfileSerializer
│   │   ├── urls.py
│   │   ├── views.py              # SendOTPView, VerifyOTPView, ProfileUpdateView
│   │   └── services.py           # SMS Gateway handlers / mock token logic
│   │
│   └── analytics/                # Projects, Dynamic Mapping, and Waitlists
│       ├── __init__.py
│       ├── admin.py
│       ├── apps.py
│       ├── models.py             # Project, RFMResult, BasketResult, MLResult models
│       ├── serializers.py        # ProjectUploadSerializer, MappingSerializer, ResultSerializers
│       ├── urls.py
│       ├── views.py              # UploadView, StartAnalysisView, StatusPollingView, ResultViews
│       ├── tasks.py              # Celery task definitions (handles queuing wrappers)
│       └── cron.py               # Data privacy routines (automated 48h raw file cleanup script)
│
├── ml_engines/                   # Core Python Data Science Package (No Django dependencies)
│   ├── __init__.py
│   ├── exceptions.py             # Custom errors (e.g., RowParsingError, EmptyColumnError)
│   ├── utils.py                  # Shared helpers (e.g., standard datetime converter)
│   ├── rfm_segmenter.py          # Operational RFM code using Pandas & Numpy
│   ├── market_basket.py          # Operational Market Basket code using MLXtend (Apriori)
│   ├── propensity_scorer.py      # Operational Propensity scoring models using Sklearn
│   └── anomaly_detector.py       # Operational Isolation Forest code for anomaly spotting
│
└── media/                        # Temporary File System Target
    ├── uploads/                  # Input storage path for raw user Excel/CSV records
    └── downloads/                # Generated, downloadable segmented Excel files

```

---

## 🛠️ Key Architectural Configuration Samples

### 1. Celery Broker Setup (`ai_analytics/celery_app.py`)

This file registers the background worker instance, binding with Redis to offload heavy calculations from the client threads.

```python
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_analytics.settings')

app = Celery('ai_analytics')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Automatically discover tasks.py files across registered apps
app.autodiscover_tasks(['apps.analytics'])

```

### 2. Decoupling Web Tasks from Data Science Engine (`apps/analytics/tasks.py`)

This Celery task acts as the web-to-engine translation adapter layer. It loads the database record, runs the raw computational backend from `ml_engines`, writes the artifact out, and updates the task status to `SUCCESS`.

```python
import pandas as pd
from celery import shared_task
from django.utils import timezone
from apps.analytics.models import Project, RFMResult
from ml_engines.rfm_segmenter import calculate_rfm

@shared_task(bind=True)
def run_rfm_analysis_task(self, project_id):
    try:
        project = Project.objects.get(id=project_id)
        project.status = 'PROCESSING'
        project.save()
        
        # Load the raw user data file safely
        df = pd.read_excel(project.raw_file_path) if project.raw_file_path.endswith('.xlsx') else pd.read_csv(project.raw_file_path)
        
        # Pull down the structural column mapping array passed by the client UI
        mapping = project.data_mapping
        
        # Core ML Engine invocation (clean separation from Django models)
        summary_metrics, visual_chart_data, output_df = calculate_rfm(
            data_frame=df,
            customer_id_col=mapping['customer_id_column'],
            date_col=mapping['date_column'],
            amount_col=mapping['amount_column'],
            invoice_id_col=mapping['invoice_id_column']
        )
        
        # Save output artifacts to disk
        output_path = f"media/downloads/rfm_out_{project.id}.xlsx"
        output_df.to_excel(output_path, index=False)
        
        # Commit results to persistent relational DB columns
        RFMResult.objects.create(
            project=project,
            summary=summary_metrics,
            chart_data=visual_chart_data,
            result_file_path=output_path
        )
        
        project.status = 'SUCCESS'
        project.save()

    except Exception as exc:
        project.status = 'FAILED'
        project.error_log = str(exc)
        project.save()
        raise exc

```

This structural separation ensures your team can build out new operational micro-features or refactor machine learning configurations inside `ml_engines` without breaking or altering database schemas or standard Django URL routing structures.