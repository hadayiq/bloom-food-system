import os
from datetime import datetime
from openpyxl import load_workbook

from database.products import ProductRepository


class TransactionRepository:

    def __init__(self):
        self.file = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "inventory.xlsx"
        )

    def save_transaction(self, product, transaction_type, quantity, notes):

        workbook = load_workbook(self.file)
        sheet = workbook["Transactions"]

        transaction_id = f"TR{sheet.max_row:05d}"

        now = datetime.now()

        sheet.append(
            [
                transaction_id,
                now.strftime("%Y-%m-%d"),
                now.strftime("%H:%M:%S"),
                product,
                transaction_type,
                quantity,
                notes,
            ]
        )

        workbook.save(self.file)

    def get_transactions_by_product(self, product):

        workbook = load_workbook(self.file)
        sheet = workbook["Transactions"]

        transactions = []

        for row in sheet.iter_rows(min_row=2, values_only=True):

            if row[3] == product:

                transactions.append(row)

        return transactions

    def get_product_balance(self, product):

        product_repo = ProductRepository()

        product_id = product_repo.get_product_id(product)

        opening_balance = product_repo.get_opening_balance(product_id)

        transactions = self.get_transactions_by_product(product)

        total_in = 0
        total_out = 0

        for row in transactions:

            transaction_type = row[4]
            quantity = float(row[5])

            if transaction_type in ["إنتاج", "مشتريات", "مردودات مبيعات"]:
                total_in += quantity

            elif transaction_type in ["صرف للتجزئة", "صرف للتسليمات"]:
                total_out += quantity

        balance = opening_balance + total_in - total_out

        return total_in, total_out, balance

    def get_inventory_summary(self):

        product_repo = ProductRepository()

        products = product_repo.get_all_products()

        summary = []

        for _, row in products.iterrows():

            product_name = row["Product_Name"]

            product_id = row["product_ID"]

            opening_balance = product_repo.get_opening_balance(product_id)

            total_in, total_out, balance = self.get_product_balance(product_name)

            summary.append(
                [product_name, opening_balance, total_in, total_out, balance]
            )

        return summary

    def check_stock(self, product, requested_quantity):

        _, _, balance = self.get_product_balance(product)

        return balance >= requested_quantity

    # =====================================
    # Update Transaction
    # =====================================

    def update_transaction(
        self,
        transaction_id,
        product,
        transaction_type,
        quantity,
        notes,
    ):

        workbook = load_workbook(self.file)

        sheet = workbook["Transactions"]

        for row in sheet.iter_rows(min_row=2):

            if row[0].value == transaction_id:

                row[3].value = product
                row[4].value = transaction_type
                row[5].value = quantity
                row[6].value = notes

                break

        workbook.save(self.file)
        # تحديث كل الشاشات

        from utils.refresh_manager import refresh_manager

        refresh_manager.data_changed.emit()

    # =====================================
    # Get Transaction By ID
    # =====================================

    def get_transaction_by_id(self, transaction_id):

        workbook = load_workbook(self.file)

        sheet = workbook["Transactions"]

        for row in sheet.iter_rows(min_row=2, values_only=True):

            if row[0] == transaction_id:

                return {
                    "id": row[0],
                    "date": row[1],
                    "time": row[2],
                    "product": row[3],
                    "type": row[4],
                    "quantity": row[5],
                    "notes": row[6],
                }

        return None

    def delete_transaction(self, transaction_id):

        print("DELETE FUNCTION CALLED")

        workbook = load_workbook(self.file)

        sheet = workbook["Transactions"]

        for row in range(2, sheet.max_row + 1):

            if sheet.cell(row=row, column=1).value == transaction_id:

                sheet.delete_rows(row)

                break

        workbook.save(self.file)
        from utils.refresh_manager import refresh_manager

        refresh_manager.data_changed.emit()

        print("DELETE DONE")

    def product_has_transactions(self, product_name):

        workbook = load_workbook(self.file)

        sheet = workbook["Transactions"]

        for row in sheet.iter_rows(min_row=2, values_only=True):

            if row[3] == product_name:
                return True

        return False
