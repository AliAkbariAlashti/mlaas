from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("analytics", "0003_seed_analysis_services")]
    operations = [
        migrations.AlterField(
            model_name="project",
            name="status",
            field=models.CharField(
                choices=[
                    ("PENDING", "Pending"),
                    ("PROCESSING", "Processing"),
                    ("SUCCESS", "Success"),
                    ("FAILED", "Failed"),
                    ("WAITLISTED", "Private beta requested"),
                ],
                default="PENDING",
                max_length=15,
            ),
        ),
    ]
