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
from ui.issue_voucher_dialog import IssueVoucherDialog
from ui.subwarehouses_page import SubwarehousesPage

from utils.refresh_manager import refresh_manager


class MainWindow(QWidget):

    def __init__(self):

        super().__init__()

        self.setWindowTitle("Bloom Food - Inventory System")
        self.resize(1250, 750)

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(250)

        sidebar_layout = QVBoxLayout()
        sidebar_layout.setContentsMargins(18, 24, 18, 18)
        sidebar_layout.setSpacing(6)

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

        self.btn_dashboard = QPushButton("Dashboard")
        self.btn_add = QPushButton("إضافة حركة")
        self.btn_search = QPushButton("كارت الصنف")
        self.btn_products = QPushButton("إدارة الأصناف")
        self.btn_subwarehouses = QPushButton("المخازن الفرعية")
        self.btn_reports = QPushButton("التقارير")

        base_dir = os.path.dirname(os.path.abspath(__file__))
        icons_dir = os.path.join(base_dir, "icons")

        self.icon_files = {
            self.btn_dashboard: ("dashboard.svg", "dashboard_active.svg"),
            self.btn_add: ("transaction.svg", "transaction_active.svg"),
            self.btn_search: ("product_card.svg", "product_card_active.svg"),
            self.btn_products: ("products.svg", "products_active.svg"),
            self.btn_subwarehouses: ("subwarehouse.svg", "subwarehouse_active.svg"),
            self.btn_reports: ("reports.svg", "reports_active.svg"),
        }

        icon_size = QSize(22, 22)

        for button, (icon_name, _) in self.icon_files.items():
            icon_path = os.path.join(icons_dir, icon_name)
            icon = QIcon(icon_path)
            print(
                f"[ICON] {icon_name} | "
                f"EXISTS={os.path.exists(icon_path)} | "
                f"NULL={icon.isNull()}"
            )
            button.setIcon(icon)
            button.setIconSize(icon_size)

        buttons = [
            self.btn_dashboard,
            self.btn_add,
            self.btn_search,
            self.btn_products,
            self.btn_subwarehouses,
            self.btn_reports,
        ]

        for button in buttons:
            button.setObjectName("sidebar_button")
            button.setCursor(Qt.PointingHandCursor)
            button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            button.setLayoutDirection(Qt.RightToLeft)
            sidebar_layout.addWidget(button)

        sidebar_layout.addStretch()

        footer = QLabel("Bloom Food\n" "Inventory System")
        footer.setObjectName("sidebar_footer")
        footer.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(footer)

        sidebar.setLayout(sidebar_layout)

        self.stack = QStackedWidget()
        self.stack.setObjectName("content_area")

        self.dashboard_page = InventorySummaryPage()
        self.add_page = AddTransactionPage()
        self.product_card_page = ProductCardPage()
        self.products_page = ProductsPage()
        self.subwarehouses_page = SubwarehousesPage()
        self.reports_page = ReportsPage()

        # The issue voucher belongs to the Add Transaction workflow, but is a
        # separate multi-line document so the user never has to enter 27
        # individual transactions for one delivery.
        issue_button = QPushButton("＋  إضافة إذن صرف")
        issue_button.setObjectName("secondary_button")
        issue_button.setMinimumHeight(50)
        issue_button.setCursor(Qt.PointingHandCursor)
        issue_button.clicked.connect(self.open_issue_voucher)
        issue_card = self.add_page.new_button.parentWidget()
        if issue_card is not None and issue_card.layout() is not None:
            issue_card.layout().addWidget(issue_button)

        self.stack.addWidget(self.dashboard_page)
        self.stack.addWidget(self.add_page)
        self.stack.addWidget(self.product_card_page)
        self.stack.addWidget(self.products_page)
        self.stack.addWidget(self.subwarehouses_page)
        self.stack.addWidget(self.reports_page)

        refresh_manager.data_changed.connect(self.dashboard_page.load_data)
        refresh_manager.products_changed.connect(self.dashboard_page.load_data)
        refresh_manager.data_changed.connect(self.subwarehouses_page.load_data)

        self.btn_dashboard.clicked.connect(
            lambda: self.change_page(0, self.btn_dashboard)
        )
        self.btn_add.clicked.connect(lambda: self.change_page(1, self.btn_add))
        self.btn_search.clicked.connect(lambda: self.change_page(2, self.btn_search))
        self.btn_products.clicked.connect(
            lambda: self.change_page(3, self.btn_products)
        )
        self.btn_subwarehouses.clicked.connect(
            lambda: self.change_page(4, self.btn_subwarehouses)
        )
        self.btn_reports.clicked.connect(
            lambda: self.change_page(5, self.btn_reports)
        )

        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.stack)
        self.setLayout(main_layout)

        self.change_page(0, self.btn_dashboard)

    def open_issue_voucher(self):
        dialog = IssueVoucherDialog(self)
        if dialog.exec():
            refresh_manager.data_changed.emit()
            refresh_manager.products_changed.emit()

    def _set_sidebar_icon(self, button, active=False):
        normal_icon, active_icon = self.icon_files[button]
        icon_name = active_icon if active else normal_icon
        icon_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "icons",
            icon_name,
        )
        button.setIcon(QIcon(icon_path))

    def change_page(self, index, active_button):
        self.stack.setCurrentIndex(index)

        buttons = [
            self.btn_dashboard,
            self.btn_add,
            self.btn_search,
            self.btn_products,
            self.btn_subwarehouses,
            self.btn_reports,
        ]

        for button in buttons:
            is_active = button == active_button
            button.setProperty("active", is_active)
            self._set_sidebar_icon(button, is_active)
            button.style().unpolish(button)
            button.style().polish(button)
            button.update()
