from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

urlpatterns = [
    path("", include("apps.core.urls")),
    path("pessoas/", include("apps.people.urls")),
    path("financeiro/", include("apps.finance.urls", namespace="finance")),
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="core/login.html",
            redirect_authenticated_user=True,
        ),
        name="login",
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(next_page="/login/"),
        name="logout",
    ),
    path("admin/", admin.site.urls),
]