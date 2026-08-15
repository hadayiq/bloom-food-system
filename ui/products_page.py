from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QBoxLayout,
    QDoubleSpinBox,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from database.products import ProductRepository
from database.transactions import TransactionRepository
from utils.refresh_manager import refresh_manager
from ui.add_batch_dialog import AddBatchDialog


class ProductsPage(QWidget):
    """Product administration plus batch creation entry point."""

    def __init__(self):
        super().__init__()
        self.setLayoutDirection(Qt.RightToLeft)

        self.repo = ProductRepository()
        self.transaction_repo = TransactionRepository()
        self.selected_product_id = None
        self.products_data = []

        self.build_ui()
        self.load_products()

        refresh_manager.products_changed.connect(self.refresh_products)
        refresh_manager.data_changed.connect(self.refresh_products)
        self.show_table_view()

    def build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(35, 30, 35, 30)
        main_layout.setSpacing(18)

        title = QLabel("إدارة الأصناف")
        title.setObjectName("page_title")
        subtitle = QLabel("إضافة وتعديل ومتابعة الأصناف والباتشات")
        subtitle.setObjectName("page_subtitle")
        main_layout.addWidget(title)
        main_layout.addWidget(subtitle)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 10, 0, 20)
        content_layout.setSpacing(18)

        self.table_view = QWidget()
        table_view_layout = QVBoxLayout(self.table_view)
        table_view_layout.setContentsMargins(0, 0, 0, 0)
        table_view_layout.setSpacing(15)

        action_layout = QHBoxLayout()
        action_layout.setDirection(QBoxLayout.RightToLeft)
        action_layout.setSpacing(10)

        self.add_button = QPushButton("＋  إضافة صنف")
        self.add_button.setObjectName("primary_button")
        self.add_button.setMinimumHeight(45)
        self.add_button.clicked.connect(self.show_add_view)
        action_layout.addWidget(self.add_button)

        self.batch_button = QPushButton("＋  إضافة باتش")
        self.batch_button.setObjectName("secondary_button")
        self.batch_button.setMinimumHeight(45)
        self.batch_button.clicked.connect(self.open_batch_dialog)
        action_layout.addWidget(self.batch_button)

        self.edit_button = QPushButton("تعديل")
        self.edit_button.setObjectName("secondary_button")
        self.edit_button.setMinimumHeight(45)
        self.edit_button.hide()
        self.edit_button.clicked.connect(self.show_edit_view)
        action_layout.addWidget(self.edit_button)

        self.delete_button = QPushButton("حذف")
        self.delete_button.setObjectName("danger_button")
        self.delete_button.setMinimumHeight(45)
        self.delete_button.hide()
        self.delete_button.clicked.connect(self.delete_product)
        action_layout.addWidget(self.delete_button)

        action_layout.addStretch()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍  ابحث عن صنف بالاسم أو الكود...")
        self.search_input.setMinimumHeight(45)
        self.search_input.textChanged.connect(self.filter_products)
        action_layout.addWidget(self.search_input, 1)
        table_view_layout.addLayout(action_layout)

        table_card = QFrame()
        table_card.setObjectName("dashboard_table_card")
        table_card_layout = QVBoxLayout(table_card)
        table_card_layout.setContentsMargins(15, 15, 15, 15)

        self.table = QTableWidget()
        self.table.setObjectName("products_table")
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["كود الصنف", "اسم الصنف", "الوحدة", "رصيد أول المدة"])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setMinimumHeight(350)
        self.table.cellClicked.connect(self.select_product)

        header = self.table.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignCenter)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)

        table_card_layout.addWidget(self.table)
        table_view_layout.addWidget(table_card)
        content_layout.addWidget(self.table_view)

        self.form_view = QFrame()
        self.form_view.setObjectName("transaction_card")
        form_layout = QVBoxLayout(self.form_view)
        form_layout.setContentsMargins(30, 30, 30, 30)
        form_layout.setSpacing(12)

        self.form_title = QLabel("إضافة صنف جديد")
        self.form_title.setObjectName("section_title")
        form_layout.addWidget(self.form_title)

        self.id_label = QLabel("كود الصنف")
        self.id_label.setObjectName("form_label")
        self.id_value = QLabel("-")
        self.id_value.setObjectName("page_subtitle")
        form_layout.addWidget(self.id_label)
        form_layout.addWidget(self.id_value)

        name_label = QLabel("اسم الصنف")
        name_label.setObjectName("form_label")
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("أدخل اسم الصنف")
        self.name_input.setMinimumHeight(45)
        form_layout.addWidget(name_label)
        form_layout.addWidget(self.name_input)

        unit_label = QLabel("الوحدة")
        unit_label.setObjectName("form_label")
        self.unit_input = QLineEdit()
        self.unit_input.setPlaceholderText("مثال: كرتونة / قطعة / كيلو")
        self.unit_input.setMinimumHeight(45)
        form_layout.addWidget(unit_label)
        form_layout.addWidget(self.unit_input)

        balance_label = QLabel("رصيد أول المدة")
        balance_label.setObjectName("form_label")
        self.balance_input = QDoubleSpinBox()
        self.balance_input.setRange(0.0, 999999999.0)
        self.balance_input.setDecimals(3)
        self.balance_input.setMinimumHeight(45)
        form_layout.addWidget(balance_label)
        form_layout.addWidget(self.balance_input)

        buttons_layout = QHBoxLayout()
        buttons_layout.setDirection(QBoxLayout.RightToLeft)

        self.save_button = QPushButton("حفظ الصنف")
        self.save_button.setObjectName("primary_button")
        self.save_button.setMinimumHeight(45)
        self.save_button.clicked.connect(self.save_form)
        buttons_layout.addWidget(self.save_button)

        self.cancel_button = QPushButton("إلغاء")
        self.cancel_button.setObjectName("secondary_button")
        self.cancel_button.setMinimumHeight(45)
        self.cancel_button.clicked.connect(self.cancel_form)
        buttons_layout.addWidget(self.cancel_button)
        buttons_layout.addStretch()
        form_layout.addLayout(buttons_layout)

        self.form_view.hide()
        content_layout.addWidget(self.form_view)
        content_layout.addStretch()

        scroll.setWidget(content)
        main_layout.addWidget(scroll)

    def load_products(self):
        products = self.repo.get_all_products()
        self.products_data = []
        for _, row in products.iterrows():
            product_id = str(row["product_ID"])
            self.products_data.append({
                "id": product_id,
                "name": str(row["Product_Name"]),
                "unit": str(row["Unit"]),
                "opening": self.repo.get_opening_balance(product_id),
            })
        self.populate_table(self.products_data)

    def populate_table(self, products):
        self.table.setRowCount(len(products))
        for row_index, product in enumerate(products):
            values = [product["id"], product["name"], product["unit"], f'{product["opening"]:,.3f}']
            for column_index, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row_index, column_index, item)

    def filter_products(self, text):
        text = text.strip().lower()
        if not text:
            self.populate_table(self.products_data)
            return
        matches = [
            product for product in self.products_data
            if text in product["name"].lower() or text in product["id"].lower()
        ]
        self.populate_table(matches)
        self.selected_product_id = None
        self.show_action_buttons(False)

    def select_product(self, row, column):
        item = self.table.item(row, 0)
        if item is None:
            return
        self.selected_product_id = item.text()
        self.show_action_buttons(True)

    def show_action_buttons(self, selected):
        self.add_button.setVisible(not selected)
        self.edit_button.setVisible(selected)
        self.delete_button.setVisible(selected)

    def open_batch_dialog(self):
        dialog = AddBatchDialog(self, self.selected_product_id)
        dialog.exec()

    def show_add_view(self):
        self.selected_product_id = None
        self.form_title.setText("إضافة صنف جديد")
        self.id_label.hide()
        self.id_value.hide()
        self.name_input.clear()
        self.unit_input.clear()
        self.balance_input.setValue(0)
        self.table_view.hide()
        self.form_view.show()
        self.name_input.setFocus()

    def show_edit_view(self):
        if not self.selected_product_id:
            return
        product = next((p for p in self.products_data if p["id"] == self.selected_product_id), None)
        if product is None:
            return
        self.form_title.setText("تعديل بيانات الصنف")
        self.id_label.show()
        self.id_value.show()
        self.id_value.setText(product["id"])
        self.name_input.setText(product["name"])
        self.unit_input.setText(product["unit"])
        self.balance_input.setValue(product["opening"])
        self.table_view.hide()
        self.form_view.show()
        self.name_input.setFocus()

    def save_form(self):
        name = self.name_input.text().strip()
        unit = self.unit_input.text().strip()
        balance = self.balance_input.value()

        if not name:
            QMessageBox.warning(self, "خطأ", "اسم الصنف مطلوب.")
            return
        if not unit:
            QMessageBox.warning(self, "خطأ", "الوحدة مطلوبة.")
            return

        try:
            if self.selected_product_id:
                self.repo.update_product(self.selected_product_id, name, unit, balance)
                message = "تم تعديل بيانات الصنف بنجاح."
            else:
                if self.repo.product_exists(name):
                    QMessageBox.warning(self, "خطأ", "هذا الصنف موجود بالفعل.")
                    return
                self.repo.add_product(name, unit, balance)
                message = "تم إضافة الصنف بنجاح."
        except Exception as exc:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء حفظ الصنف:\n{exc}")
            return

        QMessageBox.information(self, "تم", message)
        self.load_products()
        self.cancel_form()

    def delete_product(self):
        if not self.selected_product_id:
            QMessageBox.warning(self, "خطأ", "اختر صنفًا أولاً.")
            return

        product = next((p for p in self.products_data if p["id"] == self.selected_product_id), None)
        if product is None:
            return

        if self.transaction_repo.product_has_transactions(product["name"]):
            QMessageBox.warning(self, "لا يمكن الحذف", "لا يمكن حذف هذا الصنف لأنه يحتوي على حركات مخزنية.")
            return

        reply = QMessageBox.question(
            self,
            "تأكيد حذف الصنف",
            f"هل أنت متأكد من حذف الصنف؟\n\nالكود: {product['id']}\nالصنف: {product['name']}",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        try:
            self.repo.delete_product(self.selected_product_id)
        except Exception as exc:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء حذف الصنف:\n{exc}")
            return

        QMessageBox.information(self, "تم الحذف", "تم حذف الصنف بنجاح.")
        self.selected_product_id = None
        self.load_products()
        self.show_table_view()

    def cancel_form(self):
        self.name_input.clear()
        self.unit_input.clear()
        self.balance_input.setValue(0)
        self.form_view.hide()
        self.show_table_view()

    def show_table_view(self):
        self.form_view.hide()
        self.table_view.show()
        self.selected_product_id = None
        self.table.clearSelection()
        self.show_action_buttons(False)

    def refresh_products(self):
        current_search = self.search_input.text() if hasattr(self, "search_input") else ""
        self.load_products()
        if current_search:
            self.search_input.setText(current_search)
