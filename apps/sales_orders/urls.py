from django.urls import path

from . import views

app_name = "sales_orders"

urlpatterns = [
    path("", views.index, name="index"),
    path("new/", views.new, name="new"),
    path("edit/<int:id>/", views.edit, name="edit"),
    path("delete/<int:id>/", views.delete, name="delete"),
    path("export_csv", views.export_csv, name="export_csv"),
    path("export_excel", views.export_excel, name="export_excel"),
    path("transform/<int:id>", views.transform, name="transform"),
]
