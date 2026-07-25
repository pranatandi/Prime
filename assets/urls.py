from django.urls import path

from . import views

app_name = "assets"

urlpatterns = [
    path("", views.FixedAssetListView.as_view(), name="fixedasset_list"),
    path("add/", views.FixedAssetCreateView.as_view(), name="fixedasset_create"),
    path("export/", views.FixedAssetExportView.as_view(), name="fixedasset_export"),
    path("run-depreciation/", views.FixedAssetRunDepreciationAllView.as_view(), name="fixedasset_run_depreciation"),
    path("<int:pk>/", views.FixedAssetDetailView.as_view(), name="fixedasset_detail"),
    path("<int:pk>/edit/", views.FixedAssetUpdateView.as_view(), name="fixedasset_edit"),
    path("<int:pk>/delete/", views.FixedAssetDeleteView.as_view(), name="fixedasset_delete"),
    path("<int:pk>/post-depreciation/", views.FixedAssetPostDepreciationView.as_view(), name="fixedasset_post_depreciation"),
    path("<int:pk>/dispose/", views.FixedAssetDisposeView.as_view(), name="fixedasset_dispose"),
]
