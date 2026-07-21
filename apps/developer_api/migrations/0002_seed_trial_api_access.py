from django.db import migrations


POLICIES = (
    ("Service catalog", "/api/v1/services/"),
    ("Analytics dashboard", "/api/v1/dashboard/"),
    ("Projects and reports", "/api/v1/projects/"),
)


def seed_trial_access(apps, schema_editor):
    APIEndpointPolicy = apps.get_model("developer_api", "APIEndpointPolicy")
    APIPlan = apps.get_model("developer_api", "APIPlan")
    AnalysisService = apps.get_model("analytics", "AnalysisService")
    policies = []
    for name, path_prefix in POLICIES:
        policy, _ = APIEndpointPolicy.objects.get_or_create(
            path_prefix=path_prefix,
            defaults={"name": name, "allow_api_keys": True, "is_active": True},
        )
        policies.append(policy)
    plan, _ = APIPlan.objects.get_or_create(
        name="Developer Trial",
        defaults={"monthly_request_limit": 1_000, "is_active": True},
    )
    plan.endpoint_policies.set(policies)
    plan.services.set(AnalysisService.objects.filter(is_active=True))


def unseed_trial_access(apps, schema_editor):
    APIPlan = apps.get_model("developer_api", "APIPlan")
    APIEndpointPolicy = apps.get_model("developer_api", "APIEndpointPolicy")
    APIPlan.objects.filter(name="Developer Trial").delete()
    APIEndpointPolicy.objects.filter(
        path_prefix__in=[item[1] for item in POLICIES]
    ).delete()


class Migration(migrations.Migration):
    dependencies = [("developer_api", "0001_initial")]
    operations = [migrations.RunPython(seed_trial_access, unseed_trial_access)]
