from django.urls import path

from .views import (
    BasketResultView,
    JoinWaitlistView,
    PredictiveResultView,
    ProjectStatusView,
    ProjectUploadView,
    RFMResultView,
    ServiceListView,
    StartAnalysisView,
)

urlpatterns = [
    path("services/", ServiceListView.as_view(), name="service-list"),
    path("projects/upload/", ProjectUploadView.as_view(), name="project-upload"),
    path("projects/<uuid:project_id>/start/", StartAnalysisView.as_view(), name="project-start"),
    path("projects/<uuid:project_id>/status/", ProjectStatusView.as_view(), name="project-status"),
    path("projects/<uuid:project_id>/rfm-results/", RFMResultView.as_view(), name="rfm-results"),
    path("projects/<uuid:project_id>/basket-results/", BasketResultView.as_view(), name="basket-results"),
    path("projects/<uuid:project_id>/predictive-results/", PredictiveResultView.as_view(), name="predictive-results"),
    path("projects/<uuid:project_id>/join-waitlist/", JoinWaitlistView.as_view(), name="join-waitlist"),
]
