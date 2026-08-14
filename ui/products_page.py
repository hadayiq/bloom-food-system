from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QFrame,
    QHeaderView,
    QScrollArea,
)
from PySide6.QtCore import Qt

from database.products import ProductRepository
from database.transactions import TransactionRepository
from utils.refresh_manager import refresh_manager


class ProductsPage(QWidget):

    def __init__(self):
        super().__init__()

        # =====================================================
        # RTL
        # =====================================================

        self.setLayoutDirection(Qt.RightToLeft)

        self.repo = ProductRepository()
        self.transaction_repo = TransactionRepository()

        self.selected_product_id = None

        self.products_data = []

        self.build_ui()

        self.load_products()

        refresh_manager.products_changed.connect(self.refresh_products)

        self.show_table_view()

    # =========================================================
    # BUILD UI
    # =========================================================

    def build_ui(self):

        main_layout = QVBoxLayout(self)

        main_layout.setContentsMargins(
            35,
            30,
            35,
            30,
        )

        main_layout.setSpacing(18)

        # =====================================================
        # TITLE
        # =====================================================

        title = QLabel("إدارة الأصناف")

        title.setObjectName("page_title")

        title.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        subtitle = QLabel("إضافة وتعديل ومتابعة بيانات الأصناف الموجودة بالمخزن")

        subtitle.setObjectName("page_subtitle")

        subtitle.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        main_layout.addWidget(title)
        main_layout.addWidget(subtitle)

        # =====================================================
        # SCROLL AREA
        # =====================================================

        scroll = QScrollArea()

        scroll.setWidgetResizable(True)

        scroll.setFrameShape(QFrame.NoFrame)

        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        scroll.setLayoutDirection(Qt.RightToLeft)

        # =====================================================
        # CONTENT
        # =====================================================

        content = QWidget()

        content.setLayoutDirection(Qt.RightToLeft)

        content_layout = QVBoxLayout(content)

        content_layout.setContentsMargins(
            0,
            10,
            0,
            20,
        )

        content_layout.setSpacing(18)

        # =====================================================
        # TABLE VIEW
        # =====================================================

        self.table_view = QWidget()

        self.table_view.setLayoutDirection(Qt.RightToLeft)

        table_view_layout = QVBoxLayout(self.table_view)

        table_view_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        table_view_layout.setSpacing(15)

        # =====================================================
        # ACTION BAR
        # =====================================================

        action_layout = QHBoxLayout()

        action_layout.setSpacing(10)

        action_layout.setDirection(QBoxLayout.RightToLeft)

        # =====================================================
        # ADD BUTTON
        # =====================================================

        self.add_button = QPushButton("＋  إضافة صنف")

        self.add_button.setObjectName("primary_button")

        self.add_button.setMinimumHeight(45)

        self.add_button.setMinimumWidth(140)

        self.add_button.setCursor(Qt.PointingHandCursor)

        self.add_button.clicked.connect(self.show_add_view)

        action_layout.addWidget(self.add_button)

        # =====================================================
        # EDIT BUTTON
        # =====================================================

        self.edit_button = QPushButton("تعديل")

        self.edit_button.setObjectName("secondary_button")

        self.edit_button.setMinimumHeight(45)

        self.edit_button.setMinimumWidth(100)

        self.edit_button.setCursor(Qt.PointingHandCursor)

        self.edit_button.clicked.connect(self.show_edit_view)

        self.edit_button.hide()

        action_layout.addWidget(self.edit_button)

        # =====================================================
        # DELETE BUTTON
        # =====================================================

        self.delete_button = QPushButton("حذف")

        self.delete_button.setObjectName("danger_button")

        self.delete_button.setMinimumHeight(45)

        self.delete_button.setMinimumWidth(100)

        self.delete_button.setCursor(Qt.PointingHandCursor)

        self.delete_button.clicked.connect(self.delete_product)

        self.delete_button.hide()

        action_layout.addWidget(self.delete_button)

        # =====================================================
        # STRETCH
        # =====================================================

        action_layout.addStretch()

        # =====================================================
        # SEARCH
        # =====================================================

        self.search_input = QLineEdit()

        self.search_input.setPlaceholderText("🔍  ابحث عن صنف بالاسم أو الكود...")

        self.search_input.setMinimumHeight(45)

        self.search_input.setLayoutDirection(Qt.RightToLeft)

        self.search_input.textChanged.connect(self.filter_products)

        action_layout.addWidget(
            self.search_input,
            1,
        )

        table_view_layout.addLayout(action_layout)

        # =====================================================
        # TABLE CARD
        # =====================================================

        table_card = QFrame()

        table_card.setObjectName("dashboard_table_card")

        table_card.setLayoutDirection(Qt.RightToLeft)

        table_card_layout = QVBoxLayout(table_card)

        table_card_layout.setContentsMargins(
            15,
            15,
            15,
            15,
        )

        table_card_layout.setSpacing(0)

        # =====================================================
        # TABLE
        # =====================================================

        self.table = QTableWidget()

        self.table.setObjectName("products_table")

        self.table.setLayoutDirection(Qt.RightToLeft)

        self.table.setColumnCount(4)

        # =====================================================
        # IMPORTANT:
        # RTL COLUMN ORDER
        #
        # من اليمين للشمال:
        #
        # كود الصنف
        # اسم الصنف
        # الوحدة
        # رصيد أول المدة
        # =====================================================

        self.table.setHorizontalHeaderLabels(
            [
                "كود الصنف",
                "اسم الصنف",
                "الوحدة",
                "رصيد أول المدة",
            ]
        )

        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        self.table.setSelectionBehavior(QTableWidget.SelectRows)

        self.table.setSelectionMode(QTableWidget.SingleSelection)

        self.table.verticalHeader().setVisible(False)

        self.table.setAlternatingRowColors(True)

        self.table.setMinimumHeight(350)

        # =====================================================
        # HEADER
        # =====================================================

        header = self.table.horizontalHeader()

        header.setLayoutDirection(Qt.RightToLeft)

        header.setDefaultAlignment(Qt.AlignCenter)

        header.setSectionResizeMode(
            0,
            QHeaderView.ResizeToContents,
        )

        header.setSectionResizeMode(
            1,
            QHeaderView.Stretch,
        )

        header.setSectionResizeMode(
            2,
            QHeaderView.ResizeToContents,
        )

        header.setSectionResizeMode(
            3,
            QHeaderView.ResizeToContents,
        )

        # =====================================================
        # SELECT PRODUCT
        # =====================================================

        self.table.cellClicked.connect(self.select_product)

        table_card_layout.addWidget(self.table)

        table_view_layout.addWidget(table_card)

        table_view_layout.addStretch()

        content_layout.addWidget(self.table_view)

        # =====================================================
        # FORM VIEW
        # =====================================================

        self.form_view = QFrame()

        self.form_view.setObjectName("transaction_card")

        self.form_view.setLayoutDirection(Qt.RightToLeft)

        form_layout = QVBoxLayout(self.form_view)

        form_layout.setContentsMargins(
            30,
            30,
            30,
            30,
        )

        form_layout.setSpacing(12)

        # =====================================================
        # FORM TITLE
        # =====================================================

        self.form_title = QLabel("إضافة صنف جديد")

        self.form_title.setObjectName("section_title")

        self.form_title.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        form_layout.addWidget(self.form_title)

        # =====================================================
        # PRODUCT ID
        # =====================================================

        self.id_label = QLabel("كود الصنف")

        self.id_label.setObjectName("form_label")

        self.id_label.setAlignment(Qt.AlignRight)

        self.id_value = QLabel("-")

        self.id_value.setObjectName("page_subtitle")

        self.id_value.setAlignment(Qt.AlignRight)

        form_layout.addWidget(self.id_label)

        form_layout.addWidget(self.id_value)

        # =====================================================
        # NAME
        # =====================================================

        name_label = QLabel("اسم الصنف")

        name_label.setObjectName("form_label")

        name_label.setAlignment(Qt.AlignRight)

        self.name_input = QLineEdit()

        self.name_input.setPlaceholderText("أدخل اسم الصنف")

        self.name_input.setMinimumHeight(45)

        self.name_input.setAlignment(Qt.AlignRight)

        form_layout.addWidget(name_label)

        form_layout.addWidget(self.name_input)

        # =====================================================
        # UNIT
        # =====================================================

        unit_label = QLabel("الوحدة")

        unit_label.setObjectName("form_label")

        unit_label.setAlignment(Qt.AlignRight)

        self.unit_input = QLineEdit()

        self.unit_input.setPlaceholderText("مثال: كرتونة / قطعة / كيلو")

        self.unit_input.setMinimumHeight(45)

        self.unit_input.setAlignment(Qt.AlignRight)

        form_layout.addWidget(unit_label)

        form_layout.addWidget(self.unit_input)

        # =====================================================
        # OPENING BALANCE
        # =====================================================

        balance_label = QLabel("رصيد أول المدة")

        balance_label.setObjectName("form_label")

        balance_label.setAlignment(Qt.AlignRight)

        self.balance_input = QLineEdit()

        self.balance_input.setPlaceholderText("أدخل رصيد أول المدة")

        self.balance_input.setMinimumHeight(45)

        self.balance_input.setAlignment(Qt.AlignRight)

        form_layout.addWidget(balance_label)

        form_layout.addWidget(self.balance_input)

        # =====================================================
        # FORM BUTTONS
        # =====================================================

        buttons_layout = QHBoxLayout()

        buttons_layout.setDirection(QBoxLayout.RightToLeft)

        buttons_layout.setSpacing(10)

        # Save

        self.save_button = QPushButton("حفظ الصنف")

        self.save_button.setObjectName("primary_button")

        self.save_button.setMinimumHeight(45)

        self.save_button.setMinimumWidth(140)

        self.save_button.setCursor(Qt.PointingHandCursor)

        self.save_button.clicked.connect(self.save_form)

        buttons_layout.addWidget(self.save_button)

        # Cancel

        self.cancel_button = QPushButton("إلغاء")

        self.cancel_button.setObjectName("secondary_button")

        self.cancel_button.setMinimumHeight(45)

        self.cancel_button.setMinimumWidth(100)

        self.cancel_button.setCursor(Qt.PointingHandCursor)

        self.cancel_button.clicked.connect(self.cancel_form)

        buttons_layout.addWidget(self.cancel_button)

        buttons_layout.addStretch()

        form_layout.addLayout(buttons_layout)

        self.form_view.hide()

        content_layout.addWidget(self.form_view)

        # =====================================================
        # FINISH
        # =====================================================

        scroll.setWidget(content)

        main_layout.addWidget(scroll)

    # =========================================================
    # LOAD PRODUCTS
    # =========================================================

    def load_products(self):

        products = self.repo.get_all_products()

        self.products_data = []

        for _, row in products.iterrows():

            product_id = str(row["product_ID"])

            product_name = str(row["Product_Name"])

            unit = str(row["Unit"])

            opening_balance = self.repo.get_opening_balance(product_id)

            self.products_data.append(
                {
                    "id": product_id,
                    "name": product_name,
                    "unit": unit,
                    "opening": opening_balance,
                }
            )

        self.populate_table(self.products_data)

    # =========================================================
    # POPULATE TABLE
    # =========================================================

    def populate_table(
        self,
        products,
    ):

        self.table.setRowCount(len(products))

        for row_index, product in enumerate(products):

            values = [
                product["id"],
                product["name"],
                product["unit"],
                f'{product["opening"]:,.2f}',
            ]

            for column_index, value in enumerate(values):

                item = QTableWidgetItem(str(value))

                item.setTextAlignment(Qt.AlignCenter)

                self.table.setItem(
                    row_index,
                    column_index,
                    item,
                )

    # =========================================================
    # SEARCH
    # =========================================================

    def filter_products(
        self,
        text,
    ):

        text = text.strip().lower()

        if not text:

            self.populate_table(self.products_data)

            return

        matches = []

        for product in self.products_data:

            if text in product["name"].lower() or text in product["id"].lower():

                matches.append(product)

        self.populate_table(matches)

        self.selected_product_id = None

        self.show_action_buttons(False)

    # =========================================================
    # SELECT PRODUCT
    # =========================================================

    def select_product(
        self,
        row,
        column,
    ):

        item = self.table.item(
            row,
            0,
        )

        if item is None:

            return

        self.selected_product_id = item.text()

        self.show_action_buttons(True)

    # =========================================================
    # ACTION BUTTONS
    # =========================================================

    def show_action_buttons(
        self,
        selected,
    ):

        self.add_button.setVisible(not selected)

        self.edit_button.setVisible(selected)

        self.delete_button.setVisible(selected)

    # =========================================================
    # SHOW ADD VIEW
    # =========================================================

    def show_add_view(self):

        self.selected_product_id = None

        self.form_title.setText("إضافة صنف جديد")

        self.id_label.hide()

        self.id_value.hide()

        self.name_input.clear()

        self.unit_input.clear()

        self.balance_input.clear()

        self.table_view.hide()

        self.form_view.show()

        self.name_input.setFocus()

    # =========================================================
    # SHOW EDIT VIEW
    # =========================================================

    def show_edit_view(self):

        if not self.selected_product_id:

            return

        product = None

        for item in self.products_data:

            if item["id"] == self.selected_product_id:

                product = item

                break

        if product is None:

            return

        self.form_title.setText("تعديل بيانات الصنف")

        self.id_label.show()

        self.id_value.show()

        self.id_value.setText(product["id"])

        self.name_input.setText(product["name"])

        self.unit_input.setText(product["unit"])

        self.balance_input.setText(str(product["opening"]))

        self.table_view.hide()

        self.form_view.show()

        self.name_input.setFocus()

    # =========================================================
    # SAVE FORM
    # =========================================================

    def save_form(self):

        name = self.name_input.text().strip()

        unit = self.unit_input.text().strip()

        balance_text = self.balance_input.text().strip()

        # =====================================================
        # VALIDATION
        # =====================================================

        if not name:

            QMessageBox.warning(
                self,
                "خطأ",
                "اسم الصنف مطلوب.",
            )

            return

        if not unit:

            QMessageBox.warning(
                self,
                "خطأ",
                "الوحدة مطلوبة.",
            )

            return

        if not balance_text:

            balance = 0

        else:

            try:

                balance = float(balance_text)

            except ValueError:

                QMessageBox.warning(
                    self,
                    "خطأ",
                    "رصيد أول المدة يجب أن يكون رقمًا.",
                )

                return

        # =====================================================
        # EDIT
        # =====================================================

        if self.selected_product_id:

            try:

                self.repo.update_product(
                    self.selected_product_id,
                    name,
                    unit,
                    balance,
                )

            except Exception as e:

                QMessageBox.critical(
                    self,
                    "خطأ",
                    f"حدث خطأ أثناء تعديل الصنف:\n{e}",
                )

                return

            QMessageBox.information(
                self,
                "تم التعديل",
                "تم تعديل بيانات الصنف بنجاح.",
            )

        # =====================================================
        # ADD
        # =====================================================

        else:

            if self.repo.product_exists(name):

                QMessageBox.warning(
                    self,
                    "خطأ",
                    "هذا الصنف موجود بالفعل.",
                )

                return

            try:

                self.repo.add_product(
                    name,
                    unit,
                    balance,
                )

            except Exception as e:

                QMessageBox.critical(
                    self,
                    "خطأ",
                    f"حدث خطأ أثناء إضافة الصنف:\n{e}",
                )

                return

            QMessageBox.information(
                self,
                "تمت الإضافة",
                "تم إضافة الصنف بنجاح.",
            )

        self.load_products()

        self.cancel_form()

    # =========================================================
    # DELETE
    # =========================================================

    def delete_product(self):

        if not self.selected_product_id:

            QMessageBox.warning(
                self,
                "خطأ",
                "اختر صنفًا أولاً.",
            )

            return

        product = None

        for item in self.products_data:

            if item["id"] == self.selected_product_id:

                product = item

                break

        if product is None:

            return

        product_name = product["name"]

        # =====================================================
        # CHECK TRANSACTIONS
        # =====================================================

        if self.transaction_repo.product_has_transactions(product_name):

            QMessageBox.warning(
                self,
                "لا يمكن الحذف",
                "لا يمكن حذف هذا الصنف لأنه يحتوي على حركات مخزنية.",
            )

            return

        # =====================================================
        # CONFIRM
        # =====================================================

        reply = QMessageBox.question(
            self,
            "تأكيد حذف الصنف",
            (
                "هل أنت متأكد من حذف الصنف؟\n\n"
                f"الكود: {product['id']}\n"
                f"الصنف: {product_name}"
            ),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply != QMessageBox.Yes:

            return

        try:

            self.repo.delete_product(self.selected_product_id)

        except Exception as e:

            QMessageBox.critical(
                self,
                "خطأ",
                f"حدث خطأ أثناء حذف الصنف:\n{e}",
            )

            return

        QMessageBox.information(
            self,
            "تم الحذف",
            "تم حذف الصنف بنجاح.",
        )

        self.selected_product_id = None

        self.load_products()

        self.show_table_view()

    # =========================================================
    # CANCEL FORM
    # =========================================================

    def cancel_form(self):

        self.selected_product_id = None

        self.name_input.clear()

        self.unit_input.clear()

        self.balance_input.clear()

        self.form_view.hide()

        self.show_table_view()

    # =========================================================
    # SHOW TABLE
    # =========================================================

    def show_table_view(self):

        self.form_view.hide()

        self.table_view.show()

        self.selected_product_id = None

        self.table.clearSelection()

        self.show_action_buttons(False)

        self.search_input.setFocus()

    # =========================================================
    # REFRESH
    # =========================================================

    def refresh_products(self):

        current_search = (
            self.search_input.text()
            if hasattr(
                self,
                "search_input",
            )
            else ""
        )

        self.load_products()

        if current_search:

            self.search_input.setText(current_search)

        else:

            self.show_table_view()
