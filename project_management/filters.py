from django_filters import rest_framework as filters

from project_management.models import Project, WorkLog


class ProjectFilter(filters.FilterSet):
    class Meta:
        model = Project
        fields = "__all__"


class WorkLogFilter(filters.FilterSet):
    project = filters.ModelChoiceFilter(
        field_name="function__feature__project",
        queryset=Project.objects.all(),
        label="Project",
    )

    class Meta:
        model = WorkLog
        fields = ["project", "developer", "status"]
