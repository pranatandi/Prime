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
    path("orders/<int:pk>/", views.PurchaseOrderDetailView.as_view(), name="purchaseorder_detail"),
    path("orders/<int:pk>/edit/", views.PurchaseOrderUpdateView.as_view(), name="purchaseorder_edit"),
    path("orders/<int:pk>/delete/", views.PurchaseOrderDeleteView.as_view(), name="purchaseorder_delete"),
    path("orders/<int:pk>/receive/", views.PurchaseOrderReceiveView.as_view(), name="purchaseorder_receive"),
    path("orders/<int:pk>/create-bill/", views.PurchaseOrderCreateBillView.as_view(), name="purchaseorder_create_bill"),

    path("bills/", views.BillListView.as_view(), name="bill_list"),
    path("bills/add/", views.BillCreateView.as_view(), name="bill_create"),
    path("bills/export/", views.BillExportView.as_view(), name="bill_export"),
    path("bills/<int:pk>/edit/", views.BillUpdateView.as_view(), name="bill_edit"),
    path("bills/<int:pk>/delete/", views.BillDeleteView.as_view(), name="bill_delete"),
]
