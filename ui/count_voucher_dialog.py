from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QDoubleSpinBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QScrollArea, QFrame, QMessageBox,
)
from PySide6.QtCore import Qt

from database.issues import IssueRepository


class CountVoucherDialog(QDialog):
    """Record the physical count against the original issue voucher."""

    def __init__(self, issue_no, parent=None):
        super().__init__(parent)
        self.issue_no = str(issue_no)
        self.repo = IssueRepository()
        self.issue = self.repo.get_issue(self.issue_no)
        self.rows = []
        self.setWindowTitle(f"جرد إذن الصرف {self.issue_no}")
        self.resize(1100, 760)
        self.setMinimumSize(900, 620)
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(18, 16, 18, 14)
        root.setSpacing(10)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        content = QFrame()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(6, 6, 12, 6)
        layout.setSpacing(12)
        scroll.setWidget(content)
        root.addWidget(scroll, 1)

        title = QLabel("جرد مخزن المندوب")
        title.setObjectName("page_title")
        layout.addWidget(title)

        if not self.issue:
            layout.addWidget(QLabel("إذن الصرف غير موجود."))
            self.save_button = None
            return

        info = QFrame()
        info.setObjectName("transaction_card")
        info_layout = QHBoxLayout(info)
        info_layout.setContentsMargins(16, 12, 16, 12)
        info_layout.addWidget(QLabel(f"إذن الصرف: {self.issue_no}"))
        info_layout.addWidget(QLabel(f"المندوب: {self.issue['representative']}"))
        info_layout.addWidget(QLabel(f"التاريخ: {self.issue['date']}"))
        info_layout.addStretch()
        layout.addWidget(info)

        hint = QLabel("اكتب الكمية الموجودة فعليًا في السيارة. الأصناف والـBatch والكميات الأصلية مأخوذة من إذن الصرف.")
        hint.setObjectName("section_description")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["الصنف", "كمية الصرف", "الباتش", "الصلاحية", "الجرد الفعلي"])
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionMode(QTableWidget.NoSelection)
        self.table.setFocusPolicy(Qt.NoFocus)
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        layout.addWidget(self.table)

        for line in self.issue["lines"]:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setRowHeight(row, 58)
            product = QTableWidgetItem(str(line["product"]))
            product.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(row, 0, product)
            issued = QTableWidgetItem(f"{line['quantity']:,.2f}")
            issued.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 1, issued)
            batch = QTableWidgetItem(line["batch_code"] or "—")
            batch.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 2, batch)
            expiry = QTableWidgetItem(str(line["expiry_date"] or "—"))
            expiry.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 3, expiry)
            count = QDoubleSpinBox()
            count.setRange(0.0, float(line["quantity"]))
            count.setDecimals(2)
            count.setSingleStep(1.0)
            count.setButtonSymbols(QDoubleSpinBox.NoButtons)
            count.setMinimumHeight(40)
            count.setAlignment(Qt.AlignCenter)
            self.table.setCellWidget(row, 4, count)
            self.rows.append((line, count))

        layout.addStretch()

        actions = QFrame()
        actions.setObjectName("transaction_card")
        action_layout = QHBoxLayout(actions)
        action_layout.setContentsMargins(10, 8, 10, 8)
        cancel = QPushButton("إلغاء")
        cancel.setObjectName("secondary_button")
        cancel.setMinimumHeight(46)
        cancel.clicked.connect(self.reject)
        self.save_button = QPushButton("حفظ الجرد")
        self.save_button.setObjectName("primary_button")
        self.save_button.setMinimumHeight(46)
        self.save_button.setMinimumWidth(180)
        self.save_button.clicked.connect(self.save_count)
        action_layout.addWidget(cancel)
        action_layout.addStretch()
        action_layout.addWidget(self.save_button)
        root.addWidget(actions)

    def save_count(self):
        try:
            lines = []
            for original, widget in self.rows:
                lines.append({
                    "product": original["product"],
                    "batch_code": original["batch_code"],
                    "counted_quantity": float(widget.value()),
                })
            self.repo.save_count(self.issue_no, lines)
        except Exception as exc:
            QMessageBox.warning(self, "تعذر حفظ الجرد", str(exc))
            return
        QMessageBox.information(self, "تم الحفظ", "تم تسجيل الجرد بنجاح. لم يتم تنفيذ التصفية أو إعادة الكمية للمخزن الرئيسي بعد.")
        self.accept()
