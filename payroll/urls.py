from django.urls import path

from . import views

app_name = "payroll"

urlpatterns = [
    path("employees/", views.EmployeeListView.as_view(), name="employee_list"),
    path("employees/add/", views.EmployeeCreateView.as_view(), name="employee_create"),
    path("employees/export/", views.EmployeeExportView.as_view(), name="employee_export"),
    path("employees/<int:pk>/edit/", views.EmployeeUpdateView.as_view(), name="employee_edit"),
    path("employees/<int:pk>/delete/", views.EmployeeDeleteView.as_view(), name="employee_delete"),

    path("runs/", views.PayrollRunListView.as_view(), name="payrollrun_list"),
    path("runs/add/", views.PayrollRunCreateView.as_view(), name="payrollrun_create"),
    path("runs/<int:pk>/", views.PayrollRunDetailView.as_view(), name="payrollrun_detail"),
    path("runs/<int:pk>/edit/", views.PayrollRunUpdateView.as_view(), name="payrollrun_edit"),
    path("runs/<int:pk>/delete/", views.PayrollRunDeleteView.as_view(), name="payrollrun_delete"),
    path("runs/<int:pk>/process/", views.PayrollRunProcessView.as_view(), name="payrollrun_process"),
]
