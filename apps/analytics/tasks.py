from celery import shared_task

from .models import BasketResult, MLResult, Project, RFMResult


@shared_task(bind=True)
def run_analysis_task(self, project_id: str):
    project = Project.objects.select_related("service").get(pk=project_id)
    project.status = Project.Status.PROCESSING
    project.error_log = None
    project.save(update_fields=("status", "error_log"))
    try:
        # TODO: Invoke the selected ML engine and persist real calculated results.
        if project.service.result_kind == project.service.ResultKind.RFM:
            RFMResult.objects.update_or_create(project=project)
        elif project.service.result_kind == project.service.ResultKind.BASKET:
            BasketResult.objects.update_or_create(project=project)
        else:
            MLResult.objects.update_or_create(project=project)
        project.status = Project.Status.SUCCESS
        project.save(update_fields=("status",))
    except Exception as exc:
        project.status = Project.Status.FAILED
        project.error_log = str(exc)
        project.save(update_fields=("status", "error_log"))
        raise
