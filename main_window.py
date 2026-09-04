import os

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QFrame,
    QStackedWidget, QSizePolicy, QMessageBox, QBoxLayout,
)
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import Qt, QSize

from ui.inventory_summary_page import InventorySummaryPage
from ui.add_transaction_page import AddTransactionPage
from ui.product_card_page import ProductCardPage
from ui.reports_page import ReportsPage
from ui.products_page import ProductsPage
from ui.issue_voucher_dialog import IssueVoucherDialog
from ui.subwarehouses_page import SubwarehousesPage
from utils.refresh_manager import refresh_manager


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bloom Food - Inventory System")
        self.resize(1440, 960)
        self.setMinimumSize(1200, 800)
        self.setLayoutDirection(Qt.LeftToRight)

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.setDirection(QBoxLayout.LeftToRight)

        base_dir = os.path.dirname(os.path.abspath(__file__))
        icons_dir = os.path.join(base_dir, "icons")

        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(218)
        sidebar.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        sidebar.setLayoutDirection(Qt.LeftToRight)
        self.sidebar = sidebar

        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(16, 24, 16, 32)
        sidebar_layout.setSpacing(10)
        sidebar_layout.setDirection(QBoxLayout.TopToBottom)

        brand_row = QWidget()
        brand_row.setObjectName("sidebar_brand")
        brand_layout = QHBoxLayout(brand_row)
        brand_layout.setContentsMargins(0, 0, 0, 0)
        brand_layout.setSpacing(8)

        logo = QLabel()
        logo.setObjectName("sidebar_logo")
        logo.setAlignment(Qt.AlignCenter)
        logo.setFixedSize(38, 48)
        logo_path = os.path.join(icons_dir, "bloomfood_logo.png")
        if not os.path.exists(logo_path):
            logo_path = os.path.join(icons_dir, "bloom_logo.png")
        pixmap = QPixmap(logo_path)
        if not pixmap.isNull():
            logo.setPixmap(pixmap.scaled(38, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        company_name = QLabel("BLOOM FOOD")
        company_name.setObjectName("sidebar_company_name")
        company_name.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        company_name.setWordWrap(False)
        brand_layout.addWidget(logo, 0, Qt.AlignVCenter)
        brand_layout.addWidget(company_name, 1, Qt.AlignVCenter)
        sidebar_layout.addWidget(brand_row)
        sidebar_layout.addSpacing(24)

        self.btn_dashboard = QPushButton("Dashboard")
        self.btn_inventory = QPushButton("Inventory")
        self.btn_reports = QPushButton("Reports")
        self.btn_product = QPushButton("Product")
        self.btn_subinventory = QPushButton("Subinventory")
        self.btn_orders = QPushButton("Orders")

        self.icon_files = {
            self.btn_dashboard: ("dashboard.svg", "dashboard_active.svg"),
            self.btn_inventory: ("products.svg", "products_active.svg"),
            self.btn_reports: ("reports.svg", "reports_active.svg"),
            self.btn_product: ("product_card.svg", "product_card_active.svg"),
            self.btn_subinventory: ("subwarehouse.svg", "subwarehouse_active.svg"),
            self.btn_orders: ("transaction.svg", "transaction_active.svg"),
        }

        for button, (icon_name, _) in self.icon_files.items():
            button.setObjectName("sidebar_button")
            button.setIcon(QIcon(os.path.join(icons_dir, icon_name)))
            button.setIconSize(QSize(18, 18))
            button.setCursor(Qt.PointingHandCursor)
            button.setFixedHeight(44)
            button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            button.setLayoutDirection(Qt.LeftToRight)
            sidebar_layout.addWidget(button, 0, Qt.AlignTop)

        sidebar_layout.addStretch(1)

        self.btn_exit = QPushButton("Logout")
        self.btn_exit.setObjectName("sidebar_logout_button")
        self.btn_exit.setIcon(QIcon(os.path.join(icons_dir, "sidebar_logout.svg")))
        self.btn_exit.setIconSize(QSize(18, 18))
        self.btn_exit.setCursor(Qt.PointingHandCursor)
        self.btn_exit.setFixedHeight(44)
        self.btn_exit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.btn_exit.setLayoutDirection(Qt.LeftToRight)
        sidebar_layout.addWidget(self.btn_exit, 0, Qt.AlignBottom)

        self.stack = QStackedWidget()
        self.stack.setObjectName("content_area")
        self.stack.setLayoutDirection(Qt.LeftToRight)

        self.dashboard_page = InventorySummaryPage()
        self.add_page = AddTransactionPage()
        self.product_card_page = ProductCardPage()
        self.products_page = ProductsPage()
        self.subwarehouses_page = SubwarehousesPage()
        self.reports_page = ReportsPage()

        issue_button = QPushButton("＋  إضافة إذن صرف")
        issue_button.setObjectName("secondary_button")
        issue_button.setMinimumHeight(50)
        issue_button.setCursor(Qt.PointingHandCursor)
        issue_button.clicked.connect(self.open_issue_voucher)
        issue_card = self.add_page.new_button.parentWidget()
        if issue_card is not None and issue_card.layout() is not None:
            issue_card.layout().addWidget(issue_button)

        for page in (self.dashboard_page, self.add_page, self.product_card_page,
                     self.products_page, self.subwarehouses_page, self.reports_page):
            self.stack.addWidget(page)

        refresh_manager.data_changed.connect(self.dashboard_page.load_data)
        refresh_manager.products_changed.connect(self.dashboard_page.load_data)
        refresh_manager.data_changed.connect(self.subwarehouses_page.load_data)

        self.btn_dashboard.clicked.connect(lambda: self.change_page(0, self.btn_dashboard))
        self.btn_inventory.clicked.connect(lambda: self.change_page(3, self.btn_inventory))
        self.btn_reports.clicked.connect(lambda: self.change_page(5, self.btn_reports))
        self.btn_product.clicked.connect(lambda: self.change_page(2, self.btn_product))
        self.btn_subinventory.clicked.connect(lambda: self.change_page(4, self.btn_subinventory))
        self.btn_orders.clicked.connect(lambda: self.change_page(1, self.btn_orders))
        self.btn_exit.clicked.connect(self.confirm_exit)

        main_layout.addWidget(sidebar, 0, Qt.AlignLeft | Qt.AlignTop)
        main_layout.addWidget(self.stack, 1)
        self.change_page(0, self.btn_dashboard)

    @staticmethod
    def _refresh_style(widget):
        widget.style().unpolish(widget)
        widget.style().polish(widget)
        widget.update()

    def confirm_exit(self):
        answer = QMessageBox.question(self, "Logout", "هل تريد إغلاق نظام Bloom Food؟",
                                      QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if answer == QMessageBox.Yes:
            self.close()

    def open_issue_voucher(self):
        dialog = IssueVoucherDialog(self)
        if dialog.exec():
            refresh_manager.data_changed.emit()
            refresh_manager.products_changed.emit()

    def _set_sidebar_icon(self, button, active=False):
        normal_icon, active_icon = self.icon_files[button]
        icon_name = active_icon if active else normal_icon
        button.setIcon(QIcon(os.path.join(os.path.dirname(os.path.abspath(__file__)), "icons", icon_name)))

    def change_page(self, index, active_button):
        self.stack.setCurrentIndex(index)
        for button in self.icon_files:
            is_active = button == active_button
            button.setProperty("active", is_active)
            self._set_sidebar_icon(button, is_active)
            self._refresh_style(button)
