from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QLineEdit,
    QTextEdit,
    QMessageBox,
    QFrame,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QScrollArea,
    QStyle,
    QDoubleSpinBox,
)
from PySide6.QtCore import Qt

from database.products import ProductRepository
from database.transactions import TransactionRepository
from database.batches import BatchRepository
from utils.refresh_manager import refresh_manager


class AddTransactionPage(QWidget):

    def __init__(self):
        super().__init__()
        self.product_repo = ProductRepository()
        self.transaction_repo = TransactionRepository()
        self.batch_repo = BatchRepository()
        self.build_ui()
        self.load_products()
        refresh_manager.products_changed.connect(self.reload_products)
        refresh_manager.data_changed.connect(self.refresh_page)
        self.show_start_view()

    def build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(35, 30, 35, 30)
        content_layout.setSpacing(18)

        header_layout = QVBoxLayout()
        header_layout.setSpacing(3)
        self.title = QLabel("الحركات المخزنية")
        self.title.setObjectName("page_title")
        self.subtitle = QLabel("إضافة ومتابعة الحركات الخاصة بالأصناف")
        self.subtitle.setObjectName("page_subtitle")
        header_layout.addWidget(self.title)
        header_layout.addWidget(self.subtitle)
        content_layout.addLayout(header_layout)

        self.start_view = QWidget()
        start_layout = QVBoxLayout(self.start_view)
        start_layout.setContentsMargins(0, 20, 0, 0)
        start_layout.setSpacing(20)

        new_card = QFrame()
        new_card.setObjectName("transaction_card")
        new_layout = QVBoxLayout(new_card)
        new_layout.setContentsMargins(25, 25, 25, 25)
        new_layout.setSpacing(8)
        new_title = QLabel("إضافة حركة جديدة")
        new_title.setObjectName("section_title")
        new_description = QLabel("قم بتسجيل حركة مخزنية جديدة على أحد الأصناف")
        new_description.setObjectName("section_description")
        self.new_button = QPushButton("＋  حركة جديدة")
        self.new_button.setObjectName("primary_button")
        self.new_button.setMinimumHeight(50)
        self.new_button.setCursor(Qt.PointingHandCursor)
        self.new_button.clicked.connect(self.show_form_view)
        new_layout.addWidget(new_title)
        new_layout.addWidget(new_description)
        new_layout.addSpacing(10)
        new_layout.addWidget(self.new_button)
        start_layout.addWidget(new_card)

        recent_title_layout = QHBoxLayout()
        recent_title = QLabel("آخر الحركات")
        recent_title.setObjectName("section_title")
        recent_title_layout.addStretch()
        recent_title_layout.addWidget(recent_title)
        start_layout.addLayout(recent_title_layout)

        self.recent_table = QTableWidget()
        self.recent_table.setColumnCount(6)
        self.recent_table.setHorizontalHeaderLabels(
            ["التاريخ", "الصنف", "الباتش", "الحركة", "الكمية", "ملاحظات"]
        )
        self.recent_table.setAlternatingRowColors(True)
        self.recent_table.setShowGrid(False)
        self.recent_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.recent_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.recent_table.setSelectionMode(QTableWidget.SingleSelection)
        self.recent_table.verticalHeader().setVisible(False)
        self.recent_table.verticalHeader().setDefaultSectionSize(44)
        header = self.recent_table.horizontalHeader()
        header.setHighlightSections(False)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.Stretch)
        start_layout.addWidget(self.recent_table)
        content_layout.addWidget(self.start_view)

        self.form_view = QWidget()
        form_main_layout = QVBoxLayout(self.form_view)
        form_main_layout.setContentsMargins(0, 20, 0, 0)
        form_main_layout.setSpacing(18)

        back_layout = QHBoxLayout()
        self.back_button = QPushButton("← رجوع")
        self.back_button.setObjectName("secondary_button")
        self.back_button.setCursor(Qt.PointingHandCursor)
        self.back_button.clicked.connect(self.show_start_view)
        back_layout.addWidget(self.back_button)
        back_layout.addStretch()
        form_main_layout.addLayout(back_layout)

        product_card = QFrame()
        product_card.setObjectName("transaction_card")
        product_layout = QVBoxLayout(product_card)
        product_layout.setContentsMargins(25, 25, 25, 25)
        product_layout.setSpacing(10)

        product_label = QLabel("الصنف")
        product_label.setObjectName("form_label")
        self.product_combo = QComboBox()
        self.product_combo.setMinimumHeight(45)
        self.product_combo.currentIndexChanged.connect(self.product_selected)
        product_layout.addWidget(product_label)
        product_layout.addWidget(self.product_combo)

        self.batch_label = QLabel("الباتش")
        self.batch_label.setObjectName("form_label")
        self.batch_combo = QComboBox()
        self.batch_combo.setMinimumHeight(45)
        self.batch_combo.addItem("اختر الباتش")
        self.batch_combo.currentIndexChanged.connect(self.batch_selected)
        product_layout.addWidget(self.batch_label)
        product_layout.addWidget(self.batch_combo)
        self.batch_label.hide()
        self.batch_combo.hide()
        self.batch_hint = QLabel("")
        self.batch_hint.setObjectName("section_description")
        product_layout.addWidget(self.batch_hint)
        form_main_layout.addWidget(product_card)

        self.summary_container = QWidget()
        summary_layout = QHBoxLayout(self.summary_container)
        summary_layout.setContentsMargins(0, 0, 0, 0)
        summary_layout.setSpacing(15)
        self.incoming_card, self.incoming_value = self.create_summary_card("الوارد", "0.00", "kpi_green", QStyle.SP_ArrowDown)
        self.outgoing_card, self.outgoing_value = self.create_summary_card("المنصرف", "0.00", "kpi_blue", QStyle.SP_ArrowUp)
        self.balance_card, self.balance_value = self.create_summary_card("المتبقي", "0.00", "kpi_orange", QStyle.SP_DriveHDIcon)
        summary_layout.addWidget(self.incoming_card)
        summary_layout.addWidget(self.outgoing_card)
        summary_layout.addWidget(self.balance_card)
        form_main_layout.addWidget(self.summary_container)

        input_card = QFrame()
        input_card.setObjectName("transaction_card")
        input_layout = QVBoxLayout(input_card)
        input_layout.setContentsMargins(25, 25, 25, 25)
        input_layout.setSpacing(10)

        type_label = QLabel("نوع الحركة")
        type_label.setObjectName("form_label")
        self.type_combo = QComboBox()
        self.type_combo.setMinimumHeight(45)
        self.type_combo.addItem("اختر نوع الحركة")
        self.type_combo.addItems(["إنتاج", "مشتريات", "صرف للتجزئة", "صرف للتسليمات", "مردودات مبيعات"])
        input_layout.addWidget(type_label)
        input_layout.addWidget(self.type_combo)

        quantity_label = QLabel("الكمية")
        quantity_label.setObjectName("form_label")
        self.quantity_input = QDoubleSpinBox()
        self.quantity_input.setMinimumHeight(45)
        self.quantity_input.setRange(0.0, 999999999.0)
        self.quantity_input.setDecimals(2)
        self.quantity_input.setSingleStep(1.0)
        self.quantity_input.setValue(0.0)
        self.quantity_input.setButtonSymbols(QDoubleSpinBox.NoButtons)
        input_layout.addWidget(quantity_label)
        input_layout.addWidget(self.quantity_input)

        notes_label = QLabel("ملاحظات")
        notes_label.setObjectName("form_label")
        self.notes_input = QTextEdit()
        self.notes_input.setMinimumHeight(100)
        self.notes_input.setPlaceholderText("أضف ملاحظات إن وجدت...")
        input_layout.addWidget(notes_label)
        input_layout.addWidget(self.notes_input)

        save_layout = QHBoxLayout()
        save_layout.addStretch()
        self.save_button = QPushButton("حفظ الحركة")
        self.save_button.setObjectName("primary_button")
        self.save_button.setMinimumHeight(48)
        self.save_button.setMinimumWidth(170)
        self.save_button.setCursor(Qt.PointingHandCursor)
        self.save_button.clicked.connect(self.save_transaction)
        save_layout.addWidget(self.save_button)
        input_layout.addLayout(save_layout)
        form_main_layout.addWidget(input_card)
        form_main_layout.addStretch()
        content_layout.addWidget(self.form_view)

        scroll.setWidget(content)
        main_layout.addWidget(scroll)

    def create_summary_card(self, title, value, style_class, icon_type):
        card = QFrame()
        card.setObjectName("kpi_card")
        card.setProperty("class", style_class)
        layout = QVBoxLayout()
        layout.setContentsMargins(18, 12, 18, 12)
        layout.setSpacing(4)
        icon_label = QLabel()
        icon_label.setObjectName("kpi_icon")
        icon = self.style().standardIcon(icon_type)
        icon_label.setPixmap(icon.pixmap(28, 28))
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
        card.setLayout(layout)
        return card, value_label

    def load_products(self):
        self.product_combo.clear()
        self.product_combo.addItem("اختر الصنف")
        products = self.product_repo.get_product_names()
        if products:
            self.product_combo.addItems(products)
        self.product_combo.setCurrentIndex(0)

    def product_selected(self):
        if self.product_combo.currentIndex() == 0:
            self.batch_label.hide()
            self.batch_combo.hide()
            self.batch_hint.clear()
            self.summary_container.hide()
            return

        product = self.product_combo.currentText()
        product_id = self.product_repo.get_product_id(product)
        batches = self.batch_repo.get_batches(product_id) if product_id is not None else []

        self.batch_combo.blockSignals(True)
        self.batch_combo.clear()
        self.batch_combo.addItem("اختر الباتش")
        for batch in batches:
            code = str(batch["code"])
            expiry = batch["expiry_date"]
            self.batch_combo.addItem(f"{code}  |  صلاحية: {expiry}", code)
        self.batch_combo.setCurrentIndex(0)
        self.batch_combo.blockSignals(False)

        has_batches = bool(batches)
        self.batch_label.setVisible(has_batches)
        self.batch_combo.setVisible(has_batches)
        self.batch_hint.setText("اختيار الباتش إلزامي لهذا الصنف." if has_batches else "هذا الصنف لا يحتوي على باتشات حالياً.")

        self.update_product_summary(product)

    def batch_selected(self):
        if self.batch_combo.currentIndex() == 0:
            if self.product_combo.currentIndex() != 0:
                self.update_product_summary(self.product_combo.currentText())
            return
        product = self.product_combo.currentText()
        batch_code = self.batch_combo.currentData()
        try:
            total_in, total_out, balance = self.transaction_repo.get_batch_balance(product, batch_code)
            self.incoming_value.setText(f"{total_in + self.batch_repo.get_opening_balance(self.product_repo.get_product_id(product), batch_code):,.2f}")
            self.outgoing_value.setText(f"{total_out:,.2f}")
            self.balance_value.setText(f"{balance:,.2f}")
            self.summary_container.show()
        except Exception as e:
            print("Error getting batch balance:", e)
            self.summary_container.hide()

    def update_product_summary(self, product):
        try:
            total_in, total_out, balance = self.transaction_repo.get_product_balance(product)
            self.incoming_value.setText(f"{total_in:,.2f}")
            self.outgoing_value.setText(f"{total_out:,.2f}")
            self.balance_value.setText(f"{balance:,.2f}")
            self.summary_container.show()
        except Exception as e:
            print("Error getting product balance:", e)
            self.summary_container.hide()

    def show_start_view(self):
        self.start_view.show()
        self.form_view.hide()
        self.load_recent_transactions()

    def show_form_view(self):
        self.start_view.hide()
        self.form_view.show()
        self.product_combo.setCurrentIndex(0)
        self.type_combo.setCurrentIndex(0)
        self.batch_combo.clear()
        self.batch_combo.addItem("اختر الباتش")
        self.batch_label.hide()
        self.batch_combo.hide()
        self.batch_hint.clear()
        self.quantity_input.setValue(0.0)
        self.notes_input.clear()
        self.summary_container.hide()
        self.product_combo.setFocus()

    def reload_products(self):
        current = self.product_combo.currentText() if self.product_combo.count() else ""
        self.load_products()
        index = self.product_combo.findText(current)
        if index >= 0:
            self.product_combo.setCurrentIndex(index)

    def load_recent_transactions(self):
        transactions = []
        try:
            import openpyxl
            workbook = openpyxl.load_workbook(self.transaction_repo.file, read_only=True, data_only=True)
            sheet = workbook["Transactions"]
            for row in sheet.iter_rows(min_row=2, values_only=True):
                if row:
                    transactions.append(row)
            workbook.close()
        except Exception as e:
            print("Error loading transactions:", e)
            self.recent_table.setRowCount(0)
            return

        transactions = list(reversed(transactions[-10:]))
        self.recent_table.setRowCount(len(transactions))
        for row_index, row in enumerate(transactions):
            date = row[1] if len(row) > 1 and row[1] is not None else ""
            time = row[2] if len(row) > 2 and row[2] is not None else ""
            product = row[3] if len(row) > 3 else ""
            transaction_type = row[4] if len(row) > 4 else ""
            quantity = row[5] if len(row) > 5 else 0
            notes = row[6] if len(row) > 6 else ""
            batch = row[7] if len(row) > 7 else ""
            try:
                quantity_text = f"{float(quantity):,.2f}"
            except (ValueError, TypeError):
                quantity_text = str(quantity)
            values = [f"{date} {time}".strip(), product, batch or "—", transaction_type, quantity_text, notes or ""]
            for column_index, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment((Qt.AlignCenter | Qt.AlignVCenter) if column_index in [0, 2, 3, 4] else (Qt.AlignRight | Qt.AlignVCenter))
                if column_index == 3:
                    if transaction_type in ["إنتاج", "مشتريات", "مردودات مبيعات"]:
                        item.setForeground(Qt.darkGreen)
                    elif transaction_type in ["صرف للتجزئة", "صرف للتسليمات"]:
                        item.setForeground(Qt.blue)
                self.recent_table.setItem(row_index, column_index, item)

    def save_transaction(self):
        if self.product_combo.currentIndex() == 0:
            QMessageBox.warning(self, "خطأ", "اختر الصنف.")
            return
        if self.type_combo.currentIndex() == 0:
            QMessageBox.warning(self, "خطأ", "اختر نوع الحركة.")
            return

        quantity = float(self.quantity_input.value())
        if quantity <= 0:
            QMessageBox.warning(self, "خطأ", "الكمية يجب أن تكون أكبر من صفر.")
            return

        product = self.product_combo.currentText()
        transaction_type = self.type_combo.currentText()
        notes = self.notes_input.toPlainText().strip()
        batch_code = self.batch_combo.currentData() if self.batch_combo.isVisible() else None

        if self.batch_combo.isVisible() and not batch_code:
            QMessageBox.warning(self, "خطأ", "اختر الباتش أولاً.")
            return

        if transaction_type in ["صرف للتجزئة", "صرف للتسليمات"]:
            if not self.transaction_repo.check_stock(product, quantity, batch_code):
                QMessageBox.warning(self, "الرصيد غير كافٍ", "الكمية المطلوبة أكبر من الرصيد المتاح في الباتش.")
                return

        try:
            self.transaction_repo.save_transaction(product, transaction_type, quantity, notes, batch_code)
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء حفظ الحركة:\n{e}")
            return

        refresh_manager.data_changed.emit()
        QMessageBox.information(self, "تم الحفظ", "تم حفظ الحركة بنجاح.")
        self.show_start_view()

    def refresh_page(self):
        if self.product_combo.currentIndex() != 0:
            self.product_selected()
        self.load_recent_transactions()
