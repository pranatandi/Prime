from django.urls import path

from . import views

app_name = "inventory"

urlpatterns = [
    path("warehouses/", views.WarehouseListView.as_view(), name="warehouse_list"),
    path("warehouses/add/", views.WarehouseCreateView.as_view(), name="warehouse_create"),
    path("warehouses/<int:pk>/edit/", views.WarehouseUpdateView.as_view(), name="warehouse_edit"),
    path("warehouses/<int:pk>/delete/", views.WarehouseDeleteView.as_view(), name="warehouse_delete"),

    path("products/", views.ProductListView.as_view(), name="product_list"),
    path("products/add/", views.ProductCreateView.as_view(), name="product_create"),
    path("products/export/", views.ProductExportView.as_view(), name="product_export"),
    path("products/<int:pk>/edit/", views.ProductUpdateView.as_view(), name="product_edit"),
    path("products/<int:pk>/delete/", views.ProductDeleteView.as_view(), name="product_delete"),

    path("stock-movements/", views.StockMovementListView.as_view(), name="stockmovement_list"),
]
