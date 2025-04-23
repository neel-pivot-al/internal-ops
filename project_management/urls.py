from django.urls import path
from rest_framework.routers import DefaultRouter

from project_management.views import InvoiceView, generate_invoice
from project_management.viewsets import (
    FeatureViewSet,
    InvoiceViewSet,
    ProjectRateViewSet,
    ProjectViewSet,
    WorkLogViewSet,
)

router = DefaultRouter()
router.register(r"projects", ProjectViewSet)
router.register(r"worklogs", WorkLogViewSet)
router.register(r"invoices", InvoiceViewSet)
router.register(r"features", FeatureViewSet)
router.register(r"project-rates", ProjectRateViewSet)
urlpatterns = [
    *router.urls,
    path("generate_invoice/", generate_invoice),
]
