from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from accounts.forms import LoginForm
from accounts.views import SignupView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("signup/", SignupView.as_view(), name="signup"),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="registration/login.html", authentication_form=LoginForm),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("", include("dashboard.urls")),
    path("accounts/", include("accounts.urls")),
    path("crm/", include("crm.urls")),
    path("finance/", include("finance.urls")),
    path("inventory/", include("inventory.urls")),
    path("sales/", include("sales.urls")),
    path("payroll/", include("payroll.urls")),
    path("purchasing/", include("purchasing.urls")),
]
