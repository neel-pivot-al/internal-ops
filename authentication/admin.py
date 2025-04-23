from typing import Any

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.http import HttpRequest

# Register your models here.
from .models import Skill, User


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "id",
        "username",
        "first_name",
        "last_name",
        "email",
        "is_staff",
        "is_active",
        "date_joined",
    )
    list_filter = ("role",)
    search_fields = ("email", "first_name", "last_name")
    ordering = ("first_name",)
    autocomplete_fields = ("skills",)

    def get_fieldsets(self, request, obj=None):
        if obj is None:
            return super().get_fieldsets(request, obj)
        fieldsets = (
            (None, {"fields": ("username", "password")}),
            ("Personal info", {"fields": ("first_name", "last_name", "email", "role")}),
            ("Important dates", {"fields": ("last_login", "date_joined")}),
            ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser")}),
        )
        if obj.role == User.Role.DEVELOPER:
            fieldsets = fieldsets + (("Skills", {"fields": ("skills", "time_zone")}),)
            fieldsets = (
                (None, {"fields": ("username", "password")}),
                (
                    "Personal info",
                    {"fields": ("first_name", "last_name", "email", "role")},
                ),
                ("Skills", {"fields": ("skills", "time_zone")}),
                ("Important dates", {"fields": ("last_login", "date_joined")}),
                ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser")}),
            )
        return fieldsets

    # def get_autocomplete_fields(self, request: HttpRequest) -> tuple[Any, ...]:
    #     if request.user.role == User.Role.DEVELOPER:
    #         return ("skills", "time_zone")
    #     return ()

    def has_view_permission(self, request, obj=None):
        return request.user.role == User.Role.ADMIN

    def has_change_permission(self, request, obj=None):
        return request.user.role == User.Role.ADMIN

    def has_delete_permission(self, request, obj=None):
        return request.user.role == User.Role.ADMIN


admin.site.unregister(Group)
