from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QScrollArea,
)
from PySide6.QtCore import Qt

from database.issues import IssueRepository
from ui.count_voucher_dialog import CountVoucherDialog
from ui.liquidation_dialog import LiquidationDialog
from utils.refresh_manager import refresh_manager


class SubwarehousesPage(QWidget):
    """Representatives' cars as subwarehouses."""

    def __init__(self):
        super().__init__()
        self.repo = IssueRepository()
        self.selected_rep = None
        self.build_ui()
        refresh_manager.data_changed.connect(self.load_data)
        self.load_data()

    def build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(35, 30, 35, 30)
        root.setSpacing(18)

        title = QLabel("المخازن الفرعية")
        title.setObjectName("page_title")
        subtitle = QLabel("كل سيارة مندوب تُعامل كمخزن فرعي مستقل")
        subtitle.setObjectName("page_subtitle")
        root.addWidget(title)
        root.addWidget(subtitle)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.content = QWidget()
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(0, 10, 0, 10)
        self.content_layout.setSpacing(14)
        self.scroll.setWidget(self.content)
        root.addWidget(self.scroll, 1)

    def _clear(self):
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def load_data(self, *_):
        self._clear()
        totals = self.repo.get_subwarehouses()
        open_issues = self.repo.get_open_issues()
        open_reps = {item["representative"] for item in open_issues}
        reps = sorted(set(totals) | open_reps)

        if not reps:
            empty = QLabel("لا توجد مخازن فرعية حتى الآن. عند حفظ أول إذن صرف سيظهر المندوب هنا.")
            empty.setObjectName("section_description")
            self.content_layout.addWidget(empty)
            self.content_layout.addStretch()
            return

        for rep in reps:
            self._add_rep_card(rep, totals.get(rep, 0.0), rep in open_reps)
        self.content_layout.addStretch()

    def _add_rep_card(self, representative, total, is_open):
        card = QFrame()
        card.setObjectName("transaction_card")
        layout = QHBoxLayout(card)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(15)

        title_box = QVBoxLayout()
        name = QLabel(representative)
        name.setObjectName("section_title")
        status = QLabel("غير مُصفّى" if is_open else "مُصفّى")
        status.setObjectName("section_description")
        title_box.addWidget(name)
        title_box.addWidget(status)

        amount = QLabel(f"الرصيد المحمّل: {total:,.2f}")
        amount.setObjectName("kpi_value")
        amount.setAlignment(Qt.AlignCenter)

        button = QPushButton("فتح المخزن")
        button.setMinimumHeight(44)
        button.setObjectName("danger_button" if is_open else "secondary_button")
        button.setCursor(Qt.PointingHandCursor)
        button.clicked.connect(lambda _=False, rep=representative: self.show_rep(rep))

        layout.addLayout(title_box, 1)
        layout.addWidget(amount)
        layout.addWidget(button)
        self.content_layout.addWidget(card)

    def show_rep(self, representative):
        self.selected_rep = representative
        self._clear()

        back = QPushButton("← رجوع للمخازن الفرعية")
        back.setObjectName("secondary_button")
        back.clicked.connect(self.load_data)
        self.content_layout.addWidget(back, 0, Qt.AlignLeft)

        title = QLabel(f"مخزن المندوب: {representative}")
        title.setObjectName("page_title")
        self.content_layout.addWidget(title)

        issues = [x for x in self.repo.get_open_issues() if x["representative"] == representative]
        if issues:
            issue_title = QLabel("أذون الصرف المفتوحة")
            issue_title.setObjectName("section_title")
            self.content_layout.addWidget(issue_title)
            for issue in issues:
                card = QFrame()
                card.setObjectName("transaction_card")
                row = QHBoxLayout(card)
                row.setContentsMargins(14, 10, 14, 10)
                label = QLabel(f"إذن {issue['issue_no']} — {issue['date']}")
                label.setObjectName("section_description")
                row.addWidget(label, 1)

                count_button = QPushButton("جرد")
                count_button.setObjectName("primary_button")
                count_button.setMinimumHeight(40)
                count_button.setCursor(Qt.PointingHandCursor)
                already_counted = self.repo.has_count(issue["issue_no"])
                count_button.setEnabled(not already_counted)
                count_button.setText("تم الجرد" if already_counted else "جرد")
                count_button.clicked.connect(lambda _=False, no=issue["issue_no"]: self.open_count(no))
                row.addWidget(count_button)

                if already_counted:
                    liquidated = self.repo.has_liquidation(issue["issue_no"])
                    liquidate_button = QPushButton("تمت التصفية" if liquidated else "تصفية")
                    liquidate_button.setObjectName("secondary_button" if liquidated else "primary_button")
                    liquidate_button.setMinimumHeight(40)
                    liquidate_button.setCursor(Qt.PointingHandCursor)
                    liquidate_button.setEnabled(not liquidated)
                    liquidate_button.clicked.connect(lambda _=False, no=issue["issue_no"]: self.open_liquidation(no))
                    row.addWidget(liquidate_button)

                self.content_layout.addWidget(card)

        closed_title = QLabel("الأذون المكتملة")
        closed_title.setObjectName("section_title")
        self.content_layout.addWidget(closed_title)
        closed = self.repo.get_closed_issues_for_rep(representative)
        if not closed:
            self.content_layout.addWidget(QLabel("لا توجد أذون مكتملة بعد."))
        else:
            for issue in closed:
                card = QFrame()
                card.setObjectName("transaction_card")
                row = QHBoxLayout(card)
                row.setContentsMargins(14, 10, 14, 10)
                label = QLabel(f"إذن {issue['issue_no']} — {issue['date']}")
                label.setObjectName("section_description")
                row.addWidget(label, 1)
                done = QLabel("● مكتمل")
                done.setObjectName("success_text")
                done.setAlignment(Qt.AlignCenter)
                row.addWidget(done)
                self.content_layout.addWidget(card)

        table_title = QLabel("الرصيد الحالي في السيارة")
        table_title.setObjectName("section_title")
        self.content_layout.addWidget(table_title)

        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["الصنف", "الباتش", "الصلاحية", "الرصيد"])
        table.setAlternatingRowColors(True)
        table.setShowGrid(False)
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)

        stock = self.repo.get_subwarehouse_stock(representative)
        table.setRowCount(len(stock))
        for r, item in enumerate(stock):
            values = [item["product"], item["batch_code"] or "—", "—", f"{item['quantity']:,.2f}"]
            for c, value in enumerate(values):
                cell = QTableWidgetItem(str(value))
                cell.setTextAlignment(Qt.AlignCenter if c else (Qt.AlignRight | Qt.AlignVCenter))
                table.setItem(r, c, cell)

        self.content_layout.addWidget(table)
        self.content_layout.addStretch()

    def open_count(self, issue_no):
        dialog = CountVoucherDialog(issue_no, self)
        if dialog.exec():
            self.show_rep(self.selected_rep)

    def open_liquidation(self, issue_no):
        dialog = LiquidationDialog(issue_no, self)
        if dialog.exec():
            self.show_rep(self.selected_rep)
