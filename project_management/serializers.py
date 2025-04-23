from django.contrib.auth import get_user_model
from django.db import models
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied, ValidationError

from project_management.models import (
    Feature,
    Function,
    Invoice,
    Project,
    ProjectRate,
    WorkLog,
)

User = get_user_model()


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = "__all__"


class ClientFeatureUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feature
        fields = ["description", "title"]

    def validate(self, attrs):
        obj = self.instance
        if obj.status not in [Feature.Status.SPECS, Feature.Status.BACKLOG]:
            raise PermissionDenied("You can only update features in specs or backlog")
        return attrs


class FeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feature
        fields = "__all__"


class FunctionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Function
        fields = "__all__"


class WorkLogListSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkLog
        fields = ["id", "function", "developer", "date_logged", "hours_worked"]


class WorkLogCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkLog
        fields = ["function", "hours_worked", "description"]

    def validate(self, attrs):
        function = attrs["function"]

        function = Function.objects.get_or_404(id=function.id)

        total_hours_for_function = (
            WorkLog.objects.filter(function_id=function).aggregate(
                total_hours=models.Sum("hours_worked")
            )["total_hours"]
            or 0
        )
        if total_hours_for_function >= function.estimated_time:
            raise ValidationError("Function has already been completed")
        return attrs

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["developer"] = user
        validated_data["status"] = WorkLog.Status.REVIEW
        return super().create(validated_data)


class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = "__all__"


class GenerateInvoiceSerializer(serializers.Serializer):
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    client = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role=User.Role.CLIENT)
    )

    def validate(self, attrs):
        user = self.context["request"].user
        if user.role != User.Role.ADMIN:
            raise PermissionDenied("You are not allowed to generate invoices")
        return attrs


class ProjectRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectRate
        fields = "__all__"
