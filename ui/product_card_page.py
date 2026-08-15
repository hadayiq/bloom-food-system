from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox,
    QLineEdit, QTextEdit, QMessageBox, QFrame, QTableWidget,
    QTableWidgetItem, QHeaderView, QScrollArea, QListWidget, QListWidgetItem
)
from PySide6.QtCore import Qt

from database.products import ProductRepository
from database.transactions import TransactionRepository
from database.batches import BatchRepository
from utils.refresh_manager import refresh_manager


class ProductCardPage(QWidget):
    """Product card with optional batch-level filtering and movement tracking."""

    IN_TYPES = ["إنتاج", "مشتريات", "مردودات مبيعات"]
    OUT_TYPES = ["صرف للتجزئة", "صرف للتسليمات"]

    def __init__(self):
        super().__init__()
        self.setLayoutDirection(Qt.RightToLeft)
        self.product_repo = ProductRepository()
        self.transaction_repo = TransactionRepository()
        self.batch_repo = BatchRepository()
        self.selected_product = None
        self.selected_transaction_id = None
        self.products_data = []
        self.build_ui()
        self.load_products()
        refresh_manager.products_changed.connect(self.reload_products)
        refresh_manager.data_changed.connect(self.refresh_page)
        self.show_search_view()

    def build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QScrollArea.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setLayoutDirection(Qt.RightToLeft)
        content = QWidget()
        content.setLayoutDirection(Qt.RightToLeft)
        main = QVBoxLayout(content)
        main.setContentsMargins(35, 30, 35, 30)
        main.setSpacing(18)
        title = QLabel("كارت الصنف")
        title.setObjectName("page_title")
        title.setAlignment(Qt.AlignRight)
        main.addWidget(title)
        subtitle = QLabel("اعرض حركات الصنف بالكامل أو حركات باتش محدد")
        subtitle.setObjectName("page_subtitle")
        subtitle.setAlignment(Qt.AlignRight)
        main.addWidget(subtitle)

        self.search_view = QWidget()
        search_layout = QVBoxLayout(self.search_view)
        search_layout.setContentsMargins(0, 55, 0, 55)
        search_layout.setSpacing(15)
        search_title = QLabel("ابحث عن الصنف")
        search_title.setObjectName("search_page_title")
        search_title.setAlignment(Qt.AlignCenter)
        search_layout.addWidget(search_title)
        self.search_input = QLineEdit()
        self.search_input.setObjectName("product_search")
        self.search_input.setPlaceholderText("🔍  ابحث باسم الصنف أو الكود...")
        self.search_input.setMinimumHeight(58)
        self.search_input.setAlignment(Qt.AlignRight)
        self.search_input.textChanged.connect(self.filter_products)
        self.search_input.returnPressed.connect(self.select_first_search_result)
        search_layout.addWidget(self.search_input)
        self.search_results = QListWidget()
        self.search_results.setObjectName("product_search_results")
        self.search_results.setMaximumHeight(230)
        self.search_results.setLayoutDirection(Qt.RightToLeft)
        self.search_results.hide()
        self.search_results.itemClicked.connect(self.select_search_result)
        search_layout.addWidget(self.search_results)
        main.addWidget(self.search_view)

        self.product_view = QWidget()
        product_layout = QVBoxLayout(self.product_view)
        product_layout.setContentsMargins(0, 0, 0, 0)
        product_layout.setSpacing(16)
        self.top_search = QLineEdit()
        self.top_search.setObjectName("top_product_search")
        self.top_search.setPlaceholderText("🔍  ابحث عن صنف آخر...")
        self.top_search.setMinimumHeight(48)
        self.top_search.textChanged.connect(self.filter_top_products)
        self.top_search.returnPressed.connect(self.select_first_top_result)
        product_layout.addWidget(self.top_search)
        self.top_search_results = QListWidget()
        self.top_search_results.setObjectName("top_product_search_results")
        self.top_search_results.setMaximumHeight(180)
        self.top_search_results.hide()
        self.top_search_results.itemClicked.connect(self.select_top_search_result)
        product_layout.addWidget(self.top_search_results)

        batch_frame = QFrame()
        batch_frame.setObjectName("transaction_card")
        batch_layout = QVBoxLayout(batch_frame)
        batch_layout.setContentsMargins(20, 16, 20, 16)
        batch_layout.setSpacing(8)
        batch_label = QLabel("عرض الحركات حسب الباتش")
        batch_label.setObjectName("form_label")
        batch_layout.addWidget(batch_label)
        self.batch_combo = QComboBox()
        self.batch_combo.setMinimumHeight(46)
        self.batch_combo.setEditable(True)
        self.batch_combo.setInsertPolicy(QComboBox.NoInsert)
        self.batch_combo.setPlaceholderText("كل الباتشات")
        self.batch_combo.setLayoutDirection(Qt.RightToLeft)
        self.batch_combo.currentIndexChanged.connect(self.batch_filter_changed)
        batch_layout.addWidget(self.batch_combo)
        self.batch_info = QLabel("")
        self.batch_info.setObjectName("page_subtitle")
        self.batch_info.setAlignment(Qt.AlignRight)
        batch_layout.addWidget(self.batch_info)
        product_layout.addWidget(batch_frame)

        cards = QHBoxLayout()
        cards.setSpacing(12)
        self.code_card, self.code_value = self.create_info_card("كود الصنف", "-", "kpi_purple")
        self.name_card, self.name_value = self.create_info_card("اسم الصنف", "-", "kpi_blue")
        self.unit_card, self.unit_value = self.create_info_card("الوحدة", "-", "kpi_orange")
        self.opening_card, self.opening_value = self.create_info_card("رصيد أول المدة", "0.00", "kpi_green")
        self.balance_card, self.balance_value = self.create_info_card("الرصيد الحالي", "0.00", "kpi_green")
        for card in [self.code_card, self.name_card, self.unit_card, self.opening_card, self.balance_card]:
            cards.addWidget(card)
        product_layout.addLayout(cards)

        movement_cards = QHBoxLayout()
        self.batch_in_card, self.batch_in_value = self.create_info_card("الوارد", "0.00", "kpi_blue")
        self.batch_return_card, self.batch_return_value = self.create_info_card("المرتجع", "0.00", "kpi_orange")
        self.batch_out_card, self.batch_out_value = self.create_info_card("المنصرف", "0.00", "kpi_purple")
        for card in [self.batch_in_card, self.batch_return_card, self.batch_out_card]:
            movement_cards.addWidget(card)
        product_layout.addLayout(movement_cards)

        header_layout = QHBoxLayout()
        section = QLabel("حركات الصنف")
        section.setObjectName("section_title")
        header_layout.addWidget(section)
        header_layout.addStretch()
        self.pdf_button = QPushButton("PDF")
        self.pdf_button.setObjectName("secondary_button")
        self.pdf_button.setMinimumHeight(42)
        self.pdf_button.clicked.connect(self.pdf_placeholder)
        header_layout.addWidget(self.pdf_button)
        self.edit_button = QPushButton("تعديل")
        self.edit_button.setObjectName("secondary_button")
        self.edit_button.setMinimumHeight(42)
        self.edit_button.clicked.connect(self.show_edit_view)
        self.edit_button.hide()
        header_layout.addWidget(self.edit_button)
        self.delete_button = QPushButton("حذف")
        self.delete_button.setObjectName("danger_button")
        self.delete_button.setMinimumHeight(42)
        self.delete_button.clicked.connect(self.delete_transaction)
        self.delete_button.hide()
        header_layout.addWidget(self.delete_button)
        product_layout.addLayout(header_layout)

        self.table = QTableWidget()
        self.table.setObjectName("product_card_table")
        self.table.setLayoutDirection(Qt.RightToLeft)
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(["رقم الحركة", "التاريخ", "الوقت", "الباتش", "نوع الحركة", "الوارد", "المنصرف", "ملاحظات"])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setMinimumHeight(320)
        header = self.table.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignCenter)
        for i in range(7):
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.Stretch)
        self.table.cellClicked.connect(self.select_transaction)
        product_layout.addWidget(self.table)

        self.edit_view = QFrame()
        self.edit_view.setObjectName("transaction_card")
        edit = QVBoxLayout(self.edit_view)
        edit.setContentsMargins(22, 22, 22, 22)
        edit.setSpacing(10)
        label = QLabel("الصنف"); label.setObjectName("form_label"); edit.addWidget(label)
        self.edit_product_combo = QComboBox(); self.edit_product_combo.setMinimumHeight(45); self.edit_product_combo.setLayoutDirection(Qt.RightToLeft); edit.addWidget(self.edit_product_combo)
        label = QLabel("الباتش"); label.setObjectName("form_label"); edit.addWidget(label)
        self.edit_batch_combo = QComboBox(); self.edit_batch_combo.setMinimumHeight(45); self.edit_batch_combo.setLayoutDirection(Qt.RightToLeft); edit.addWidget(self.edit_batch_combo)
        label = QLabel("نوع الحركة"); label.setObjectName("form_label"); edit.addWidget(label)
        self.edit_type_combo = QComboBox(); self.edit_type_combo.setMinimumHeight(45); self.edit_type_combo.addItems(self.IN_TYPES + self.OUT_TYPES); edit.addWidget(self.edit_type_combo)
        label = QLabel("الكمية"); label.setObjectName("form_label"); edit.addWidget(label)
        self.edit_quantity = QLineEdit(); self.edit_quantity.setMinimumHeight(45); edit.addWidget(self.edit_quantity)
        label = QLabel("ملاحظات"); label.setObjectName("form_label"); edit.addWidget(label)
        self.edit_notes = QTextEdit(); self.edit_notes.setMinimumHeight(100); edit.addWidget(self.edit_notes)
        buttons = QHBoxLayout(); buttons.addStretch()
        cancel = QPushButton("إلغاء"); cancel.setObjectName("secondary_button"); cancel.setMinimumHeight(45); cancel.clicked.connect(self.cancel_edit); buttons.addWidget(cancel)
        save = QPushButton("حفظ التعديل"); save.setObjectName("primary_button"); save.setMinimumHeight(45); save.clicked.connect(self.update_transaction); buttons.addWidget(save)
        edit.addLayout(buttons)
        self.edit_view.hide()
        product_layout.addWidget(self.edit_view)
        self.product_view.hide()
        main.addWidget(self.product_view)
        main.addStretch()
        self.scroll_area.setWidget(content)
        outer.addWidget(self.scroll_area)

    def create_info_card(self, title, value, style_class):
        card = QFrame(); card.setObjectName("kpi_card"); card.setProperty("class", style_class)
        layout = QVBoxLayout(card); layout.setContentsMargins(15, 12, 15, 12)
        label = QLabel(title); label.setObjectName("kpi_title"); label.setAlignment(Qt.AlignCenter)
        value_label = QLabel(value); value_label.setObjectName("kpi_value"); value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label); layout.addWidget(value_label)
        return card, value_label

    def load_products(self):
        products = self.product_repo.get_all_products()
        self.products_data = [{"id": str(row["product_ID"]), "name": str(row["Product_Name"]), "unit": str(row["Unit"])} for _, row in products.iterrows()]
        self.edit_product_combo.clear()
        for product in self.products_data:
            self.edit_product_combo.addItem(product["name"], product["id"])

    def filter_products(self):
        text = self.search_input.text().strip().lower(); self.search_results.clear()
        if not text:
            self.search_results.hide(); return
        for product in self.products_data:
            if text in product["name"].lower() or text in product["id"].lower():
                item = QListWidgetItem(f'{product["name"]}   •   {product["id"]}'); item.setData(Qt.UserRole, product["id"]); self.search_results.addItem(item)
        self.search_results.setVisible(self.search_results.count() > 0)

    def select_first_search_result(self):
        if self.search_results.count(): self.select_search_result(self.search_results.item(0))

    def select_search_result(self, item):
        product = self.find_product(item.data(Qt.UserRole))
        if product: self.show_product(product)

    def find_product(self, product_id):
        return next((p for p in self.products_data if p["id"] == product_id), None)

    def show_product(self, product):
        self.selected_product = product
        self.search_view.hide(); self.product_view.show()
        self.top_search.clear(); self.top_search_results.hide()
        self.populate_batches()
        self.update_product_cards(); self.load_transactions()
        self.scroll_area.verticalScrollBar().setValue(0)

    def populate_batches(self, preserve_code=None):
        self.batch_combo.blockSignals(True); self.batch_combo.clear(); self.batch_combo.addItem("كل الباتشات", "")
        for batch in self.batch_repo.get_batches(self.selected_product["id"]):
            self.batch_combo.addItem(str(batch["code"]), str(batch["code"]))
        self.batch_combo.blockSignals(False)
        if preserve_code:
            index = self.batch_combo.findData(preserve_code)
            if index >= 0: self.batch_combo.setCurrentIndex(index)
        else: self.batch_combo.setCurrentIndex(0)
        self.update_batch_info()

    def batch_filter_changed(self, _index=0):
        self.update_batch_info(); self.load_transactions()

    def update_batch_info(self):
        code = self.batch_combo.currentData() or ""
        if not self.selected_product or not code:
            self.batch_info.setText("عرض كل حركات الصنف — اختر باتش محدد لرؤية إجمالي الوارد والمرتجع والمنصرف له.")
            self.batch_in_value.setText("0.00"); self.batch_return_value.setText("0.00"); self.batch_out_value.setText("0.00")
            return
        batch = self.batch_repo.get_batch(self.selected_product["id"], code)
        if not batch: return
        _, out_total, balance = self.transaction_repo.get_batch_balance(self.selected_product["name"], code)
        returns = 0.0; normal_in = 0.0
        for row in self.transaction_repo.get_transactions_by_product(self.selected_product["name"], code):
            qty = float(row[5] or 0)
            if row[4] == "مردودات مبيعات": returns += qty
            elif row[4] in ["إنتاج", "مشتريات"]: normal_in += qty
        self.batch_in_value.setText(f"{normal_in:,.2f}"); self.batch_return_value.setText(f"{returns:,.2f}"); self.batch_out_value.setText(f"{out_total:,.2f}")
        self.batch_info.setText(f'الباتش: {code}  •  إنتاج: {batch["production_date"]}  •  صلاحية: {batch["expiry_date"]}  •  رصيد أول المدة: {batch["opening_balance"]:,.2f}  •  الرصيد الحالي: {balance:,.2f}')

    def update_product_cards(self):
        if not self.selected_product: return
        product_id = self.selected_product["id"]; name = self.selected_product["name"]
        opening = self.product_repo.get_opening_balance(product_id); _, _, balance = self.transaction_repo.get_product_balance(name)
        self.code_value.setText(product_id); self.name_value.setText(name); self.unit_value.setText(self.selected_product["unit"])
        self.opening_value.setText(f"{opening:,.2f}"); self.balance_value.setText(f"{balance:,.2f}")

    def load_transactions(self):
        if not self.selected_product: return
        name = self.selected_product["name"]; code = self.batch_combo.currentData() or None
        transactions = self.transaction_repo.get_transactions_by_product(name, code)
        self.table.setRowCount(len(transactions))
        for r, row in enumerate(transactions):
            qty = float(row[5] or 0); typ = row[4]
            incoming = f"{qty:,.2f}" if typ in self.IN_TYPES else ""; outgoing = f"{qty:,.2f}" if typ in self.OUT_TYPES else ""
            values = [row[0], row[1], row[2], row[7] if len(row) > 7 and row[7] else "—", typ, incoming, outgoing, row[6] or ""]
            for c, value in enumerate(values):
                item = QTableWidgetItem(str(value)); item.setTextAlignment(Qt.AlignCenter); self.table.setItem(r, c, item)
        self.selected_transaction_id = None; self.show_action_buttons(False)

    def select_transaction(self, row, _column):
        item = self.table.item(row, 0)
        if item: self.selected_transaction_id = item.text(); self.show_action_buttons(True)

    def show_action_buttons(self, selected):
        self.pdf_button.setVisible(not selected); self.edit_button.setVisible(selected); self.delete_button.setVisible(selected)

    def pdf_placeholder(self):
        QMessageBox.information(self, "PDF", "زر إنشاء PDF جاهز، وسنضيف وظيفة التصدير لاحقًا.")

    def show_edit_view(self):
        if not self.selected_transaction_id: return
        tx = self.transaction_repo.get_transaction_by_id(self.selected_transaction_id)
        if not tx: return
        self.edit_product_combo.setCurrentText(tx["product"]); self.populate_edit_batches(tx["product"], tx.get("batch", ""))
        self.edit_type_combo.setCurrentText(tx["type"]); self.edit_quantity.setText(str(tx["quantity"])); self.edit_notes.setPlainText(str(tx["notes"] or ""))
        self.table.hide(); self.edit_view.show(); self.pdf_button.hide(); self.edit_button.hide(); self.delete_button.hide()
        self.scroll_area.verticalScrollBar().setValue(self.scroll_area.verticalScrollBar().maximum())

    def populate_edit_batches(self, product_name, batch_code=""):
        product = next((p for p in self.products_data if p["name"] == product_name), None)
        self.edit_batch_combo.clear(); self.edit_batch_combo.addItem("بدون باتش", "")
        if product:
            for batch in self.batch_repo.get_batches(product["id"]): self.edit_batch_combo.addItem(str(batch["code"]), str(batch["code"]))
        index = self.edit_batch_combo.findData(batch_code or ""); self.edit_batch_combo.setCurrentIndex(max(0, index))

    def cancel_edit(self):
        self.edit_view.hide(); self.table.show(); self.selected_transaction_id = None; self.show_action_buttons(False)

    def update_transaction(self):
        if not self.selected_transaction_id: return
        try: quantity = float(self.edit_quantity.text().strip())
        except ValueError:
            QMessageBox.warning(self, "خطأ", "الكمية يجب أن تكون رقمًا."); return
        if quantity <= 0:
            QMessageBox.warning(self, "خطأ", "الكمية يجب أن تكون أكبر من صفر."); return
        tx = self.transaction_repo.get_transaction_by_id(self.selected_transaction_id)
        if not tx: return
        product = self.edit_product_combo.currentText(); typ = self.edit_type_combo.currentText(); batch = self.edit_batch_combo.currentData() or None; notes = self.edit_notes.toPlainText().strip()
        try:
            self.transaction_repo.update_transaction(self.selected_transaction_id, product, typ, quantity, notes, batch)
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء تعديل الحركة:\n{e}"); return
        self.cancel_edit(); self.update_product_cards(); self.load_transactions()

    def delete_transaction(self):
        if not self.selected_transaction_id: return
        tx = self.transaction_repo.get_transaction_by_id(self.selected_transaction_id)
        if not tx: return
        reply = QMessageBox.question(self, "تأكيد حذف الحركة", f"هل أنت متأكد من حذف الحركة {tx['id']}؟", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply != QMessageBox.Yes: return
        try: self.transaction_repo.delete_transaction(self.selected_transaction_id)
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء حذف الحركة:\n{e}"); return
        self.selected_transaction_id = None; self.show_action_buttons(False); self.update_product_cards(); self.load_transactions()

    def filter_top_products(self, text):
        text = text.strip().lower(); self.top_search_results.clear()
        if not text: self.top_search_results.hide(); return
        for product in self.products_data:
            if text in product["name"].lower() or text in product["id"].lower():
                item = QListWidgetItem(f'{product["name"]}   •   {product["id"]}'); item.setData(Qt.UserRole, product["id"]); self.top_search_results.addItem(item)
        self.top_search_results.setVisible(self.top_search_results.count() > 0)

    def select_first_top_result(self):
        if self.top_search_results.count(): self.select_top_search_result(self.top_search_results.item(0))

    def select_top_search_result(self, item):
        product = self.find_product(item.data(Qt.UserRole))
        if product: self.show_product(product)

    def reload_products(self):
        old = self.selected_product["id"] if self.selected_product else None
        self.load_products()
        if old:
            product = self.find_product(old)
            if product: self.show_product(product)

    def refresh_page(self):
        if self.selected_product:
            product = self.find_product(self.selected_product["id"])
            if product:
                self.selected_product = product
                self.populate_batches(self.batch_combo.currentData() or "")
                self.update_product_cards(); self.load_transactions()
        else:
            self.load_products()

    def show_search_view(self):
        self.selected_product = None; self.selected_transaction_id = None
        self.product_view.hide(); self.search_view.show(); self.top_search_results.hide(); self.edit_view.hide(); self.table.show()
        self.show_action_buttons(False); self.search_input.clear(); self.search_results.clear(); self.search_results.hide()
