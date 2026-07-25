from django.urls import path

from . import views

app_name = "sales"

urlpatterns = [
    path("orders/", views.SalesOrderListView.as_view(), name="salesorder_list"),
    path("orders/add/", views.SalesOrderCreateView.as_view(), name="salesorder_create"),
    path("orders/<int:pk>/", views.SalesOrderDetailView.as_view(), name="salesorder_detail"),
    path("orders/<int:pk>/edit/", views.SalesOrderUpdateView.as_view(), name="salesorder_edit"),
    path("orders/<int:pk>/delete/", views.SalesOrderDeleteView.as_view(), name="salesorder_delete"),
    path("orders/<int:pk>/deliver/", views.SalesOrderDeliverView.as_view(), name="salesorder_deliver"),
    path("orders/<int:pk>/create-invoice/", views.SalesOrderCreateInvoiceView.as_view(), name="salesorder_create_invoice"),
]
