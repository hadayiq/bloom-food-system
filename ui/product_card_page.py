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
    QListWidget,
    QListWidgetItem,
    QBoxLayout,
)

from PySide6.QtCore import Qt

from database.products import ProductRepository
from database.transactions import TransactionRepository
from utils.refresh_manager import refresh_manager


class ProductCardPage(QWidget):

    def __init__(self):
        super().__init__()

        # =====================================================
        # RTL
        # =====================================================

        self.setLayoutDirection(Qt.RightToLeft)

        self.product_repo = ProductRepository()
        self.transaction_repo = TransactionRepository()

        self.selected_transaction_id = None
        self.selected_product = None
        self.products_data = []

        self.build_ui()
        self.load_products()

        refresh_manager.products_changed.connect(self.reload_products)

        refresh_manager.data_changed.connect(self.refresh_page)

        self.show_search_view()

    # =========================================================
    # BUILD UI
    # =========================================================

    def build_ui(self):

        outer_layout = QVBoxLayout(self)

        outer_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        # =====================================================
        # SCROLL AREA
        # =====================================================

        self.scroll_area = QScrollArea()

        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QScrollArea.NoFrame)

        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.scroll_area.setLayoutDirection(Qt.RightToLeft)

        # =====================================================
        # SCROLL CONTENT
        # =====================================================

        content = QWidget()

        content.setLayoutDirection(Qt.RightToLeft)

        main_layout = QVBoxLayout(content)

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

        self.title = QLabel("كارت الصنف")

        self.title.setObjectName("page_title")

        self.title.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        main_layout.addWidget(self.title)

        # =====================================================
        # SUBTITLE
        # =====================================================

        self.subtitle = QLabel("ابحث عن الصنف لمتابعة بياناته وحركاته المخزنية")

        self.subtitle.setObjectName("page_subtitle")

        self.subtitle.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        main_layout.addWidget(self.subtitle)

        # =====================================================
        # SEARCH VIEW
        # =====================================================

        self.search_view = QWidget()

        self.search_view.setLayoutDirection(Qt.RightToLeft)

        search_view_layout = QVBoxLayout(self.search_view)

        search_view_layout.setContentsMargins(
            0,
            70,
            0,
            70,
        )

        search_view_layout.setSpacing(15)

        # =====================================================
        # SEARCH TITLE
        # =====================================================

        search_title = QLabel("ابحث عن الصنف")

        search_title.setObjectName("search_page_title")

        search_title.setAlignment(Qt.AlignCenter)

        search_view_layout.addWidget(search_title)

        # =====================================================
        # SEARCH SUBTITLE
        # =====================================================

        search_subtitle = QLabel("اكتب اسم الصنف أو كود الصنف للبدء")

        search_subtitle.setObjectName("search_page_subtitle")

        search_subtitle.setAlignment(Qt.AlignCenter)

        search_view_layout.addWidget(search_subtitle)

        # =====================================================
        # SEARCH BOX
        # =====================================================

        self.search_input = QLineEdit()

        self.search_input.setObjectName("product_search")

        self.search_input.setPlaceholderText("🔍  ابحث عن صنف...")

        self.search_input.setMinimumHeight(58)

        self.search_input.setAlignment(Qt.AlignRight)

        self.search_input.textChanged.connect(self.filter_products)

        self.search_input.returnPressed.connect(self.select_first_search_result)

        search_view_layout.addWidget(self.search_input)

        # =====================================================
        # SEARCH RESULTS
        # =====================================================

        self.search_results = QListWidget()

        self.search_results.setObjectName("product_search_results")

        self.search_results.setMaximumHeight(230)

        self.search_results.setLayoutDirection(Qt.RightToLeft)

        self.search_results.hide()

        self.search_results.itemClicked.connect(self.select_search_result)

        search_view_layout.addWidget(self.search_results)

        main_layout.addWidget(self.search_view)

        # =====================================================
        # PRODUCT VIEW
        # =====================================================

        self.product_view = QWidget()

        self.product_view.setLayoutDirection(Qt.RightToLeft)

        product_layout = QVBoxLayout(self.product_view)

        product_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        product_layout.setSpacing(18)

        # =====================================================
        # TOP SEARCH
        # =====================================================

        self.top_search_container = QFrame()

        self.top_search_container.setObjectName("top_search_container")

        self.top_search_container.setLayoutDirection(Qt.RightToLeft)

        top_search_layout = QHBoxLayout(self.top_search_container)

        top_search_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        self.top_search = QLineEdit()

        self.top_search.setObjectName("top_product_search")

        self.top_search.setPlaceholderText("🔍  ابحث عن صنف آخر...")

        self.top_search.setMinimumHeight(48)

        self.top_search.setAlignment(Qt.AlignRight)

        self.top_search.textChanged.connect(self.filter_top_products)

        self.top_search.returnPressed.connect(self.select_first_top_result)

        top_search_layout.addWidget(self.top_search)

        product_layout.addWidget(self.top_search_container)

        # =====================================================
        # TOP SEARCH RESULTS
        # =====================================================

        self.top_search_results = QListWidget()

        self.top_search_results.setObjectName("top_product_search_results")

        self.top_search_results.setMaximumHeight(200)

        self.top_search_results.setLayoutDirection(Qt.RightToLeft)

        self.top_search_results.hide()

        self.top_search_results.itemClicked.connect(self.select_top_search_result)

        product_layout.addWidget(self.top_search_results)

        # =====================================================
        # PRODUCT INFORMATION
        # =====================================================

        cards_layout = QHBoxLayout()

        cards_layout.setSpacing(12)

        cards_layout.setDirection(
            QBoxLayout.RightToLeft if False else QBoxLayout.LeftToRight
        )

        self.code_card, self.code_value = self.create_info_card(
            "كود الصنف",
            "-",
            "kpi_purple",
        )

        self.name_card, self.name_value = self.create_info_card(
            "اسم الصنف",
            "-",
            "kpi_blue",
        )

        self.unit_card, self.unit_value = self.create_info_card(
            "الوحدة",
            "-",
            "kpi_orange",
        )

        self.opening_card, self.opening_value = self.create_info_card(
            "رصيد أول المدة",
            "0.00",
            "kpi_green",
        )

        self.balance_card, self.balance_value = self.create_info_card(
            "الرصيد الحالي",
            "0.00",
            "kpi_green",
        )

        # =====================================================
        # RTL CARD ORDER
        #
        # من اليمين:
        # كود → اسم → وحدة → أول المدة → الحالي
        # =====================================================

        cards_layout.addWidget(self.code_card)

        cards_layout.addWidget(self.name_card)

        cards_layout.addWidget(self.unit_card)

        cards_layout.addWidget(self.opening_card)

        cards_layout.addWidget(self.balance_card)

        product_layout.addLayout(cards_layout)

        # =====================================================
        # TABLE HEADER
        # =====================================================

        table_header_layout = QHBoxLayout()

        table_header_layout.setDirection(
            QBoxLayout.LeftToRight if False else QBoxLayout.RightToLeft
        )

        # =====================================================
        # SECTION TITLE - RIGHT
        # =====================================================

        table_title = QLabel("حركات الصنف")

        table_title.setObjectName("section_title")

        table_title.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        # العنوان أول عنصر في RTL
        table_header_layout.addWidget(table_title)

        # =====================================================
        # STRETCH
        # =====================================================

        table_header_layout.addStretch()

        # =====================================================
        # LEFT BUTTON AREA
        # =====================================================

        button_area = QHBoxLayout()

        button_area.setSpacing(8)

        # =====================================================
        # PDF
        # =====================================================

        self.pdf_button = QPushButton("PDF")

        self.pdf_button.setObjectName("secondary_button")

        self.pdf_button.setMinimumHeight(42)

        self.pdf_button.setMinimumWidth(110)

        self.pdf_button.setCursor(Qt.PointingHandCursor)

        self.pdf_button.clicked.connect(self.pdf_placeholder)

        button_area.addWidget(self.pdf_button)

        # =====================================================
        # EDIT
        # =====================================================

        self.edit_button = QPushButton("تعديل")

        self.edit_button.setObjectName("secondary_button")

        self.edit_button.setMinimumHeight(42)

        self.edit_button.setMinimumWidth(100)

        self.edit_button.setCursor(Qt.PointingHandCursor)

        self.edit_button.clicked.connect(self.show_edit_view)

        self.edit_button.hide()

        button_area.addWidget(self.edit_button)

        # =====================================================
        # DELETE
        # =====================================================

        self.delete_button = QPushButton("حذف")

        self.delete_button.setObjectName("danger_button")

        self.delete_button.setMinimumHeight(42)

        self.delete_button.setMinimumWidth(100)

        self.delete_button.setCursor(Qt.PointingHandCursor)

        self.delete_button.clicked.connect(self.delete_transaction)

        self.delete_button.hide()

        button_area.addWidget(self.delete_button)

        table_header_layout.addLayout(button_area)

        product_layout.addLayout(table_header_layout)

        # =====================================================
        # TABLE
        # =====================================================

        self.table = QTableWidget()

        self.table.setObjectName("product_card_table")

        # =====================================================
        # IMPORTANT:
        # RTL TABLE
        # =====================================================

        self.table.setLayoutDirection(Qt.RightToLeft)

        self.table.setColumnCount(7)

        self.table.setHorizontalHeaderLabels(
            [
                "رقم الحركة",
                "التاريخ",
                "الوقت",
                "نوع الحركة",
                "الوارد",
                "المنصرف",
                "ملاحظات",
            ]
        )

        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        self.table.setSelectionBehavior(QTableWidget.SelectRows)

        self.table.setSelectionMode(QTableWidget.SingleSelection)

        self.table.verticalHeader().setVisible(False)

        self.table.setAlternatingRowColors(True)

        self.table.setMinimumHeight(300)

        # =====================================================
        # TABLE HEADER RTL
        # =====================================================

        header = self.table.horizontalHeader()

        header.setLayoutDirection(Qt.RightToLeft)

        header.setDefaultAlignment(Qt.AlignCenter)

        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)

        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)

        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)

        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)

        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)

        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)

        header.setSectionResizeMode(6, QHeaderView.Stretch)

        self.table.cellClicked.connect(self.select_transaction)

        product_layout.addWidget(self.table)

        # =====================================================
        # EDIT VIEW
        # =====================================================

        self.edit_view = QFrame()

        self.edit_view.setObjectName("transaction_card")

        self.edit_view.setLayoutDirection(Qt.RightToLeft)

        edit_layout = QVBoxLayout(self.edit_view)

        edit_layout.setContentsMargins(
            25,
            25,
            25,
            25,
        )

        edit_layout.setSpacing(10)

        # =====================================================
        # EDIT TITLE
        # =====================================================

        edit_title = QLabel("تعديل الحركة")

        edit_title.setObjectName("section_title")

        edit_title.setAlignment(Qt.AlignRight)

        edit_layout.addWidget(edit_title)

        # =====================================================
        # PRODUCT
        # =====================================================

        edit_product_label = QLabel("الصنف")

        edit_product_label.setObjectName("form_label")

        edit_product_label.setAlignment(Qt.AlignRight)

        edit_layout.addWidget(edit_product_label)

        self.edit_product_combo = QComboBox()

        self.edit_product_combo.setMinimumHeight(45)

        self.edit_product_combo.setLayoutDirection(Qt.RightToLeft)

        edit_layout.addWidget(self.edit_product_combo)

        # =====================================================
        # TYPE
        # =====================================================

        edit_type_label = QLabel("نوع الحركة")

        edit_type_label.setObjectName("form_label")

        edit_type_label.setAlignment(Qt.AlignRight)

        edit_layout.addWidget(edit_type_label)

        self.edit_type_combo = QComboBox()

        self.edit_type_combo.setMinimumHeight(45)

        self.edit_type_combo.setLayoutDirection(Qt.RightToLeft)

        self.edit_type_combo.addItems(
            [
                "إنتاج",
                "مشتريات",
                "صرف للتجزئة",
                "صرف للتسليمات",
                "مردودات مبيعات",
            ]
        )

        edit_layout.addWidget(self.edit_type_combo)

        # =====================================================
        # QUANTITY
        # =====================================================

        edit_quantity_label = QLabel("الكمية")

        edit_quantity_label.setObjectName("form_label")

        edit_quantity_label.setAlignment(Qt.AlignRight)

        edit_layout.addWidget(edit_quantity_label)

        self.edit_quantity = QLineEdit()

        self.edit_quantity.setMinimumHeight(45)

        self.edit_quantity.setPlaceholderText("أدخل الكمية")

        self.edit_quantity.setAlignment(Qt.AlignRight)

        edit_layout.addWidget(self.edit_quantity)

        # =====================================================
        # NOTES
        # =====================================================

        edit_notes_label = QLabel("ملاحظات")

        edit_notes_label.setObjectName("form_label")

        edit_notes_label.setAlignment(Qt.AlignRight)

        edit_layout.addWidget(edit_notes_label)

        self.edit_notes = QTextEdit()

        self.edit_notes.setMinimumHeight(100)

        self.edit_notes.setLayoutDirection(Qt.RightToLeft)

        edit_layout.addWidget(self.edit_notes)

        # =====================================================
        # BUTTONS
        # =====================================================

        buttons_layout = QHBoxLayout()

        buttons_layout.addStretch()

        self.cancel_edit_button = QPushButton("إلغاء")

        self.cancel_edit_button.setObjectName("secondary_button")

        self.cancel_edit_button.setMinimumHeight(45)

        self.cancel_edit_button.clicked.connect(self.cancel_edit)

        buttons_layout.addWidget(self.cancel_edit_button)

        self.save_edit_button = QPushButton("حفظ التعديل")

        self.save_edit_button.setObjectName("primary_button")

        self.save_edit_button.setMinimumHeight(45)

        self.save_edit_button.clicked.connect(self.update_transaction)

        buttons_layout.addWidget(self.save_edit_button)

        edit_layout.addLayout(buttons_layout)

        self.edit_view.hide()

        product_layout.addWidget(self.edit_view)

        # =====================================================
        # FINAL
        # =====================================================

        self.product_view.setLayout(product_layout)

        self.product_view.hide()

        main_layout.addWidget(self.product_view)

        main_layout.addStretch()

        self.scroll_area.setWidget(content)

        outer_layout.addWidget(self.scroll_area)

    # =========================================================
    # INFO CARD
    # =========================================================

    def create_info_card(
        self,
        title,
        value,
        style_class,
    ):

        card = QFrame()

        card.setObjectName("kpi_card")

        card.setProperty("class", style_class)

        card.setLayoutDirection(Qt.RightToLeft)

        layout = QVBoxLayout()

        layout.setContentsMargins(
            15,
            12,
            15,
            12,
        )

        layout.setSpacing(3)

        title_label = QLabel(title)

        title_label.setObjectName("kpi_title")

        title_label.setAlignment(Qt.AlignCenter)

        value_label = QLabel(value)

        value_label.setObjectName("kpi_value")

        value_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(title_label)

        layout.addWidget(value_label)

        card.setLayout(layout)

        return card, value_label

    # =========================================================
    # LOAD PRODUCTS
    # =========================================================

    def load_products(self):

        products = self.product_repo.get_all_products()

        self.products_data = []

        for _, row in products.iterrows():

            self.products_data.append(
                {
                    "id": str(row["product_ID"]),
                    "name": str(row["Product_Name"]),
                    "unit": str(row["Unit"]),
                }
            )

        self.edit_product_combo.clear()

        for product in self.products_data:

            self.edit_product_combo.addItem(product["name"])

    # =========================================================
    # SEARCH - START PAGE
    # =========================================================

    def filter_products(self):

        text = self.search_input.text().strip().lower()

        self.search_results.clear()

        if not text:

            self.search_results.hide()

            return

        matches = []

        for product in self.products_data:

            name = product["name"].lower()

            product_id = product["id"].lower()

            if name.startswith(text) or product_id.startswith(text):

                matches.append(product)

        if not matches:

            self.search_results.hide()

            return

        for product in matches:

            item = QListWidgetItem()

            item.setText(f'{product["name"]}   •   {product["id"]}')

            item.setData(Qt.UserRole, product["id"])

            self.search_results.addItem(item)

        self.search_results.show()

    # =========================================================
    # SELECT FIRST SEARCH RESULT
    # =========================================================

    def select_first_search_result(self):

        if self.search_results.count() == 0:
            return

        item = self.search_results.item(0)

        self.select_search_result(item)

    # =========================================================
    # SELECT SEARCH RESULT
    # =========================================================

    def select_search_result(
        self,
        item,
    ):

        product_id = item.data(Qt.UserRole)

        product = self.find_product(product_id)

        if product is None:
            return

        self.show_product(product)

    # =========================================================
    # FIND PRODUCT
    # =========================================================

    def find_product(
        self,
        product_id,
    ):

        for product in self.products_data:

            if product["id"] == product_id:

                return product

        return None

    # =========================================================
    # SHOW PRODUCT
    # =========================================================

    def show_product(
        self,
        product,
    ):

        self.selected_product = product

        self.search_view.hide()

        self.product_view.show()

        self.top_search.show()

        self.top_search.clear()

        self.top_search_results.hide()

        self.update_product_cards()

        self.load_transactions()

        self.scroll_area.verticalScrollBar().setValue(0)

    # =========================================================
    # UPDATE PRODUCT CARDS
    # =========================================================

    def update_product_cards(self):

        if not self.selected_product:
            return

        product_id = self.selected_product["id"]

        product_name = self.selected_product["name"]

        unit = self.selected_product["unit"]

        opening_balance = self.product_repo.get_opening_balance(product_id)

        (
            _,
            _,
            current_balance,
        ) = self.transaction_repo.get_product_balance(product_name)

        self.code_value.setText(product_id)

        self.name_value.setText(product_name)

        self.unit_value.setText(unit)

        self.opening_value.setText(f"{opening_balance:,.2f}")

        self.balance_value.setText(f"{current_balance:,.2f}")

    # =========================================================
    # LOAD TRANSACTIONS
    # =========================================================

    def load_transactions(self):

        if not self.selected_product:
            return

        product_name = self.selected_product["name"]

        transactions = self.transaction_repo.get_transactions_by_product(product_name)

        self.table.setRowCount(len(transactions))

        for row_index, row_data in enumerate(transactions):

            transaction_id = row_data[0]

            date = row_data[1]

            time = row_data[2]

            transaction_type = row_data[4]

            quantity = float(row_data[5])

            notes = row_data[6] or ""

            incoming = ""

            outgoing = ""

            if transaction_type in [
                "إنتاج",
                "مشتريات",
                "مردودات مبيعات",
            ]:

                incoming = f"{quantity:,.2f}"

            else:

                outgoing = f"{quantity:,.2f}"

            values = [
                transaction_id,
                date,
                time,
                transaction_type,
                incoming,
                outgoing,
                notes,
            ]

            for column_index, value in enumerate(values):

                item = QTableWidgetItem(str(value))

                item.setTextAlignment(Qt.AlignCenter)

                self.table.setItem(row_index, column_index, item)

        self.selected_transaction_id = None

        self.show_action_buttons(False)

    # =========================================================
    # SELECT TRANSACTION
    # =========================================================

    def select_transaction(
        self,
        row,
        column,
    ):

        item = self.table.item(row, 0)

        if item is None:
            return

        self.selected_transaction_id = item.text()

        self.show_action_buttons(True)

    # =========================================================
    # ACTION BUTTONS
    # =========================================================

    def show_action_buttons(
        self,
        selected,
    ):

        self.pdf_button.setVisible(not selected)

        self.edit_button.setVisible(selected)

        self.delete_button.setVisible(selected)

    # =========================================================
    # PDF
    # =========================================================

    def pdf_placeholder(self):

        QMessageBox.information(
            self,
            "PDF",
            "زر إنشاء PDF جاهز، وسنضيف وظيفة التصدير لاحقًا.",
        )

    # =========================================================
    # SHOW EDIT
    # =========================================================

    def show_edit_view(self):

        if not self.selected_transaction_id:
            return

        transaction = self.transaction_repo.get_transaction_by_id(
            self.selected_transaction_id
        )

        if transaction is None:
            return

        self.edit_product_combo.setCurrentText(transaction["product"])

        self.edit_type_combo.setCurrentText(transaction["type"])

        self.edit_quantity.setText(str(transaction["quantity"]))

        self.edit_notes.setPlainText(str(transaction["notes"] or ""))

        self.table.hide()

        self.edit_view.show()

        self.pdf_button.hide()

        self.edit_button.hide()

        self.delete_button.hide()

        self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        )

    # =========================================================
    # CANCEL EDIT
    # =========================================================

    def cancel_edit(self):

        self.edit_view.hide()

        self.table.show()

        self.selected_transaction_id = None

        self.show_action_buttons(False)

    # =========================================================
    # UPDATE TRANSACTION
    # =========================================================

    def update_transaction(self):

        if not self.selected_transaction_id:

            QMessageBox.warning(
                self,
                "خطأ",
                "اختر حركة أولاً.",
            )

            return

        quantity_text = self.edit_quantity.text().strip()

        if not quantity_text:

            QMessageBox.warning(
                self,
                "خطأ",
                "أدخل الكمية.",
            )

            return

        try:

            quantity = float(quantity_text)

        except ValueError:

            QMessageBox.warning(
                self,
                "خطأ",
                "الكمية يجب أن تكون رقمًا.",
            )

            return

        if quantity <= 0:

            QMessageBox.warning(
                self,
                "خطأ",
                "الكمية يجب أن تكون أكبر من صفر.",
            )

            return

        transaction = self.transaction_repo.get_transaction_by_id(
            self.selected_transaction_id
        )

        if transaction is None:
            return

        product = self.edit_product_combo.currentText()

        transaction_type = self.edit_type_combo.currentText()

        notes = self.edit_notes.toPlainText().strip()

        # =====================================================
        # STOCK CHECK
        # =====================================================

        if transaction_type in [
            "صرف للتجزئة",
            "صرف للتسليمات",
        ]:

            (
                _,
                _,
                current_balance,
            ) = self.transaction_repo.get_product_balance(product)

            old_quantity = float(transaction["quantity"])

            if transaction["type"] in [
                "صرف للتجزئة",
                "صرف للتسليمات",
            ]:

                available = current_balance + old_quantity

            else:

                available = current_balance

            if quantity > available:

                QMessageBox.warning(
                    self,
                    "الرصيد غير كافٍ",
                    "الكمية المطلوبة أكبر من الرصيد المتاح.",
                )

                return

        # =====================================================
        # UPDATE
        # =====================================================

        try:

            self.transaction_repo.update_transaction(
                self.selected_transaction_id,
                product,
                transaction_type,
                quantity,
                notes,
            )

        except Exception as e:

            QMessageBox.critical(
                self,
                "خطأ",
                f"حدث خطأ أثناء تعديل الحركة:\n{e}",
            )

            return

        QMessageBox.information(
            self,
            "تم التعديل",
            "تم تعديل الحركة بنجاح.",
        )

        self.edit_view.hide()

        self.table.show()

        self.selected_transaction_id = None

        self.show_action_buttons(False)

        self.update_product_cards()

        self.load_transactions()

    # =========================================================
    # DELETE
    # =========================================================

    def delete_transaction(self):

        if not self.selected_transaction_id:

            QMessageBox.warning(
                self,
                "خطأ",
                "اختر حركة أولاً.",
            )

            return

        transaction = self.transaction_repo.get_transaction_by_id(
            self.selected_transaction_id
        )

        if transaction is None:
            return

        reply = QMessageBox.question(
            self,
            "تأكيد حذف الحركة",
            (
                "هل أنت متأكد من حذف هذه الحركة؟\n\n"
                f"رقم الحركة: "
                f"{transaction['id']}\n"
                f"الصنف: "
                f"{transaction['product']}\n"
                f"الكمية: "
                f"{transaction['quantity']}"
            ),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply != QMessageBox.Yes:
            return

        try:

            self.transaction_repo.delete_transaction(self.selected_transaction_id)

        except Exception as e:

            QMessageBox.critical(
                self,
                "خطأ",
                f"حدث خطأ أثناء حذف الحركة:\n{e}",
            )

            return

        QMessageBox.information(
            self,
            "تم الحذف",
            "تم حذف الحركة بنجاح.",
        )

        self.selected_transaction_id = None

        self.show_action_buttons(False)

        self.update_product_cards()

        self.load_transactions()

    # =========================================================
    # TOP SEARCH
    # =========================================================

    def filter_top_products(
        self,
        text,
    ):

        text = text.strip().lower()

        self.top_search_results.clear()

        if not text:

            self.top_search_results.hide()

            return

        matches = []

        for product in self.products_data:

            name = product["name"].lower()

            product_id = product["id"].lower()

            if name.startswith(text) or product_id.startswith(text):

                matches.append(product)

        if not matches:

            self.top_search_results.hide()

            return

        for product in matches:

            item = QListWidgetItem()

            item.setText(f'{product["name"]}   •   {product["id"]}')

            item.setData(Qt.UserRole, product["id"])

            self.top_search_results.addItem(item)

        self.top_search_results.show()

    # =========================================================
    # TOP SEARCH SELECT
    # =========================================================

    def select_first_top_result(self):

        if self.top_search_results.count() == 0:
            return

        item = self.top_search_results.item(0)

        self.select_top_search_result(item)

    def select_top_search_result(
        self,
        item,
    ):

        product_id = item.data(Qt.UserRole)

        product = self.find_product(product_id)

        if product is None:
            return

        self.show_product(product)

    # =========================================================
    # RELOAD PRODUCTS
    # =========================================================

    def reload_products(self):

        old_product_id = None

        if self.selected_product:

            old_product_id = self.selected_product["id"]

        self.load_products()

        if old_product_id:

            product = self.find_product(old_product_id)

            if product:

                self.selected_product = product

                self.update_product_cards()

                self.load_transactions()

    # =========================================================
    # REFRESH
    # =========================================================

    def refresh_page(self):

        if self.selected_product:

            product = self.find_product(self.selected_product["id"])

            if product:

                self.selected_product = product

                self.update_product_cards()

                self.load_transactions()

        else:

            self.load_products()

    # =========================================================
    # SEARCH VIEW
    # =========================================================

    def show_search_view(self):

        self.selected_product = None

        self.selected_transaction_id = None

        self.product_view.hide()

        self.search_view.show()

        self.top_search.hide()

        self.top_search_results.hide()

        self.edit_view.hide()

        self.table.show()

        self.show_action_buttons(False)

        self.search_input.clear()

        self.search_results.clear()

        self.search_results.hide()

        self.search_input.setFocus()
