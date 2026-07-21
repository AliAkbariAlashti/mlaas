from pathlib import Path

import pandas as pd
from celery import shared_task
from django.conf import settings

# Celery autodiscovers tasks.py; importing the maintenance task here registers
# the task name used by CELERY_BEAT_SCHEDULE with every worker.
from .cron import purge_expired_uploads  # noqa: F401

from ml_engines.anomaly_detector import calculate_anomalies
from ml_engines.market_basket import calculate_market_basket
from ml_engines.propensity_scorer import calculate_propensity
from ml_engines.rfm_segmenter import calculate_rfm

from .models import BasketResult, MLResult, Project, RFMResult


RFM_ACTIONS = {
    "Loyal Customers": "Protect loyalty with early access, recognition, and referral campaigns.",
    "New Customers": "Trigger a focused second-purchase journey while the first order is still recent.",
    "At Risk": "Launch a time-bound win-back offer and prioritize high-value customers for outreach.",
    "Lost Customers": "Use a reactivation test with strict spend limits before excluding inactive profiles.",
    "Potential Loyalists": "Increase purchase frequency with relevant bundles and replenishment reminders.",
}


def _load_frame(path: str) -> pd.DataFrame:
    return pd.read_csv(path) if Path(path).suffix.lower() == ".csv" else pd.read_excel(path)


def _write_result(frame: pd.DataFrame, project: Project, prefix: str) -> str:
    relative_path = Path("downloads") / f"{prefix}_{project.id}.xlsx"
    absolute_path = settings.MEDIA_ROOT / relative_path
    absolute_path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_excel(absolute_path, index=False)
    return str(relative_path)


@shared_task(bind=True)
def run_analysis_task(self, project_id: str):
    project = Project.objects.select_related("service").get(pk=project_id)
    project.status = Project.Status.PROCESSING
    project.error_log = None
    project.save(update_fields=("status", "error_log"))
    try:
        frame = _load_frame(project.raw_file_path.path)
        mapping = project.data_mapping
        if project.analysis_type == "RFM":
            summary, chart_data, output = calculate_rfm(
                frame,
                customer_id_col=mapping["customer_id_column"],
                date_col=mapping["date_column"],
                invoice_id_col=mapping["invoice_id_column"],
                amount_col=mapping.get("amount_column"),
            )
            actionable_insights = [
                {
                    "segment": item["segment"],
                    "customers": item["count"],
                    "share_percentage": item["percentage"],
                    "recommended_action": RFM_ACTIONS.get(item["segment"], "Review this cohort and define a targeted retention experiment."),
                }
                for item in sorted(chart_data, key=lambda item: item["count"], reverse=True)
            ]
            RFMResult.objects.update_or_create(project=project, defaults={
                "summary": summary,
                "chart_data": chart_data,
                "actionable_insights": actionable_insights,
                "result_file_path": _write_result(output, project, "rfm_out"),
            })
        elif project.analysis_type == "MARKET_BASKET":
            rules = calculate_market_basket(
                frame,
                invoice_id_col=mapping["invoice_id_column"],
                product_name_col=mapping["product_name_column"],
                quantity_col=mapping.get("quantity_column"),
            )
            BasketResult.objects.update_or_create(project=project, defaults={"rules": rules})
        elif project.analysis_type == "PROPENSITY":
            metrics, visualization_data, output = calculate_propensity(
                frame,
                customer_id_col=mapping["customer_id_column"],
                date_col=mapping["date_column"],
                amount_col=mapping["amount_column"],
            )
            metrics["result_file_path"] = _write_result(output, project, "propensity_out")
            MLResult.objects.update_or_create(project=project, defaults={
                "metrics": metrics,
                "visualization_data": visualization_data,
            })
        elif project.analysis_type == "ANOMALY":
            metrics, visualization_data, output = calculate_anomalies(
                frame,
                invoice_id_col=mapping["invoice_id_column"],
                date_col=mapping["date_column"],
                amount_col=mapping["amount_column"],
            )
            metrics["result_file_path"] = _write_result(output, project, "anomaly_out")
            MLResult.objects.update_or_create(project=project, defaults={
                "metrics": metrics,
                "visualization_data": visualization_data,
            })
        else:
            raise ValueError(f"Analysis service '{project.analysis_type}' is not implemented.")
        project.status = Project.Status.SUCCESS
        project.save(update_fields=("status",))
    except Exception as exc:
        project.status = Project.Status.FAILED
        project.error_log = str(exc)
        project.save(update_fields=("status", "error_log"))
        raise
