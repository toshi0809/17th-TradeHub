from django.urls import path

from . import views

app_name = "goods_receipts"

urlpatterns = [
    path("", views.index, name="index"),
    path("new", views.new, name="new"),
    path("show/<int:id>", views.show, name="show"),
    path("edit/<int:id>", views.edit, name="edit"),
    path("delete/<int:id>", views.delete, name="delete"),
    path("load_supplier_info/", views.load_supplier_info, name="load_supplier_info"),
    path("load_product_info/", views.load_product_info, name="load_product_info"),
    path("stocked/<int:id>", views.stocked, name="stocked"),
    path("export_csv", views.export_csv, name="export_csv"),
    path("export_excel", views.export_excel, name="export_excel"),
]
