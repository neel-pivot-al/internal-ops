from django.urls import path
from knox import views as knox_views

from authentication.views import LoginView

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", knox_views.LogoutView.as_view(), name="logout"),
    path("logoutall/", knox_views.LogoutAllView.as_view(), name="logoutall"),
]
