from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied

from authentication.models import User
from authentication.serializers import UserSerializer
from core.permissions import IsAdmin


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    search_fields = ["username", "email"]
    ordering_fields = ["username", "email"]
    filterset_fields = ["role"]

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            user = self.get_object()
            if user != self.request.user and self.request.user.role != User.Role.ADMIN:
                raise PermissionDenied("You are not allowed to perform this action.")
        return super().get_permissions()
