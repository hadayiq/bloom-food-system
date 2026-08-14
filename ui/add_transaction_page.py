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
)
from PySide6.QtCore import Qt

from database.products import ProductRepository
from database.transactions import TransactionRepository
from utils.refresh_manager import refresh_manager


class AddTransactionPage(QWidget):

    def __init__(self):
        super().__init__()

        self.product_repo = ProductRepository()
        self.transaction_repo = TransactionRepository()

        self.build_ui()
        self.load_products()

        refresh_manager.products_changed.connect(self.reload_products)

        refresh_manager.data_changed.connect(self.refresh_page)

        self.show_start_view()

    # =========================================================
    # BUILD UI
    # =========================================================

    def build_ui(self):

        main_layout = QVBoxLayout(self)

        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # =====================================================
        # SCROLL AREA
        # =====================================================

        scroll = QScrollArea()

        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # =====================================================
        # CONTENT
        # =====================================================

        content = QWidget()

        content_layout = QVBoxLayout(content)

        content_layout.setContentsMargins(
            35,
            30,
            35,
            30,
        )

        content_layout.setSpacing(18)

        # =====================================================
        # PAGE HEADER
        # =====================================================

        header_layout = QVBoxLayout()
        header_layout.setSpacing(3)

        self.title = QLabel("الحركات المخزنية")
        self.title.setObjectName("page_title")

        self.subtitle = QLabel("إضافة ومتابعة الحركات الخاصة بالأصناف")
        self.subtitle.setObjectName("page_subtitle")

        header_layout.addWidget(self.title)
        header_layout.addWidget(self.subtitle)

        content_layout.addLayout(header_layout)

        # =====================================================
        # START VIEW
        # =====================================================

        self.start_view = QWidget()

        start_layout = QVBoxLayout(self.start_view)

        start_layout.setContentsMargins(
            0,
            20,
            0,
            0,
        )

        start_layout.setSpacing(20)

        # =====================================================
        # NEW TRANSACTION CARD
        # =====================================================

        new_card = QFrame()
        new_card.setObjectName("transaction_card")

        new_layout = QVBoxLayout(new_card)

        new_layout.setContentsMargins(
            25,
            25,
            25,
            25,
        )

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

        # =====================================================
        # RECENT TRANSACTIONS TITLE
        # =====================================================

        recent_title_layout = QHBoxLayout()

        recent_title = QLabel("آخر الحركات")

        recent_title.setObjectName("section_title")

        recent_title_layout.addStretch()

        recent_title_layout.addWidget(recent_title)

        start_layout.addLayout(recent_title_layout)

        # =====================================================
        # RECENT TRANSACTIONS TABLE
        # =====================================================

        self.recent_table = QTableWidget()

        self.recent_table.setColumnCount(5)

        self.recent_table.setHorizontalHeaderLabels(
            [
                "التاريخ",
                "الصنف",
                "الحركة",
                "الكمية",
                "ملاحظات",
            ]
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

        header.setSectionResizeMode(
            4,
            QHeaderView.Stretch,
        )

        start_layout.addWidget(self.recent_table)

        content_layout.addWidget(self.start_view)

        # =====================================================
        # FORM VIEW
        # =====================================================

        self.form_view = QWidget()

        form_main_layout = QVBoxLayout(self.form_view)

        form_main_layout.setContentsMargins(
            0,
            20,
            0,
            0,
        )

        form_main_layout.setSpacing(18)

        # =====================================================
        # BACK BUTTON
        # =====================================================

        back_layout = QHBoxLayout()

        self.back_button = QPushButton("← رجوع")

        self.back_button.setObjectName("secondary_button")

        self.back_button.setCursor(Qt.PointingHandCursor)

        self.back_button.clicked.connect(self.show_start_view)

        back_layout.addWidget(self.back_button)

        back_layout.addStretch()

        form_main_layout.addLayout(back_layout)

        # =====================================================
        # PRODUCT CARD
        # =====================================================

        product_card = QFrame()

        product_card.setObjectName("transaction_card")

        product_layout = QVBoxLayout(product_card)

        product_layout.setContentsMargins(
            25,
            25,
            25,
            25,
        )

        product_layout.setSpacing(10)

        product_label = QLabel("الصنف")

        product_label.setObjectName("form_label")

        self.product_combo = QComboBox()

        self.product_combo.setMinimumHeight(45)

        self.product_combo.currentIndexChanged.connect(self.product_selected)

        product_layout.addWidget(product_label)

        product_layout.addWidget(self.product_combo)

        form_main_layout.addWidget(product_card)

        # =====================================================
        # SUMMARY CARDS
        # =====================================================

        self.summary_container = QWidget()

        summary_layout = QHBoxLayout(self.summary_container)

        summary_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        summary_layout.setSpacing(15)

        # الوارد
        (
            self.incoming_card,
            self.incoming_value,
        ) = self.create_summary_card(
            "الوارد",
            "0.00",
            "kpi_green",
            QStyle.SP_ArrowDown,
        )

        # المنصرف
        (
            self.outgoing_card,
            self.outgoing_value,
        ) = self.create_summary_card(
            "المنصرف",
            "0.00",
            "kpi_blue",
            QStyle.SP_ArrowUp,
        )

        # المتبقي
        (
            self.balance_card,
            self.balance_value,
        ) = self.create_summary_card(
            "المتبقي",
            "0.00",
            "kpi_orange",
            QStyle.SP_DriveHDIcon,
        )

        summary_layout.addWidget(self.incoming_card)

        summary_layout.addWidget(self.outgoing_card)

        summary_layout.addWidget(self.balance_card)

        form_main_layout.addWidget(self.summary_container)

        # =====================================================
        # INPUT CARD
        # =====================================================

        input_card = QFrame()

        input_card.setObjectName("transaction_card")

        input_layout = QVBoxLayout(input_card)

        input_layout.setContentsMargins(
            25,
            25,
            25,
            25,
        )

        input_layout.setSpacing(10)

        # =====================================================
        # TRANSACTION TYPE
        # =====================================================

        type_label = QLabel("نوع الحركة")

        type_label.setObjectName("form_label")

        self.type_combo = QComboBox()

        self.type_combo.setMinimumHeight(45)

        self.type_combo.addItem("اختر نوع الحركة")

        self.type_combo.addItems(
            [
                "إنتاج",
                "مشتريات",
                "صرف للتجزئة",
                "صرف للتسليمات",
                "مردودات مبيعات",
            ]
        )

        input_layout.addWidget(type_label)

        input_layout.addWidget(self.type_combo)

        # =====================================================
        # QUANTITY
        # =====================================================

        quantity_label = QLabel("الكمية")

        quantity_label.setObjectName("form_label")

        self.quantity_input = QLineEdit()

        self.quantity_input.setMinimumHeight(45)

        self.quantity_input.setPlaceholderText("أدخل الكمية")

        input_layout.addWidget(quantity_label)

        input_layout.addWidget(self.quantity_input)

        # =====================================================
        # NOTES
        # =====================================================

        notes_label = QLabel("ملاحظات")

        notes_label.setObjectName("form_label")

        self.notes_input = QTextEdit()

        self.notes_input.setMinimumHeight(100)

        self.notes_input.setPlaceholderText("أضف ملاحظات إن وجدت...")

        input_layout.addWidget(notes_label)

        input_layout.addWidget(self.notes_input)

        # =====================================================
        # SAVE BUTTON
        # =====================================================

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

        # =====================================================
        # SCROLL
        # =====================================================

        scroll.setWidget(content)

        main_layout.addWidget(scroll)

    # =========================================================
    # SUMMARY CARD
    # =========================================================

    def create_summary_card(
        self,
        title,
        value,
        style_class,
        icon_type,
    ):

        card = QFrame()

        card.setObjectName("kpi_card")

        card.setProperty(
            "class",
            style_class,
        )

        layout = QVBoxLayout()

        layout.setContentsMargins(
            18,
            12,
            18,
            12,
        )

        layout.setSpacing(4)

        # =====================================================
        # ICON
        # =====================================================

        icon_label = QLabel()

        icon_label.setObjectName("kpi_icon")

        icon = self.style().standardIcon(icon_type)

        icon_label.setPixmap(icon.pixmap(28, 28))

        icon_label.setAlignment(Qt.AlignCenter)

        # =====================================================
        # TITLE
        # =====================================================

        title_label = QLabel(title)

        title_label.setObjectName("kpi_title")

        title_label.setAlignment(Qt.AlignCenter)

        # =====================================================
        # VALUE
        # =====================================================

        value_label = QLabel(value)

        value_label.setObjectName("kpi_value")

        value_label.setAlignment(Qt.AlignCenter)

        # =====================================================
        # CARD LAYOUT
        # =====================================================

        layout.addWidget(icon_label)

        layout.addWidget(title_label)

        layout.addWidget(value_label)

        card.setLayout(layout)

        return card, value_label

    # =========================================================
    # LOAD PRODUCTS
    # =========================================================

    def load_products(self):

        self.product_combo.clear()

        self.product_combo.addItem("اختر الصنف")

        products = self.product_repo.get_product_names()

        if products:
            self.product_combo.addItems(products)

        self.product_combo.setCurrentIndex(0)

    # =========================================================
    # PRODUCT SELECTED
    # =========================================================

    def product_selected(self):

        if self.product_combo.currentIndex() == 0:

            self.summary_container.hide()

            return

        product = self.product_combo.currentText()

        try:

            (
                total_in,
                total_out,
                balance,
            ) = self.transaction_repo.get_product_balance(product)

        except Exception as e:

            print(
                "Error getting product balance:",
                e,
            )

            self.summary_container.hide()

            return

        self.incoming_value.setText(f"{total_in:,.2f}")

        self.outgoing_value.setText(f"{total_out:,.2f}")

        self.balance_value.setText(f"{balance:,.2f}")

        self.summary_container.show()

    # =========================================================
    # SHOW START VIEW
    # =========================================================

    def show_start_view(self):

        self.start_view.show()

        self.form_view.hide()

        self.load_recent_transactions()

    # =========================================================
    # SHOW FORM VIEW
    # =========================================================

    def show_form_view(self):

        self.start_view.hide()

        self.form_view.show()

        self.product_combo.setCurrentIndex(0)

        self.type_combo.setCurrentIndex(0)

        self.quantity_input.clear()

        self.notes_input.clear()

        self.summary_container.hide()

        self.product_combo.setFocus()

    # =========================================================
    # RELOAD PRODUCTS
    # =========================================================

    def reload_products(self):

        current = ""

        if self.product_combo.count():

            current = self.product_combo.currentText()

        self.load_products()

        index = self.product_combo.findText(current)

        if index >= 0:

            self.product_combo.setCurrentIndex(index)

    # =========================================================
    # LOAD RECENT TRANSACTIONS
    # =========================================================

    def load_recent_transactions(self):

        transactions = []

        try:

            import openpyxl

            workbook = openpyxl.load_workbook(
                self.transaction_repo.file,
                read_only=True,
                data_only=True,
            )

            sheet = workbook["Transactions"]

            for row in sheet.iter_rows(
                min_row=2,
                values_only=True,
            ):

                if not row:
                    continue

                transactions.append(row)

            workbook.close()

        except Exception as e:

            print(
                "Error loading transactions:",
                e,
            )

            self.recent_table.setRowCount(0)

            return

        # =====================================================
        # LAST 10
        # =====================================================

        transactions = transactions[-10:]

        transactions.reverse()

        self.recent_table.setRowCount(len(transactions))

        # =====================================================
        # FILL TABLE
        # =====================================================

        for row_index, row in enumerate(transactions):

            date = row[1] if len(row) > 1 else ""

            time = row[2] if len(row) > 2 else ""

            product = row[3] if len(row) > 3 else ""

            transaction_type = row[4] if len(row) > 4 else ""

            quantity = row[5] if len(row) > 5 else 0

            notes = row[6] if len(row) > 6 else ""

            # =================================================
            # DATE / TIME
            # =================================================

            if date is None:
                date = ""

            if time is None:
                time = ""

            date_time = (f"{date} {time}").strip()

            # =================================================
            # QUANTITY
            # =================================================

            try:

                quantity_text = f"{float(quantity):,.2f}"

            except (
                ValueError,
                TypeError,
            ):

                quantity_text = str(quantity)

            values = [
                date_time,
                product,
                transaction_type,
                quantity_text,
                notes or "",
            ]

            # =================================================
            # TABLE ITEMS
            # =================================================

            for column_index, value in enumerate(values):

                item = QTableWidgetItem(str(value))

                if column_index in [
                    0,
                    2,
                    3,
                ]:

                    item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)

                else:

                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

                # =============================================
                # TRANSACTION TYPE COLOR
                # =============================================

                if column_index == 2:

                    if transaction_type in [
                        "إنتاج",
                        "مشتريات",
                        "مردودات مبيعات",
                    ]:

                        item.setForeground(Qt.darkGreen)

                    elif transaction_type in [
                        "صرف للتجزئة",
                        "صرف للتسليمات",
                    ]:

                        item.setForeground(Qt.blue)

                self.recent_table.setItem(row_index, column_index, item)

    # =========================================================
    # SAVE TRANSACTION
    # =========================================================

    def save_transaction(self):

        # =====================================================
        # PRODUCT
        # =====================================================

        if self.product_combo.currentIndex() == 0:

            QMessageBox.warning(
                self,
                "خطأ",
                "اختر الصنف.",
            )

            return

        # =====================================================
        # TYPE
        # =====================================================

        if self.type_combo.currentIndex() == 0:

            QMessageBox.warning(
                self,
                "خطأ",
                "اختر نوع الحركة.",
            )

            return

        # =====================================================
        # QUANTITY
        # =====================================================

        quantity_text = self.quantity_input.text().strip()

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

        # =====================================================
        # DATA
        # =====================================================

        product = self.product_combo.currentText()

        transaction_type = self.type_combo.currentText()

        notes = self.notes_input.toPlainText().strip()

        # =====================================================
        # CHECK STOCK
        # =====================================================

        if transaction_type in [
            "صرف للتجزئة",
            "صرف للتسليمات",
        ]:

            if not self.transaction_repo.check_stock(
                product,
                quantity,
            ):

                QMessageBox.warning(
                    self,
                    "الرصيد غير كافٍ",
                    "الكمية المطلوبة أكبر من الرصيد الحالي.",
                )

                return

        # =====================================================
        # SAVE
        # =====================================================

        try:

            self.transaction_repo.save_transaction(
                product,
                transaction_type,
                quantity,
                notes,
            )

        except Exception as e:

            QMessageBox.critical(
                self,
                "خطأ",
                f"حدث خطأ أثناء حفظ الحركة:\n{e}",
            )

            return

        # =====================================================
        # REFRESH
        # =====================================================

        refresh_manager.data_changed.emit()

        QMessageBox.information(
            self,
            "تم الحفظ",
            "تم حفظ الحركة بنجاح.",
        )

        self.show_start_view()

    # =========================================================
    # REFRESH PAGE
    # =========================================================

    def refresh_page(self):

        if self.product_combo.currentIndex() != 0:

            self.product_selected()

        self.load_recent_transactions()
