from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QScrollArea, QFrame,
    QMessageBox,
)
from PySide6.QtCore import Qt

from database.issues import IssueRepository


class LiquidationDialog(QDialog):
    """Close an issue after count: return counted stock and calculate sold quantity."""

    def __init__(self, issue_no, parent=None):
        super().__init__(parent)
        self.issue_no = str(issue_no)
        self.repo = IssueRepository()
        self.issue = self.repo.get_issue(self.issue_no)
        self.count = self.repo.get_count(self.issue_no)
        self.setWindowTitle(f"تصفية إذن الصرف {self.issue_no}")
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

        title = QLabel("تصفية إذن الصرف")
        title.setObjectName("page_title")
        layout.addWidget(title)

        if not self.issue or not self.count:
            layout.addWidget(QLabel("لا يوجد إذن أو جرد مسجل لهذا الإذن."))
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

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["الصنف", "Batch", "الصلاحية", "إذن الصرف", "الجرد", "البيع"])
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        for column in range(1, 6):
            header.setSectionResizeMode(column, QHeaderView.ResizeToContents)
        layout.addWidget(self.table)

        total_issued = 0.0
        total_counted = 0.0
        total_sold = 0.0
        count_map = {(str(x["product"]).strip(), str(x["batch_code"]).strip().lower()): float(x["counted_quantity"] or 0) for x in self.count["lines"]}

        for line in self.issue["lines"]:
            key = (str(line["product"]).strip(), str(line["batch_code"]).strip().lower())
            counted = count_map.get(key, 0.0)
            issued = float(line["quantity"] or 0)
            sold = issued - counted
            total_issued += issued
            total_counted += counted
            total_sold += sold
            row = self.table.rowCount()
            self.table.insertRow(row)
            values = [line["product"], line["batch_code"] or "—", line["expiry_date"] or "—", f"{issued:,.2f}", f"{counted:,.2f}", f"{sold:,.2f}"]
            for col, value in enumerate(values):
                cell = QTableWidgetItem(str(value))
                cell.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter if col == 0 else Qt.AlignCenter)
                self.table.setItem(row, col, cell)

        summary = QFrame()
        summary.setObjectName("transaction_card")
        summary_layout = QHBoxLayout(summary)
        summary_layout.setContentsMargins(16, 12, 16, 12)
        summary_layout.addWidget(QLabel(f"إجمالي الصرف: {total_issued:,.2f}"))
        summary_layout.addWidget(QLabel(f"إجمالي الجرد المرتجع: {total_counted:,.2f}"))
        sale = QLabel(f"إجمالي البيع: {total_sold:,.2f}")
        sale.setObjectName("kpi_value")
        summary_layout.addWidget(sale)
        summary_layout.addStretch()
        layout.addWidget(summary)

        actions = QFrame()
        actions.setObjectName("transaction_card")
        action_layout = QHBoxLayout(actions)
        action_layout.setContentsMargins(10, 8, 10, 8)
        cancel = QPushButton("إلغاء")
        cancel.setObjectName("secondary_button")
        cancel.setMinimumHeight(46)
        cancel.clicked.connect(self.reject)
        self.save_button = QPushButton("تصفية وإغلاق الإذن")
        self.save_button.setObjectName("primary_button")
        self.save_button.setMinimumHeight(46)
        self.save_button.setMinimumWidth(220)
        self.save_button.clicked.connect(self.liquidate)
        action_layout.addWidget(cancel)
        action_layout.addStretch()
        action_layout.addWidget(self.save_button)
        root.addWidget(actions)

    def liquidate(self):
        try:
            result = self.repo.liquidate_issue(self.issue_no)
        except Exception as exc:
            QMessageBox.warning(self, "تعذر تنفيذ التصفية", str(exc))
            return
        QMessageBox.information(self, "تمت التصفية", f"تمت تصفية الإذن بنجاح.\nإجمالي البيع: {result['sold']:,.2f}\nتمت إعادة الجرد للمخزن الرئيسي.")
        self.accept()
