from django.contrib.auth import get_user_model
from rest_framework import status, viewsets
from rest_framework.exceptions import MethodNotAllowed, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.permissions import (
    IsAdmin,
    IsAdminOrClient,
    IsAdminOrClientOrDeveloper,
    IsAdminOrDeveloper,
    IsDeveloper,
)
from project_management.filters import WorkLogFilter
from project_management.models import (
    Feature,
    Function,
    Invoice,
    Project,
    ProjectRate,
    WorkLog,
)
from project_management.serializers import (
    ClientFeatureUpdateSerializer,
    FeatureSerializer,
    FunctionSerializer,
    InvoiceSerializer,
    ProjectRateSerializer,
    ProjectSerializer,
    WorkLogCreateSerializer,
    WorkLogListSerializer,
)

User = get_user_model()


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    search_fields = ["title", "description"]
    ordering_fields = ["start_date", "end_date", "priority", "status"]
    filterset_fields = {
        "status": ["exact"],
        "priority": ["exact"],
        "start_date": ["exact", "gte", "lte"],
        "end_date": ["exact", "gte", "lte"],
        "client": ["exact"],
    }
    http_method_names = ["get", "post", "patch", "delete"]

    def partial_update(self, request, *args, **kwargs):
        if request.user.role != User.Role.ADMIN:
            raise PermissionDenied("You are not allowed to update this project")
        return super().partial_update(request, *args, **kwargs)

    def get_permissions(self):
        permissions = [IsAuthenticated]
        if self.action in ["create", "update", "partial_update", "destroy"]:
            permissions = [IsAdmin]
        return [permission() for permission in permissions]

    def get_serializer_class(self):
        return ProjectSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == User.Role.CLIENT:
            return Project.objects.filter(client=user)
        elif user.role == User.Role.DEVELOPER:
            return Project.objects.filter(developers__in=[user])
        return Project.objects.all()


class FeatureViewSet(viewsets.ModelViewSet):
    queryset = Feature.objects.all()
    serializer_class = FeatureSerializer
    search_fields = ["title", "description"]
    ordering_fields = ["status"]
    filterset_fields = ["status"]
    http_method_names = ["get", "post", "patch", "delete"]

    def get_serializer_class(self):
        return FeatureSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == User.Role.CLIENT:
            return Feature.objects.filter(project__client=user)
        elif user.role == User.Role.DEVELOPER:
            return Feature.objects.filter(project__developers__in=[user])
        return Feature.objects.all()


class FunctionViewSet(viewsets.ModelViewSet):
    queryset = Function.objects.all()
    serializer_class = FunctionSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == User.Role.CLIENT:
            return Function.objects.filter(feature__project__client=user)
        elif user.role == User.Role.DEVELOPER:
            return Function.objects.filter(feature__project__developers__in=[user])
        return Function.objects.all()


class WorkLogViewSet(viewsets.ModelViewSet):
    queryset = WorkLog.objects.all()
    filterset_class = WorkLogFilter

    permission_mappings = {
        "list": [IsAdminOrClientOrDeveloper],
        "retrieve": [IsAdminOrClientOrDeveloper],
        "create": [IsDeveloper],
        "update": [IsAdminOrDeveloper],
        "partial_update": [IsAdminOrDeveloper],
    }

    def get_queryset(self):
        user = self.request.user
        if user.role == User.Role.DEVELOPER:
            return WorkLog.objects.filter(developer=user)
        if user.role == User.Role.CLIENT:
            return WorkLog.objects.filter(function__feature__project__client=user)
        return WorkLog.objects.all()

    def get_serializer_class(self):
        if self.action == "create":
            return WorkLogCreateSerializer
        return WorkLogListSerializer

    def get_permissions(self):
        return [
            permission() for permission in self.permission_mappings.get(self.action, [])
        ]

    def destroy(self, request, *args, **kwargs):
        raise MethodNotAllowed("DELETE")


class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    http_method_names = ["get"]
    serializer_class = InvoiceSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == User.Role.ADMIN:
            return Invoice.objects.all()
        if user.role == User.Role.CLIENT:
            return Invoice.objects.filter(client=user)
        if user.role == User.Role.DEVELOPER:
            return Invoice.objects.filter(
                function__feature__project__developers__in=[user]
            )
        return Invoice.objects.none()


class ProjectRateViewSet(viewsets.ModelViewSet):
    queryset = ProjectRate.objects.all()
    serializer_class = ProjectRateSerializer
    http_method_names = ["get", "post", "patch", "delete"]

    def get_permissions(self):
        if self.action in ["create", "partial_update", "destroy"]:
            return [IsAdmin()]
        return [IsAuthenticated()]
