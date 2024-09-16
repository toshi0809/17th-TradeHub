import csv
from datetime import datetime

import pandas as pd
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from apps.products.models import Product
from apps.suppliers.models import Supplier

from .forms.inventory_form import FileUploadForm, RestockForm
from .models import Inventory


def index(request):
    state = request.GET.get("select")
    order_by = request.GET.get("sort", "id")
    is_desc = request.GET.get("desc", "True") == "False"
    state_match = {"normal", "low_stock", "out_stock"}

    inventory = Inventory.objects.order_by(order_by)

    if state in state_match:
        inventory = Inventory.objects.filter(state=state)
    order_by_field = order_by if is_desc else "-" + order_by
    inventory = inventory.order_by(order_by_field)

    paginator = Paginator(inventory, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    content = {
        "inventory": page_obj,
        "selected_state": state,
        "is_desc": is_desc,
        "order_by": order_by,
        "page_obj": page_obj,
    }

    return render(request, "inventory/index.html", content)


def new(request):
    if request.method == "POST":
        form = RestockForm(request.POST)
        if form.is_valid():
            form.save().update_state()
            return redirect("inventory:index")
        else:
            return render(request, "inventory/new.html", {"form": form})
    form = RestockForm()
    return render(request, "inventory/new.html", {"form": form})


def edit(request, id):
    inventory = get_object_or_404(Inventory, id=id)
    if request.method == "POST":
        form = RestockForm(request.POST, instance=inventory)
        print(form.errors)
        if form.is_valid():
            form.save().update_state()
            return redirect("inventory:index")
        else:
            print(form.errors)
    else:
        form = RestockForm(instance=inventory)

    return render(
        request, "inventory/edit.html", {"inventory": inventory, "form": form}
    )


def delete(request, id):
    inventory = get_object_or_404(Inventory, id=id)
    inventory.delete()
    return redirect("inventory:index")


def import_file(request):
    if request.method == "POST":
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES["file"]
            if file.name.endswith(".csv"):

                decoded_file = file.read().decode("utf-8").splitlines()
                reader = csv.reader(decoded_file)
                next(reader)  # Skip header row

                for row in reader:
                    if len(row) < 5:
                        # messages.error(request, f"CSV 数据不完整，跳过该行: {row}") 很奇怪?
                        # IndexError: list index out of range
                        continue
                    try:
                        product = Product.objects.get(id=row[0])
                        supplier = Supplier.objects.get(id=row[1])
                        Inventory.objects.create(
                            product=product,
                            supplier=supplier,
                            quantity=row[2],
                            safety_stock=row[3],
                            note=row[4],
                        )
                    except (Product.DoesNotExist, Supplier.DoesNotExist) as e:
                        messages.error(request, f"匯入失敗，找不到客戶或產品: {e}")
                        return redirect("inventory:index")

                messages.success(request, "成功匯入 CSV")
                return redirect("inventory:index")

            elif file.name.endswith(".xlsx"):
                df = pd.read_excel(file)
                df.rename(
                    columns={
                        "產品": "product",
                        "供應商": "supplier",
                        "數量": "quantity",
                        "安全水位": "safety_stock",
                        "備註": "note",
                    },
                    inplace=True,
                )
                for _, row in df.iterrows():
                    try:
                        product = Product.objects.get(id=int(row["product"]))
                        supplier = Supplier.objects.get(id=int(row["supplier"]))
                        Inventory.objects.create(
                            product=product,
                            supplier=supplier,
                            quantity=str(row["quantity"]),
                            safety_stock=str(row["safety_stock"]),
                            note=str(row["note"]) if not pd.isna(row["note"]) else "",
                        )
                    except (Product.DoesNotExist, Supplier.DoesNotExist) as e:
                        messages.error(request, f"匯入失敗，找不到客戶或產品: {e}")
                        return redirect("inventory:index")
                messages.success(request, "成功匯入 Excel")
                return redirect("inventory:index")

            else:
                messages.error(request, "匯入失敗(檔案不是 CSV 或 Excel)")
                return render(request, "layouts/import.html", {"form": form})

    form = FileUploadForm()
    return render(request, "layouts/import.html", {"form": form})


def export_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="Inventory.csv"'

    writer = csv.writer(response)
    writer.writerow(
        [
            "產品",
            "供應商",
            "數量",
            "安全水位",
            "最後更新",
            "備註",
        ]
    )

    inventorys = Inventory.objects.all()
    for inventory in inventorys:
        writer.writerow(
            [
                inventory.product,
                inventory.supplier,
                inventory.quantity,
                inventory.safety_stock,
                inventory.last_updated,
                inventory.note,
            ]
        )

    return response


def export_excel(request):
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = "attachment; filename=Inventory.xlsx"

    inventory = Inventory.objects.select_related("product", "supplier").values(
        "product__product_name",
        "supplier__name",
        "quantity",
        "safety_stock",
        "last_updated",
        "note",
    )

    df = pd.DataFrame(inventory)
    for col in df.select_dtypes(include=["datetime64[ns, UTC]"]).columns:
        df[col] = df[col].dt.strftime("%Y-%m-%d %H:%M:%S")

    column_mapping = {
        "product__product_name": "產品",
        "supplier__name": "供應商",
        "quantity": "數量",
        "safety_stock": "安全水位",
        "last_updated": "最後更新",
        "note": "備註",
    }

    df.rename(columns=column_mapping, inplace=True)

    with pd.ExcelWriter(response, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Inventory")
    return response
