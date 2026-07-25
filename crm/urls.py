from django.urls import path

from . import views

app_name = "crm"

urlpatterns = [
    # Companies
    path("companies/", views.CompanyListView.as_view(), name="company_list"),
    path("companies/add/", views.CompanyCreateView.as_view(), name="company_create"),
    path("companies/<int:pk>/edit/", views.CompanyUpdateView.as_view(), name="company_edit"),
    path("companies/<int:pk>/delete/", views.CompanyDeleteView.as_view(), name="company_delete"),
    # Contacts
    path("contacts/", views.ContactListView.as_view(), name="contact_list"),
    path("contacts/add/", views.ContactCreateView.as_view(), name="contact_create"),
    path("contacts/<int:pk>/edit/", views.ContactUpdateView.as_view(), name="contact_edit"),
    path("contacts/<int:pk>/delete/", views.ContactDeleteView.as_view(), name="contact_delete"),
    # Pipeline stages
    path("stages/", views.PipelineStageListView.as_view(), name="stage_list"),
    path("stages/add/", views.PipelineStageCreateView.as_view(), name="stage_create"),
    path("stages/<int:pk>/edit/", views.PipelineStageUpdateView.as_view(), name="stage_edit"),
    path("stages/<int:pk>/delete/", views.PipelineStageDeleteView.as_view(), name="stage_delete"),
    # Deals
    path("deals/", views.DealBoardView.as_view(), name="deal_board"),
    path("deals/add/", views.DealCreateView.as_view(), name="deal_create"),
    path("deals/<int:pk>/edit/", views.DealUpdateView.as_view(), name="deal_edit"),
    path("deals/<int:pk>/delete/", views.DealDeleteView.as_view(), name="deal_delete"),
    path("deals/<int:pk>/move/", views.DealMoveStageView.as_view(), name="deal_move"),
    # Activities
    path("activities/", views.ActivityListView.as_view(), name="activity_list"),
    path("activities/add/", views.ActivityCreateView.as_view(), name="activity_create"),
    path("activities/<int:pk>/edit/", views.ActivityUpdateView.as_view(), name="activity_edit"),
    path("activities/<int:pk>/delete/", views.ActivityDeleteView.as_view(), name="activity_delete"),
]
