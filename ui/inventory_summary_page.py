from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QFrame, QHeaderView, QStyle, QPushButton, QScrollArea
)
from PySide6.QtCore import Qt

from database.transactions import TransactionRepository
from database.products import ProductRepository
from database.batches import BatchRepository
from utils.refresh_manager import refresh_manager


class InventorySummaryPage(QWidget):
    """Inventory dashboard with clickable product -> batch breakdown."""

    def __init__(self):
        super().__init__()
        self.setLayoutDirection(Qt.RightToLeft)
        self.transaction_repo = TransactionRepository()
        self.product_repo = ProductRepository()
        self.batch_repo = BatchRepository()
        self.selected_product = None

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QScrollArea.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        content = QWidget()
        main = QVBoxLayout(content)
        main.setContentsMargins(35, 30, 35, 30)
        main.setSpacing(20)

        header = QVBoxLayout()
        title = QLabel("Inventory Dashboard")
        title.setObjectName("dashboard_title")
        subtitle = QLabel("نظرة عامة على المخزون والحركات")
        subtitle.setObjectName("dashboard_subtitle")
        header.addWidget(title)
        header.addWidget(subtitle)
        main.addLayout(header)

        cards = QHBoxLayout()
        cards.setSpacing(18)
        self.current_stock_card, self.current_stock_value = self.create_card("الرصيد الحالي", "0.00", "kpi_green", QStyle.SP_DriveHDIcon)
        self.outgoing_card, self.outgoing_value = self.create_card("إجمالي المنصرف", "0.00", "kpi_blue", QStyle.SP_ArrowRight)
        self.incoming_card, self.incoming_value = self.create_card("إجمالي الوارد", "0.00", "kpi_orange", QStyle.SP_ArrowLeft)
        self.products_card, self.products_value = self.create_card("إجمالي الأصناف", "0", "kpi_purple", QStyle.SP_DirIcon)
        for card in [self.current_stock_card, self.outgoing_card, self.incoming_card, self.products_card]:
            cards.addWidget(card)
        main.addLayout(cards)

        section = QHBoxLayout()
        section_title = QLabel("ملخص المخزون — اضغط على أي صنف لعرض الباتشات")
        section_title.setObjectName("dashboard_section_title")
        section.addWidget(section_title)
        section.addStretch()
        main.addLayout(section)

        self.table = QTableWidget()
        self.table.setObjectName("dashboard_inventory_table")
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["الصنف", "أول المدة", "الوارد", "المنصرف", "الرصيد الحالي"])
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(44)
        header = self.table.horizontalHeader()
        header.setHighlightSections(False)
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        for i in range(1, 5):
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
        self.table.cellClicked.connect(self.show_batch_breakdown)
        main.addWidget(self.table)

        self.detail_frame = QFrame()
        self.detail_frame.setObjectName("transaction_card")
        detail = QVBoxLayout(self.detail_frame)
        detail.setContentsMargins(20, 18, 20, 18)
        detail.setSpacing(12)
        self.detail_title = QLabel("تفاصيل الباتشات")
        self.detail_title.setObjectName("section_title")
        detail.addWidget(self.detail_title)

        detail_cards = QHBoxLayout()
        self.detail_total = self.make_small_card("إجمالي الصنف", "0.00")
        self.detail_batch_count = self.make_small_card("عدد الباتشات", "0")
        detail_cards.addWidget(self.detail_total[0])
        detail_cards.addWidget(self.detail_batch_count[0])
        detail.addLayout(detail_cards)

        self.batch_table = QTableWidget()
        self.batch_table.setObjectName("dashboard_batch_table")
        self.batch_table.setColumnCount(7)
        self.batch_table.setHorizontalHeaderLabels(["الباتش", "الصلاحية", "أول المدة", "الوارد", "المرتجع", "المنصرف", "الرصيد"])
        self.batch_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.batch_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.batch_table.setAlternatingRowColors(True)
        self.batch_table.verticalHeader().setVisible(False)
        bh = self.batch_table.horizontalHeader()
        bh.setDefaultAlignment(Qt.AlignCenter)
        for i in range(7):
            bh.setSectionResizeMode(i, QHeaderView.ResizeToContents)
        self.batch_table.setMinimumHeight(150)
        detail.addWidget(self.batch_table)

        close = QPushButton("إخفاء تفاصيل الباتشات")
        close.setObjectName("secondary_button")
        close.clicked.connect(self.hide_batch_breakdown)
        detail.addWidget(close, alignment=Qt.AlignLeft)

        self.detail_frame.hide()
        main.addWidget(self.detail_frame)
        main.addStretch()

        self.scroll.setWidget(content)
        outer.addWidget(self.scroll)

        self.load_data()
        refresh_manager.data_changed.connect(self.load_data)
        refresh_manager.products_changed.connect(self.load_data)

    def create_card(self, title, value, object_name, icon_type):
        card = QFrame()
        card.setObjectName("kpi_card")
        card.setProperty("class", object_name)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 12, 18, 12)
        icon_label = QLabel()
        icon_label.setObjectName("kpi_icon")
        icon_label.setPixmap(self.style().standardIcon(icon_type).pixmap(28, 28))
        icon_label.setAlignment(Qt.AlignCenter)
        title_label = QLabel(title)
        title_label.setObjectName("kpi_title")
        title_label.setAlignment(Qt.AlignCenter)
        value_label = QLabel(value)
        value_label.setObjectName("kpi_value")
        value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        return card, value_label

    def make_small_card(self, title, value):
        card = QFrame()
        card.setObjectName("kpi_card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 10, 15, 10)
        label = QLabel(title)
        label.setObjectName("kpi_title")
        label.setAlignment(Qt.AlignCenter)
        val = QLabel(value)
        val.setObjectName("kpi_value")
        val.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        layout.addWidget(val)
        return card, val

    def load_data(self):
        data = self.transaction_repo.get_inventory_summary()
        self.table.setRowCount(len(data))
        total_in = total_out = total_current = 0.0
        for r, row in enumerate(data):
            for c, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter if c == 0 else Qt.AlignCenter)
                self.table.setItem(r, c, item)
            total_in += float(row[2] or 0)
            total_out += float(row[3] or 0)
            total_current += float(row[4] or 0)
        self.current_stock_value.setText(f"{total_current:,.2f}")
        self.incoming_value.setText(f"{total_in:,.2f}")
        self.outgoing_value.setText(f"{total_out:,.2f}")
        self.products_value.setText(f"{len(data):,}")
        if self.selected_product:
            self.refresh_detail()

    def show_batch_breakdown(self, row, _column):
        item = self.table.item(row, 0)
        if not item:
            return
        self.selected_product = item.text()
        self.refresh_detail()
        self.detail_frame.show()
        self.scroll.ensureWidgetVisible(self.detail_frame, 20, 20)

    def refresh_detail(self):
        product = self.selected_product
        product_id = self.product_repo.get_product_id(product)
        batches = self.batch_repo.get_batches(product_id) if product_id is not None else []
        self.detail_title.setText(f"باتشات صنف: {product}")
        _, _, total_balance = self.transaction_repo.get_product_balance(product)
        self.detail_total[1].setText(f"{total_balance:,.2f}")
        self.detail_batch_count[1].setText(str(len(batches)))
        self.batch_table.setRowCount(len(batches))

        for r, batch in enumerate(batches):
            transactions = self.transaction_repo.get_transactions_by_product(product, batch["code"])
            normal_in = returns = out = 0.0
            for tx in transactions:
                qty = float(tx[5] or 0)
                if tx[4] == "مردودات مبيعات":
                    returns += qty
                elif tx[4] in ["إنتاج", "مشتريات"]:
                    normal_in += qty
                else:
                    out += qty
            _, _, balance = self.transaction_repo.get_batch_balance(product, batch["code"])
            values = [
                batch["code"], batch["expiry_date"], f'{batch["opening_balance"]:,.2f}',
                f"{normal_in:,.2f}", f"{returns:,.2f}", f"{out:,.2f}", f"{balance:,.2f}"
            ]
            for c, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)
                self.batch_table.setItem(r, c, item)

    def hide_batch_breakdown(self):
        self.detail_frame.hide()
        self.selected_product = None
