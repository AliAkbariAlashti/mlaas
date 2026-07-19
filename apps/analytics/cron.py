from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from .models import Project


@shared_task
def purge_expired_uploads() -> int:
    projects = Project.objects.exclude(raw_file_path="").filter(created_at__lt=timezone.now() - timedelta(hours=48))
    purged = 0
    for project in projects.iterator():
        project.raw_file_path.delete(save=False)
        Project.objects.filter(pk=project.pk).update(raw_file_path="")
        purged += 1
    return purged
