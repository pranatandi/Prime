from django.urls import path

from . import views

app_name = "purchasing"

urlpatterns = [
    path("vendors/", views.VendorListView.as_view(), name="vendor_list"),
    path("vendors/add/", views.VendorCreateView.as_view(), name="vendor_create"),
    path("vendors/export/", views.VendorExportView.as_view(), name="vendor_export"),
    path("vendors/<int:pk>/edit/", views.VendorUpdateView.as_view(), name="vendor_edit"),
    path("vendors/<int:pk>/delete/", views.VendorDeleteView.as_view(), name="vendor_delete"),

    path("orders/", views.PurchaseOrderListView.as_view(), name="purchaseorder_list"),
    path("orders/add/", views.PurchaseOrderCreateView.as_view(), name="purchaseorder_create"),
    path("orders/export/", views.PurchaseOrderExportView.as_view(), name="purchaseorder_export"),
    path("orders/<int:pk>/edit/", views.PurchaseOrderUpdateView.as_view(), name="purchaseorder_edit"),
    path("orders/<int:pk>/delete/", views.PurchaseOrderDeleteView.as_view(), name="purchaseorder_delete"),
]
