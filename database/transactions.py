import os
from datetime import datetime
from openpyxl import load_workbook

from database.products import ProductRepository
from database.batches import BatchRepository


class TransactionRepository:

    TRANSACTION_IN_TYPES = ["إنتاج", "مشتريات", "مردودات مبيعات", "مردودات تسليمات"]
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
        changed = False
        if sheet.max_column < 8:
            sheet.cell(1, 8).value = "Batch_Code"
            changed = True
        elif sheet.cell(1, 8).value != "Batch_Code":
            sheet.cell(1, sheet.max_column + 1).value = "Batch_Code"
            changed = True
        if changed:
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
        if product_id is None:
            raise ValueError("الصنف غير موجود.")

        if batch_code:
            if not self.batch_repo.get_batch(product_id, batch_code):
                raise ValueError("الباتش المختار غير موجود لهذا الصنف.")
            if transaction_type in self.TRANSACTION_OUT_TYPES and not self.check_stock(product, quantity, batch_code):
                raise ValueError("الكمية المطلوبة أكبر من رصيد الباتش المتاح.")
        elif transaction_type in self.TRANSACTION_OUT_TYPES and not self.check_stock(product, quantity):
            raise ValueError("الكمية المطلوبة أكبر من رصيد الصنف المتاح.")

        workbook = load_workbook(self.file)
        sheet = workbook["Transactions"]
        transaction_id = f"TR{sheet.max_row:05d}"
        now = datetime.now()
        sheet.append([transaction_id, now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S"), product, transaction_type, quantity, notes, batch_code or ""])
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
        """
        Return (opening, incoming, current_balance).

        Bloom inventory rule:
        - The product opening balance is the product-level opening.
        - Each batch opening balance is an additional opening quantity.
        - Batch transactions are counted only once.
        - Legacy transactions without a Batch_Code are counted at product level.
        """
        product_repo = ProductRepository()
        product_id = product_repo.get_product_id(product)
        if product_id is None:
            return 0.0, 0.0, 0.0

        batches = self.batch_repo.get_batches(product_id)
        if not batches:
            opening_balance = float(product_repo.get_opening_balance(product_id) or 0)
            transactions = self.get_transactions_by_product(product)
            total_in, total_out, balance = self._calculate(transactions, opening_balance)
            # Never expose a negative stock balance from the summary.
            return opening_balance, total_in, max(0.0, balance)

        # Batch opening quantities are additive to the product opening quantity
        # in this project by design.
        total_opening = float(product_repo.get_opening_balance(product_id) or 0)
        total_in = 0.0
        total_out = 0.0

        for batch in batches:
            batch_in, batch_out, _ = self.get_batch_balance(product, batch["code"])
            total_opening += max(0.0, float(batch["opening_balance"] or 0))
            total_in += max(0.0, float(batch_in or 0))
            total_out += max(0.0, float(batch_out or 0))

        # Older transactions may not have a Batch_Code. Count those at product
        # level, while batch-tagged transactions have already been counted above.
        legacy_transactions = self.get_transactions_by_product(product)
        for row in legacy_transactions:
            batch_code = row[7] if len(row) > 7 else None
            if batch_code:
                continue
            transaction_type = row[4]
            quantity = max(0.0, float(row[5] or 0))
            if transaction_type in self.TRANSACTION_IN_TYPES:
                total_in += quantity
            elif transaction_type in self.TRANSACTION_OUT_TYPES:
                total_out += quantity

        # Calculate the balance from the same totals shown in the summary.
        # This prevents a batch opening from being mistaken for negative
        # outgoing stock.
        balance = total_opening + total_in - total_out
        return total_opening, total_in, max(0.0, balance)

    def get_inventory_summary(self):
        product_repo = ProductRepository()
        products = product_repo.get_all_products()
        summary = []
        for _, row in products.iterrows():
            product_name = row["Product_Name"]
            total_opening, total_in, balance = self.get_product_balance(product_name)

            # Outgoing is a real movement total derived from the same opening,
            # incoming and current balance values. Never display it as negative.
            total_out = max(0.0, total_opening + total_in - balance)
            summary.append([
                product_name,
                total_opening,
                total_in,
                total_out,
                balance,
            ])
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

    def update_transaction(self, transaction_id, product, transaction_type, quantity, notes, batch_code=None):
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
                return {"id": row[0], "date": row[1], "time": row[2], "product": row[3], "type": row[4], "quantity": row[5], "notes": row[6], "batch": row[7] if len(row) > 7 else ""}
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
