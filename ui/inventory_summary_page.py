from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QFrame,
    QHeaderView,
    QStyle,
)
from PySide6.QtCore import Qt

from database.transactions import TransactionRepository
from utils.refresh_manager import refresh_manager


class InventorySummaryPage(QWidget):

    def __init__(self):

        super().__init__()

        # ==========================================
        # MAIN LAYOUT
        # ==========================================

        main_layout = QVBoxLayout()

        main_layout.setContentsMargins(
            35,
            30,
            35,
            30,
        )

        main_layout.setSpacing(22)

        # ==========================================
        # PAGE HEADER
        # ==========================================

        header_layout = QVBoxLayout()
        header_layout.setSpacing(3)

        title = QLabel("Inventory Dashboard")
        title.setObjectName("dashboard_title")

        subtitle = QLabel("نظرة عامة على المخزون والحركات")
        subtitle.setObjectName("dashboard_subtitle")

        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)

        main_layout.addLayout(header_layout)

        # ==========================================
        # KPI CARDS
        # ==========================================

        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(18)

        # ------------------------------------------
        # Current Stock
        # ------------------------------------------

        (
            self.current_stock_card,
            self.current_stock_value,
        ) = self.create_card(
            "الرصيد الحالي",
            "0.00",
            "kpi_green",
            QStyle.SP_DriveHDIcon,
        )

        # ------------------------------------------
        # Outgoing
        # ------------------------------------------

        (
            self.outgoing_card,
            self.outgoing_value,
        ) = self.create_card(
            "إجمالي المنصرف",
            "0.00",
            "kpi_blue",
            QStyle.SP_ArrowRight,
        )

        # ------------------------------------------
        # Incoming
        # ------------------------------------------

        (
            self.incoming_card,
            self.incoming_value,
        ) = self.create_card(
            "إجمالي الوارد",
            "0.00",
            "kpi_orange",
            QStyle.SP_ArrowLeft,
        )

        # ------------------------------------------
        # Products
        # ------------------------------------------

        (
            self.products_card,
            self.products_value,
        ) = self.create_card(
            "إجمالي الأصناف",
            "0",
            "kpi_purple",
            QStyle.SP_DirIcon,
        )

        cards_layout.addWidget(self.current_stock_card)
        cards_layout.addWidget(self.outgoing_card)
        cards_layout.addWidget(self.incoming_card)
        cards_layout.addWidget(self.products_card)

        main_layout.addLayout(cards_layout)

        # ==========================================
        # SECTION HEADER
        # ==========================================

        section_layout = QHBoxLayout()

        table_title = QLabel("ملخص المخزون")
        table_title.setObjectName("dashboard_section_title")

        section_layout.addStretch()

        section_layout.addWidget(
            table_title,
            alignment=Qt.AlignRight,
        )

        main_layout.addLayout(section_layout)

        # ==========================================
        # INVENTORY TABLE
        # ==========================================

        self.table = QTableWidget()

        self.table.setColumnCount(5)

        self.table.setHorizontalHeaderLabels(
            [
                "الصنف",
                "أول المدة",
                "الوارد",
                "المنصرف",
                "الرصيد الحالي",
            ]
        )

        # ------------------------------------------
        # Table Behavior
        # ------------------------------------------

        self.table.setAlternatingRowColors(True)

        self.table.setShowGrid(False)

        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        self.table.setSelectionBehavior(QTableWidget.SelectRows)

        self.table.setSelectionMode(QTableWidget.SingleSelection)

        # ------------------------------------------
        # Headers
        # ------------------------------------------

        self.table.verticalHeader().setVisible(False)

        self.table.verticalHeader().setDefaultSectionSize(44)

        header = self.table.horizontalHeader()

        header.setHighlightSections(False)

        header.setStretchLastSection(True)

        # ------------------------------------------
        # Column Sizes
        # ------------------------------------------

        header.setSectionResizeMode(
            0,
            QHeaderView.Stretch,
        )

        header.setSectionResizeMode(
            1,
            QHeaderView.ResizeToContents,
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
            QHeaderView.ResizeToContents,
        )

        main_layout.addWidget(self.table)

        # ==========================================
        # FINAL LAYOUT
        # ==========================================

        self.setLayout(main_layout)

        # ==========================================
        # INITIAL LOAD
        # ==========================================

        self.load_data()

        # ==========================================
        # REFRESH SYSTEM
        # ==========================================

        refresh_manager.data_changed.connect(self.load_data)

        refresh_manager.products_changed.connect(self.load_data)

    # ==================================================
    # CREATE KPI CARD
    # ==================================================

    def create_card(
        self,
        title,
        value,
        object_name,
        icon_type,
    ):

        card = QFrame()

        card.setObjectName("kpi_card")

        card.setProperty(
            "class",
            object_name,
        )

        # ------------------------------------------
        # Card Layout
        # ------------------------------------------

        layout = QVBoxLayout()

        layout.setContentsMargins(
            18,
            12,
            18,
            12,
        )

        layout.setSpacing(4)

        # ------------------------------------------
        # ICON
        # ------------------------------------------

        icon_label = QLabel()

        icon_label.setObjectName("kpi_icon")

        icon = self.style().standardIcon(icon_type)

        icon_pixmap = icon.pixmap(
            28,
            28,
        )

        icon_label.setPixmap(icon_pixmap)

        icon_label.setAlignment(Qt.AlignCenter)

        # ------------------------------------------
        # TITLE
        # ------------------------------------------

        title_label = QLabel(title)

        title_label.setObjectName("kpi_title")

        title_label.setAlignment(Qt.AlignCenter)

        # ------------------------------------------
        # VALUE
        # ------------------------------------------

        value_label = QLabel(value)

        value_label.setObjectName("kpi_value")

        value_label.setAlignment(Qt.AlignCenter)

        # ------------------------------------------
        # ADD TO CARD
        # ------------------------------------------

        layout.addWidget(icon_label)

        layout.addWidget(title_label)

        layout.addWidget(value_label)

        card.setLayout(layout)

        return card, value_label

    # ==================================================
    # LOAD DATA
    # ==================================================

    def load_data(self):

        print("SUMMARY REFRESHED")

        repo = TransactionRepository()

        data = repo.get_inventory_summary()

        # ------------------------------------------
        # Table
        # ------------------------------------------

        self.table.setRowCount(len(data))

        # ------------------------------------------
        # Totals
        # ------------------------------------------

        total_opening = 0
        total_incoming = 0
        total_outgoing = 0
        total_current = 0

        # ==========================================
        # FILL TABLE
        # ==========================================

        for row_index, row_data in enumerate(data):

            for column_index, value in enumerate(row_data):

                item = QTableWidgetItem(str(value))

                # ----------------------------------
                # Alignment
                # ----------------------------------

                if column_index == 0:

                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

                else:

                    item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)

                self.table.setItem(
                    row_index,
                    column_index,
                    item,
                )

            # ======================================
            # CALCULATE TOTALS
            # ======================================

            try:

                total_opening += float(row_data[1])

            except (
                ValueError,
                TypeError,
            ):

                pass

            try:

                total_incoming += float(row_data[2])

            except (
                ValueError,
                TypeError,
            ):

                pass

            try:

                total_outgoing += float(row_data[3])

            except (
                ValueError,
                TypeError,
            ):

                pass

            try:

                total_current += float(row_data[4])

            except (
                ValueError,
                TypeError,
            ):

                pass

        # ==========================================
        # UPDATE KPI CARDS
        # ==========================================

        self.current_stock_value.setText(f"{total_current:,.2f}")

        self.incoming_value.setText(f"{total_incoming:,.2f}")

        self.outgoing_value.setText(f"{total_outgoing:,.2f}")

        self.products_value.setText(f"{len(data):,}")
