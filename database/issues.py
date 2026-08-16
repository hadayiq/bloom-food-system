import os
from datetime import datetime

from openpyxl import load_workbook

from database.products import ProductRepository
from database.batches import BatchRepository
from database.transactions import TransactionRepository


class IssueRepository:
    """Issue vouchers: one voucher can contain many product/batch lines."""

    HEADERS = [
        "Issue_No",
        "Issue_Date",
        "Representative",
        "Status",
    ]
    LINE_HEADERS = [
        "Issue_No",
        "Line_No",
        "Product",
        "Batch_Code",
        "Expiry_Date",
        "Quantity",
    ]
    STOCK_HEADERS = [
        "Representative",
        "Product",
        "Batch_Code",
        "Quantity",
        "Updated_At",
    ]

    def __init__(self):
        self.file = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "inventory.xlsx"
        )
        self.product_repo = ProductRepository()
        self.batch_repo = BatchRepository()
        self.transaction_repo = TransactionRepository()
        self._ensure_sheets()

    def _ensure_sheets(self):
        workbook = load_workbook(self.file)
        changed = False
        for name, headers in [
            ("Issue_Headers", self.HEADERS),
            ("Issue_Lines", self.LINE_HEADERS),
            ("Subwarehouse_Stock", self.STOCK_HEADERS),
        ]:
            if name not in workbook.sheetnames:
                sheet = workbook.create_sheet(name)
                sheet.append(headers)
                changed = True
            else:
                sheet = workbook[name]
                if sheet.max_row == 1 and all(
                    sheet.cell(1, i + 1).value is None for i in range(len(headers))
                ):
                    for i, header in enumerate(headers, start=1):
                        sheet.cell(1, i).value = header
                    changed = True
        if changed:
            workbook.save(self.file)
        workbook.close()

    def get_next_issue_no(self):
        workbook = load_workbook(self.file, data_only=True)
        sheet = workbook["Issue_Headers"]
        max_number = 0
        for row in sheet.iter_rows(min_row=2, values_only=True):
            value = row[0]
            try:
                max_number = max(max_number, int(str(value).strip()))
            except (TypeError, ValueError):
                continue
        workbook.close()
        return f"{max_number + 1:06d}"

    def issue_exists(self, issue_no):
        workbook = load_workbook(self.file, data_only=True)
        sheet = workbook["Issue_Headers"]
        exists = any(
            str(row[0]).strip() == str(issue_no).strip()
            for row in sheet.iter_rows(min_row=2, values_only=True)
            if row[0] is not None
        )
        workbook.close()
        return exists

    def save_issue(self, issue_no, representative, lines):
        issue_no = str(issue_no).strip()
        representative = str(representative).strip()
        if not issue_no:
            raise ValueError("رقم الإذن مطلوب.")
        if self.issue_exists(issue_no):
            raise ValueError("رقم الإذن موجود بالفعل.")
        if not representative:
            raise ValueError("اسم المندوب / العميل مطلوب.")
        if not lines:
            raise ValueError("يجب إدخال كمية واحدة على الأقل.")

        # Normalize and validate all lines before changing the workbook.
        normalized = []
        for line in lines:
            product = str(line.get("product", "")).strip()
            batch_code = str(line.get("batch_code", "")).strip()
            quantity = float(line.get("quantity", 0) or 0)
            if not product or quantity <= 0:
                continue

            product_id = self.product_repo.get_product_id(product)
            if product_id is None:
                raise ValueError(f"الصنف غير موجود: {product}")

            batch = None
            if batch_code:
                batch = self.batch_repo.get_batch(product_id, batch_code)
                if not batch:
                    raise ValueError(f"الباتش {batch_code} غير موجود للصنف {product}.")
            else:
                batches = self.batch_repo.get_batches(product_id)
                if batches:
                    raise ValueError(f"يجب اختيار باتش للصنف: {product}")

            if not self.transaction_repo.check_stock(product, quantity, batch_code or None):
                target = f"الباتش {batch_code}" if batch_code else "الصنف"
                raise ValueError(f"الكمية المطلوبة أكبر من رصيد {target}: {product}")

            normalized.append(
                {
                    "product": product,
                    "batch_code": batch_code,
                    "expiry_date": batch["expiry_date"] if batch else "",
                    "quantity": quantity,
                }
            )

        if not normalized:
            raise ValueError("يجب إدخال كمية واحدة على الأقل.")

        workbook = load_workbook(self.file)
        headers = workbook["Issue_Headers"]
        lines_sheet = workbook["Issue_Lines"]
        stock_sheet = workbook["Subwarehouse_Stock"]
        now = datetime.now()

        headers.append([issue_no, now.strftime("%Y-%m-%d"), representative, "مفتوح"])

        for index, line in enumerate(normalized, start=1):
            lines_sheet.append(
                [
                    issue_no,
                    index,
                    line["product"],
                    line["batch_code"],
                    line["expiry_date"],
                    line["quantity"],
                ]
            )

            # Main warehouse movement: the existing transaction ledger remains
            # the source used by current inventory calculations.
            transactions = workbook["Transactions"]
            transaction_id = f"TR{transactions.max_row:05d}"
            transactions.append(
                [
                    transaction_id,
                    now.strftime("%Y-%m-%d"),
                    now.strftime("%H:%M:%S"),
                    line["product"],
                    "صرف للتسليمات",
                    line["quantity"],
                    f"إذن صرف {issue_no} - {representative}",
                    line["batch_code"],
                ]
            )

            # Add the same quantity to the representative's subwarehouse.
            existing_row = None
            for row in range(2, stock_sheet.max_row + 1):
                if (
                    str(stock_sheet.cell(row, 1).value).strip() == representative
                    and str(stock_sheet.cell(row, 2).value).strip() == line["product"]
                    and str(stock_sheet.cell(row, 3).value or "").strip().lower()
                    == line["batch_code"].lower()
                ):
                    existing_row = row
                    break

            if existing_row is None:
                stock_sheet.append(
                    [
                        representative,
                        line["product"],
                        line["batch_code"],
                        line["quantity"],
                        now.strftime("%Y-%m-%d %H:%M:%S"),
                    ]
                )
            else:
                current = float(stock_sheet.cell(existing_row, 4).value or 0)
                stock_sheet.cell(existing_row, 4).value = current + line["quantity"]
                stock_sheet.cell(existing_row, 5).value = now.strftime("%Y-%m-%d %H:%M:%S")

        workbook.save(self.file)
        workbook.close()
        return issue_no

    def get_open_issues(self):
        workbook = load_workbook(self.file, data_only=True)
        headers = workbook["Issue_Headers"]
        result = []
        for row in headers.iter_rows(min_row=2, values_only=True):
            if not row[0]:
                continue
            if str(row[3] or "مفتوح") != "مغلق":
                result.append({
                    "issue_no": str(row[0]),
                    "date": row[1],
                    "representative": row[2],
                    "status": row[3] or "مفتوح",
                })
        workbook.close()
        return result

    def get_subwarehouses(self):
        workbook = load_workbook(self.file, data_only=True)
        sheet = workbook["Subwarehouse_Stock"]
        totals = {}
        for row in sheet.iter_rows(min_row=2, values_only=True):
            if not row[0]:
                continue
            rep = str(row[0]).strip()
            qty = float(row[3] or 0)
            totals[rep] = totals.get(rep, 0.0) + qty
        workbook.close()
        return totals

    def get_subwarehouse_stock(self, representative):
        workbook = load_workbook(self.file, data_only=True)
        sheet = workbook["Subwarehouse_Stock"]
        result = []
        for row in sheet.iter_rows(min_row=2, values_only=True):
            if str(row[0] or "").strip() != str(representative).strip():
                continue
            result.append({
                "product": row[1],
                "batch_code": row[2] or "",
                "quantity": float(row[3] or 0),
                "updated_at": row[4],
            })
        workbook.close()
        return result
