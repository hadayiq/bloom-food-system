import os
import pandas as pd
from openpyxl import load_workbook
from datetime import datetime


class ProductRepository:

    def __init__(self):
        self.file = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "inventory.xlsx"
        )

    def get_all_products(self):
        return pd.read_excel(self.file, sheet_name="Products")

    def get_product_names(self):
        df = self.get_all_products()
        return df["Product_Name"].dropna().astype(str).str.strip().tolist()

    def get_product_id(self, product_name):
        """Resolve a product by normalized display name."""
        if product_name is None:
            return None
        wanted = str(product_name).strip().casefold()
        if not wanted:
            return None
        df = self.get_all_products()
        names = df["Product_Name"].astype(str).str.strip().str.casefold()
        row = df[names == wanted]
        if row.empty:
            return None
        return row.iloc[0]["product_ID"]

    def get_opening_balance(self, product_id):
        df = pd.read_excel(self.file, sheet_name="Opening_Balance")
        row = df[df["Product_ID"] == product_id]
        if row.empty:
            return 0
        quantity = row.iloc[0]["Quantity"]
        if pd.isna(quantity):
            return 0
        return float(quantity)

    # =====================================
    # Add Product
    # =====================================
    def add_product(self, product_name, unit, opening_balance):
        workbook = load_workbook(self.file)
        products_sheet = workbook["Products"]
        opening_sheet = workbook["Opening_Balance"]
        last_row = products_sheet.max_row
        if last_row == 1:
            number = 1
        else:
            last_code = products_sheet.cell(row=last_row, column=1).value
            if last_code:
                number = int(last_code.replace("CR", "")) + 1
            else:
                number = 1
        product_id = f"CR{number:03d}"
        products_sheet.append([product_id, product_name, unit])
        opening_sheet.append([
            product_id,
            datetime.now().strftime("%Y-%m-%d"),
            opening_balance,
        ])
        workbook.save(self.file)
        from utils.refresh_manager import refresh_manager
        refresh_manager.products_changed.emit()

    def update_product(self, product_id, product_name, unit, opening_balance):
        workbook = load_workbook(self.file)
        products_sheet = workbook["Products"]
        opening_sheet = workbook["Opening_Balance"]
        for row in products_sheet.iter_rows(min_row=2):
            if row[0].value == product_id:
                row[1].value = product_name
                row[2].value = unit
                break
        for row in opening_sheet.iter_rows(min_row=2):
            if row[0].value == product_id:
                row[2].value = opening_balance
                break
        workbook.save(self.file)
        from utils.refresh_manager import refresh_manager
        refresh_manager.products_changed.emit()

    def delete_product(self, product_id):
        workbook = load_workbook(self.file)
        products_sheet = workbook["Products"]
        opening_sheet = workbook["Opening_Balance"]
        for row in range(2, products_sheet.max_row + 1):
            if products_sheet.cell(row=row, column=1).value == product_id:
                products_sheet.delete_rows(row)
                break
        for row in range(2, opening_sheet.max_row + 1):
            if opening_sheet.cell(row=row, column=1).value == product_id:
                opening_sheet.delete_rows(row)
                break
        workbook.save(self.file)
        from utils.refresh_manager import refresh_manager
        refresh_manager.products_changed.emit()

    def product_exists(self, product_name):
        return self.get_product_id(product_name) is not None
