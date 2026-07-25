from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.DashboardView.as_view(), name="index"),
    path("reports/sales/", views.SalesReportView.as_view(), name="sales_report"),
    path("reports/finance/", views.FinancialReportView.as_view(), name="financial_report"),
    path("search/", views.GlobalSearchView.as_view(), name="search"),
]
