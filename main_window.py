import os

from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QFrame,
    QStackedWidget,
    QSizePolicy,
)

from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt, QSize

from ui.inventory_summary_page import InventorySummaryPage
from ui.add_transaction_page import AddTransactionPage
from ui.product_card_page import ProductCardPage
from ui.reports_page import ReportsPage
from ui.products_page import ProductsPage

from utils.refresh_manager import refresh_manager


class MainWindow(QWidget):

    def __init__(self):

        super().__init__()

        # ==========================================
        # WINDOW
        # ==========================================

        self.setWindowTitle("Bloom Food - Inventory System")
        self.resize(1250, 750)

        # ==========================================
        # MAIN LAYOUT
        # ==========================================

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ==========================================
        # SIDEBAR
        # ==========================================

        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(250)

        sidebar_layout = QVBoxLayout()
        sidebar_layout.setContentsMargins(18, 24, 18, 18)
        sidebar_layout.setSpacing(6)

        # ==========================================
        # COMPANY HEADER
        # ==========================================

        company_name = QLabel("BLOOM FOOD")
        company_name.setObjectName("company_name")

        company_subtitle = QLabel("Inventory Management")
        company_subtitle.setObjectName("company_subtitle")

        sidebar_layout.addWidget(company_name)
        sidebar_layout.addWidget(company_subtitle)
        sidebar_layout.addSpacing(12)

        sidebar_line = QFrame()
        sidebar_line.setObjectName("sidebar_line")
        sidebar_line.setFrameShape(QFrame.HLine)
        sidebar_line.setFrameShadow(QFrame.Plain)

        sidebar_layout.addWidget(sidebar_line)

        sidebar_layout.addSpacing(18)

        # ==========================================
        # NAVIGATION BUTTONS
        # ==========================================

        self.btn_dashboard = QPushButton("Dashboard")
        self.btn_add = QPushButton("إضافة حركة")
        self.btn_search = QPushButton("كارت الصنف")
        self.btn_products = QPushButton("إدارة الأصناف")
        self.btn_reports = QPushButton("التقارير")

        # ==========================================
        # SIDEBAR ICONS
        # ==========================================

        # مكان الأيقونات:
        #
        # Inventory Project/
        # │
        # ├── main_window.py
        # │
        # └── icons/
        #     ├── dashboard.svg
        #     ├── transaction.svg
        #     ├── product_card.svg
        #     ├── products.svg
        #     └── reports.svg

        base_dir = os.path.dirname(os.path.abspath(__file__))
        icons_dir = os.path.join(base_dir, "icons")

        icon_files = {
            self.btn_dashboard: "dashboard.svg",
            self.btn_add: "transaction.svg",
            self.btn_search: "product_card.svg",
            self.btn_products: "products.svg",
            self.btn_reports: "reports.svg",
        }

        icon_size = QSize(22, 22)

        for button, icon_name in icon_files.items():

            icon_path = os.path.join(icons_dir, icon_name)

            icon = QIcon(icon_path)

            # Debug
            print(
                f"[ICON] {icon_name} | "
                f"EXISTS={os.path.exists(icon_path)} | "
                f"NULL={icon.isNull()}"
            )

            # وضع الأيقونة فعليًا على الزر
            button.setIcon(icon)
            button.setIconSize(icon_size)

        # ==========================================
        # SIDEBAR BUTTON SETTINGS
        # ==========================================

        buttons = [
            self.btn_dashboard,
            self.btn_add,
            self.btn_search,
            self.btn_products,
            self.btn_reports,
        ]

        for button in buttons:

            button.setObjectName("sidebar_button")

            button.setCursor(Qt.PointingHandCursor)

            button.setSizePolicy(
                QSizePolicy.Expanding,
                QSizePolicy.Fixed,
            )

            # RTL
            # النص العربي والأيقونة ناحية اليمين
            button.setLayoutDirection(Qt.RightToLeft)

            sidebar_layout.addWidget(button)

        sidebar_layout.addStretch()

        # ==========================================
        # FOOTER
        # ==========================================

        footer = QLabel("Bloom Food\n" "Inventory System")

        footer.setObjectName("sidebar_footer")
        footer.setAlignment(Qt.AlignCenter)

        sidebar_layout.addWidget(footer)

        sidebar.setLayout(sidebar_layout)

        # ==========================================
        # STACKED PAGES
        # ==========================================

        self.stack = QStackedWidget()
        self.stack.setObjectName("content_area")

        self.dashboard_page = InventorySummaryPage()
        self.add_page = AddTransactionPage()
        self.product_card_page = ProductCardPage()
        self.products_page = ProductsPage()
        self.reports_page = ReportsPage()

        self.stack.addWidget(self.dashboard_page)
        self.stack.addWidget(self.add_page)
        self.stack.addWidget(self.product_card_page)
        self.stack.addWidget(self.products_page)
        self.stack.addWidget(self.reports_page)

        # ==========================================
        # REFRESH SYSTEM
        # ==========================================

        refresh_manager.data_changed.connect(self.dashboard_page.load_data)

        refresh_manager.products_changed.connect(self.dashboard_page.load_data)

        # ==========================================
        # NAVIGATION
        # ==========================================

        self.btn_dashboard.clicked.connect(
            lambda: self.change_page(0, self.btn_dashboard)
        )

        self.btn_add.clicked.connect(lambda: self.change_page(1, self.btn_add))

        self.btn_search.clicked.connect(lambda: self.change_page(2, self.btn_search))

        self.btn_products.clicked.connect(
            lambda: self.change_page(3, self.btn_products)
        )

        self.btn_reports.clicked.connect(lambda: self.change_page(4, self.btn_reports))

        # ==========================================
        # MAIN SCREEN LAYOUT
        # ==========================================

        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.stack)

        self.setLayout(main_layout)

        # ==========================================
        # DEFAULT PAGE
        # ==========================================

        self.change_page(0, self.btn_dashboard)

    # ==========================================
    # CHANGE PAGE
    # ==========================================

    def change_page(self, index, active_button):

        self.stack.setCurrentIndex(index)

        buttons = [
            self.btn_dashboard,
            self.btn_add,
            self.btn_search,
            self.btn_products,
            self.btn_reports,
        ]

        for button in buttons:

            button.setProperty("active", button == active_button)

            button.style().unpolish(button)
            button.style().polish(button)
            button.update()
