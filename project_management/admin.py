from collections.abc import Sequence

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.http import HttpRequest
from simple_history.admin import SimpleHistoryAdmin

from .models import Feature, Function, Invoice, Project

User = get_user_model()

# Register your models here.


class FeatureInline(admin.TabularInline):
    show_change_link = True
    model = Feature
    extra = 1

    def get_readonly_fields(self, request, obj=None):
        if request.user.role == User.Role.CLIENT:
            return ["status", "estimated_time", "cost"]
        if request.user.role == User.Role.DEVELOPER:
            return ["status", "estimated_time", "cost"]
        return []

    def has_delete_permission(self, request, obj=None) -> bool:
        return request.user.role == User.Role.ADMIN


@admin.register(Project)
class ProjectAdmin(SimpleHistoryAdmin):
    list_display = ("title", "status", "priority", "client", "start_date")
    list_filter = ("status", "start_date")
    autocomplete_fields = ("client", "developers")
    list_editable = ("status", "priority")
    inlines = [FeatureInline]
    search_fields = ("title",)

    def get_readonly_fields(self, request, obj=None):
        if request.user.role == User.Role.CLIENT:
            return [
                "client",
                "start_date",
                "developers",
                "priority",
                "status",
                "end_date",
            ]
        if request.user.role == User.Role.DEVELOPER:
            return [
                "title",
                "description",
                "client",
                "start_date",
                "developers",
                "priority",
                "status",
                "end_date",
            ]
        return []

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.role == User.Role.ADMIN:
            return qs
        if request.user.role == User.Role.CLIENT:
            return qs.filter(client=request.user)
        if request.user.role == User.Role.DEVELOPER:
            return qs.filter(developers__in=[request.user])
        return qs.none()

    def get_list_display(self, request: HttpRequest) -> Sequence[str]:
        if request.user.role == User.Role.CLIENT:
            return ("title", "status", "priority", "start_date")
        return ("title", "status", "priority", "client", "start_date")

    def has_view_permission(self, request, obj=None):
        return True

    def has_change_permission(self, request, obj=None):
        if request.user.role == User.Role.ADMIN:
            return True
        if request.user.role == User.Role.CLIENT:
            return obj is not None and obj.client == request.user
        if request.user.role == User.Role.DEVELOPER:
            return obj is not None and request.user in obj.developers.all()
        return False


class FunctionInline(admin.StackedInline):
    model = Function
    extra = 1
    autocomplete_fields = ("developer",)

    def has_view_permission(self, request, obj=None):
        return True

    def has_edit_permission(self, request, obj=None):
        return False


@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ("project", "title", "status")
    list_filter = ("status", "project")
    autocomplete_fields = ("project",)
    inlines = [FunctionInline]

    def has_view_permission(self, request, obj=None):
        return True

    def has_edit_permission(self, request, obj=None):
        return False


@admin.register(Function)
class FunctionAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "status",
        "feature__project__title",
        "estimated_time",
        "cost",
    )
    list_filter = ("status", "feature__project__title")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.role == User.Role.ADMIN:
            return qs
        return qs.filter(developer=request.user)

    def has_view_permission(self, request, obj=None):
        return True

    def get_readonly_fields(self, request, obj=None):
        if obj is not None:
            return ["developer"]
        return []

    def has_change_permission(self, request, obj=None):
        if obj is not None:
            can_edit = (
                request.user == obj.developer or request.user.role == User.Role.ADMIN
            )
        return False


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("client", "amount", "status", "from_date", "to_date")
    list_filter = ("status", "from_date", "to_date")
    autocomplete_fields = ("client",)
