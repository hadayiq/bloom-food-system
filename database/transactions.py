import os
from datetime import datetime
from openpyxl import load_workbook

from database.products import ProductRepository
from database.batches import BatchRepository


class TransactionRepository:

    TRANSACTION_IN_TYPES = ["إنتاج", "مشتريات", "مردودات مبيعات"]
    TRANSACTION_OUT_TYPES = ["صرف للتجزئة", "صرف للتسليمات"]

    def __init__(self):
        self.file = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "inventory.xlsx"
        )
        self.batch_repo = BatchRepository()
        self._ensure_batch_column()

    def _ensure_batch_column(self):
        workbook = load_workbook(self.file)
        sheet = workbook["Transactions"]
        if sheet.max_column < 8:
            sheet.cell(1, 8).value = "Batch_Code"
        elif sheet.cell(1, 8).value != "Batch_Code":
            # Keep existing columns intact and only add the batch field at the end.
            sheet.cell(1, sheet.max_column + 1).value = "Batch_Code"
        workbook.save(self.file)
        workbook.close()

    def _transaction_batch(self, row):
        return row[7] if len(row) > 7 else None

    def save_transaction(self, product, transaction_type, quantity, notes, batch_code=None):
        quantity = float(quantity)
        if quantity < 0:
            raise ValueError("الكمية لا يمكن أن تكون سالبة.")
        if quantity == 0:
            raise ValueError("الكمية يجب أن تكون أكبر من صفر.")

        product_repo = ProductRepository()
        product_id = product_repo.get_product_id(product)

        if batch_code:
            if not self.batch_repo.get_batch(product_id, batch_code):
                raise ValueError("الباتش المختار غير موجود لهذا الصنف.")
            if transaction_type in self.TRANSACTION_OUT_TYPES and not self.check_stock(
                product, quantity, batch_code
            ):
                raise ValueError("الكمية المطلوبة أكبر من رصيد الباتش المتاح.")
        elif transaction_type in self.TRANSACTION_OUT_TYPES and not self.check_stock(product, quantity):
            raise ValueError("الكمية المطلوبة أكبر من رصيد الصنف المتاح.")

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
                batch_code or "",
            ]
        )

        workbook.save(self.file)
        workbook.close()

    def get_transactions_by_product(self, product, batch_code=None):
        workbook = load_workbook(self.file, data_only=True)
        sheet = workbook["Transactions"]
        transactions = []

        for row in sheet.iter_rows(min_row=2, values_only=True):
            if row[3] != product:
                continue
            if batch_code is not None and (len(row) < 8 or row[7] != batch_code):
                continue
            transactions.append(row)

        workbook.close()
        return transactions

    def _calculate(self, transactions, opening_balance):
        total_in = 0.0
        total_out = 0.0

        for row in transactions:
            transaction_type = row[4]
            quantity = float(row[5] or 0)

            if transaction_type in self.TRANSACTION_IN_TYPES:
                total_in += quantity
            elif transaction_type in self.TRANSACTION_OUT_TYPES:
                total_out += quantity

        balance = float(opening_balance) + total_in - total_out
        return total_in, total_out, balance

    def get_batch_balance(self, product, batch_code):
        product_repo = ProductRepository()
        product_id = product_repo.get_product_id(product)
        if product_id is None:
            return 0.0, 0.0, 0.0

        opening = self.batch_repo.get_opening_balance(product_id, batch_code)
        transactions = self.get_transactions_by_product(product, batch_code)
        return self._calculate(transactions, opening)

    def get_product_balance(self, product):
        product_repo = ProductRepository()
        product_id = product_repo.get_product_id(product)
        if product_id is None:
            return 0.0, 0.0, 0.0

        batches = self.batch_repo.get_batches(product_id)

        # Once batches exist for a product, their opening balances become the
        # source of truth for the product opening stock. Legacy transactions
        # without a batch are still included so old data is not lost.
        if batches:
            total_in = 0.0
            total_out = 0.0

            for batch in batches:
                batch_in, batch_out, _ = self.get_batch_balance(product, batch["code"])
                total_in += batch_in + batch["opening_balance"]
                total_out += batch_out

            legacy_transactions = self.get_transactions_by_product(product)
            for row in legacy_transactions:
                if len(row) >= 8 and row[7]:
                    continue
                transaction_type = row[4]
                quantity = float(row[5] or 0)
                if transaction_type in self.TRANSACTION_IN_TYPES:
                    total_in += quantity
                elif transaction_type in self.TRANSACTION_OUT_TYPES:
                    total_out += quantity

            return total_in, total_out, total_in - total_out

        opening_balance = product_repo.get_opening_balance(product_id)
        transactions = self.get_transactions_by_product(product)
        return self._calculate(transactions, opening_balance)

    def get_inventory_summary(self):
        product_repo = ProductRepository()
        products = product_repo.get_all_products()
        summary = []

        for _, row in products.iterrows():
            product_name = row["Product_Name"]
            product_id = row["product_ID"]
            opening_balance = product_repo.get_opening_balance(product_id)
            total_in, total_out, balance = self.get_product_balance(product_name)
            summary.append([product_name, opening_balance, total_in, total_out, balance])

        return summary

    def check_stock(self, product, requested_quantity, batch_code=None):
        requested_quantity = float(requested_quantity)
        if requested_quantity < 0:
            return False

        if batch_code:
            _, _, balance = self.get_batch_balance(product, batch_code)
        else:
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
        batch_code=None,
    ):
        quantity = float(quantity)
        if quantity < 0 or quantity == 0:
            raise ValueError("الكمية يجب أن تكون أكبر من صفر.")

        workbook = load_workbook(self.file)
        sheet = workbook["Transactions"]

        for row in sheet.iter_rows(min_row=2):
            if row[0].value == transaction_id:
                row[3].value = product
                row[4].value = transaction_type
                row[5].value = quantity
                row[6].value = notes
                if sheet.max_column < 8:
                    sheet.cell(1, 8).value = "Batch_Code"
                sheet.cell(row=row[0].row, column=8).value = batch_code or ""
                break

        workbook.save(self.file)
        workbook.close()

        from utils.refresh_manager import refresh_manager
        refresh_manager.data_changed.emit()

    def get_transaction_by_id(self, transaction_id):
        workbook = load_workbook(self.file, data_only=True)
        sheet = workbook["Transactions"]

        for row in sheet.iter_rows(min_row=2, values_only=True):
            if row[0] == transaction_id:
                workbook.close()
                return {
                    "id": row[0],
                    "date": row[1],
                    "time": row[2],
                    "product": row[3],
                    "type": row[4],
                    "quantity": row[5],
                    "notes": row[6],
                    "batch": row[7] if len(row) > 7 else "",
                }

        workbook.close()
        return None

    def delete_transaction(self, transaction_id):
        workbook = load_workbook(self.file)
        sheet = workbook["Transactions"]

        for row in range(2, sheet.max_row + 1):
            if sheet.cell(row=row, column=1).value == transaction_id:
                sheet.delete_rows(row)
                break

        workbook.save(self.file)
        workbook.close()

        from utils.refresh_manager import refresh_manager
        refresh_manager.data_changed.emit()

    def product_has_transactions(self, product_name):
        workbook = load_workbook(self.file, data_only=True)
        sheet = workbook["Transactions"]

        for row in sheet.iter_rows(min_row=2, values_only=True):
            if row[3] == product_name:
                workbook.close()
                return True

        workbook.close()
        return False
