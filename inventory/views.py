from core.views import (
    GenericTenantCreateView,
    GenericTenantDeleteView,
    GenericTenantListView,
    GenericTenantUpdateView,
    TenantCSVExportView,
)
from .forms import ProductForm, WarehouseForm
from .models import Product, StockMovement, Warehouse


# ---- Warehouse ----

class WarehouseListView(GenericTenantListView):
    model = Warehouse
    title = "Warehouses"
    url_basename = "inventory:warehouse"
    list_fields = [("Nama", "name"), ("Alamat", "address"), ("Default?", "is_default")]


class WarehouseCreateView(GenericTenantCreateView):
    model = Warehouse
    form_class = WarehouseForm
    title = "Warehouse"
    url_basename = "inventory:warehouse"


class WarehouseUpdateView(GenericTenantUpdateView):
    model = Warehouse
    form_class = WarehouseForm
    title = "Warehouse"
    url_basename = "inventory:warehouse"


class WarehouseDeleteView(GenericTenantDeleteView):
    model = Warehouse
    title = "Warehouse"
    url_basename = "inventory:warehouse"


# ---- Product ----

class ProductListView(GenericTenantListView):
    model = Product
    title = "Products"
    url_basename = "inventory:product"
    has_export = True
    list_fields = [
        ("SKU", "sku"), ("Nama", "name"), ("Unit", "unit"), ("Harga Jual", "sell_price"),
        ("Stok", "total_stock"), ("Aktif", "is_active"),
    ]


class ProductCreateView(GenericTenantCreateView):
    model = Product
    form_class = ProductForm
    title = "Product"
    url_basename = "inventory:product"


class ProductUpdateView(GenericTenantUpdateView):
    model = Product
    form_class = ProductForm
    title = "Product"
    url_basename = "inventory:product"


class ProductDeleteView(GenericTenantDeleteView):
    model = Product
    title = "Product"
    url_basename = "inventory:product"


class ProductExportView(TenantCSVExportView):
    model = Product
    filename = "products"
    export_fields = [
        ("SKU", "sku"), ("Nama", "name"), ("Unit", "unit"), ("Harga Pokok", "cost_price"),
        ("Harga Jual", "sell_price"), ("Stok", "total_stock"), ("Aktif", "is_active"),
    ]


# ---- Stock Movements (read-only ledger) ----

class StockMovementListView(GenericTenantListView):
    model = StockMovement
    title = "Stock Movements"
    url_basename = "inventory:stockmovement"
    readonly = True
    list_fields = [
        ("Tanggal", "date"), ("Produk", "product"), ("Gudang", "warehouse"),
        ("Tipe", "get_movement_type_display"), ("Jumlah", "quantity"), ("Referensi", "reference"),
    ]

    def get_queryset(self):
        return super().get_queryset().select_related("product", "warehouse")
