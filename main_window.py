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
    QMessageBox,
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
        self.resize(1250, 750)
        self._sidebar_light = False

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # -------------------------------------------------------------
        # Sidebar — focused navigation, based on the selected reference.
        # -------------------------------------------------------------
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(270)
        self.sidebar = sidebar

        sidebar_layout = QVBoxLayout()
        sidebar_layout.setContentsMargins(18, 18, 18, 16)
        sidebar_layout.setSpacing(6)

        base_dir = os.path.dirname(os.path.abspath(__file__))
        icons_dir = os.path.join(base_dir, "icons")

        # Logo / brand block
        logo = QLabel()
        logo.setObjectName("sidebar_logo")
        self.sidebar_logo = logo
        self.sidebar_logo_dark = os.path.join(icons_dir, "bloom_logo.svg")
        self.sidebar_logo_light = os.path.join(icons_dir, "bloom_logo_light.svg")
        logo.setPixmap(QPixmap(self.sidebar_logo_dark))
        logo.setScaledContents(True)
        logo.setFixedHeight(64)
        logo.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(logo)
        sidebar_layout.addSpacing(8)

        sidebar_line = QFrame()
        sidebar_line.setObjectName("sidebar_line")
        sidebar_line.setFrameShape(QFrame.HLine)
        sidebar_line.setFrameShadow(QFrame.Plain)
        sidebar_layout.addWidget(sidebar_line)
        sidebar_layout.addSpacing(14)

        # Navigation
        self.btn_dashboard = QPushButton("الرئيسية")
        self.btn_add = QPushButton("إضافة حركة")
        self.btn_search = QPushButton("كارت الصنف")
        self.btn_products = QPushButton("إدارة الأصناف")
        self.btn_subwarehouses = QPushButton("المخازن الفرعية")
        self.btn_reports = QPushButton("التقارير")

        self.icon_files = {
            self.btn_dashboard: ("dashboard.svg", "dashboard_active.svg"),
            self.btn_add: ("transaction.svg", "transaction_active.svg"),
            self.btn_search: ("product_card.svg", "product_card_active.svg"),
            self.btn_products: ("products.svg", "products_active.svg"),
            self.btn_subwarehouses: ("subwarehouse.svg", "subwarehouse_active.svg"),
            self.btn_reports: ("reports.svg", "reports_active.svg"),
        }

        for button, (icon_name, _) in self.icon_files.items():
            button.setIcon(QIcon(os.path.join(icons_dir, icon_name)))
            button.setIconSize(QSize(22, 22))

        for button in self.icon_files:
            button.setObjectName("sidebar_button")
            button.setCursor(Qt.PointingHandCursor)
            button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            button.setLayoutDirection(Qt.RightToLeft)
            sidebar_layout.addWidget(button)

        sidebar_layout.addStretch(1)

        # Admin profile card
        admin_card = QFrame()
        admin_card.setObjectName("admin_card")
        admin_layout = QHBoxLayout(admin_card)
        admin_layout.setContentsMargins(10, 9, 10, 9)
        admin_layout.setSpacing(10)
        admin_layout.setDirection(QHBoxLayout.RightToLeft)

        avatar = QLabel()
        avatar.setObjectName("admin_avatar")
        avatar.setPixmap(QPixmap(os.path.join(icons_dir, "admin_avatar.svg")))
        avatar.setFixedSize(40, 40)
        avatar.setScaledContents(True)

        admin_text = QVBoxLayout()
        admin_text.setContentsMargins(0, 0, 0, 0)
        admin_text.setSpacing(1)
        admin_name = QLabel("Admin")
        admin_name.setObjectName("admin_name")
        admin_role = QLabel("مدير النظام")
        admin_role.setObjectName("admin_role")
        admin_text.addWidget(admin_name)
        admin_text.addWidget(admin_role)

        admin_layout.addWidget(avatar)
        admin_layout.addLayout(admin_text, 1)
        sidebar_layout.addWidget(admin_card)
        sidebar_layout.addSpacing(8)

        # Three utility buttons from the reference design.
        utility_row = QHBoxLayout()
        utility_row.setContentsMargins(0, 0, 0, 0)
        utility_row.setSpacing(7)

        self.btn_theme = self._make_sidebar_utility_button(
            "sidebar_sun.svg", "تغيير مظهر الشريط الجانبي"
        )
        self.btn_notifications = self._make_sidebar_utility_button(
            "sidebar_bell.svg", "التنبيهات"
        )
        self.btn_exit = self._make_sidebar_utility_button(
            "sidebar_logout.svg", "خروج من البرنامج"
        )

        utility_row.addWidget(self.btn_theme)
        utility_row.addWidget(self.btn_notifications)
        utility_row.addWidget(self.btn_exit)
        sidebar_layout.addLayout(utility_row)

        sidebar.setLayout(sidebar_layout)

        # -------------------------------------------------------------
        # Content
        # -------------------------------------------------------------
        self.stack = QStackedWidget()
        self.stack.setObjectName("content_area")

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

        self.stack.addWidget(self.dashboard_page)
        self.stack.addWidget(self.add_page)
        self.stack.addWidget(self.product_card_page)
        self.stack.addWidget(self.products_page)
        self.stack.addWidget(self.subwarehouses_page)
        self.stack.addWidget(self.reports_page)

        refresh_manager.data_changed.connect(self.dashboard_page.load_data)
        refresh_manager.products_changed.connect(self.dashboard_page.load_data)
        refresh_manager.data_changed.connect(self.subwarehouses_page.load_data)

        self.btn_dashboard.clicked.connect(lambda: self.change_page(0, self.btn_dashboard))
        self.btn_add.clicked.connect(lambda: self.change_page(1, self.btn_add))
        self.btn_search.clicked.connect(lambda: self.change_page(2, self.btn_search))
        self.btn_products.clicked.connect(lambda: self.change_page(3, self.btn_products))
        self.btn_subwarehouses.clicked.connect(lambda: self.change_page(4, self.btn_subwarehouses))
        self.btn_reports.clicked.connect(lambda: self.change_page(5, self.btn_reports))

        self.btn_theme.clicked.connect(self.toggle_sidebar_theme)
        self.btn_notifications.clicked.connect(self.show_notifications)
        self.btn_exit.clicked.connect(self.confirm_exit)

        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.stack)
        self.setLayout(main_layout)

        self.change_page(0, self.btn_dashboard)

    def _make_sidebar_utility_button(self, icon_name, tooltip):
        button = QPushButton()
        button.setObjectName("sidebar_utility_button")
        button.setIcon(QIcon(os.path.join(os.path.dirname(os.path.abspath(__file__)), "icons", icon_name)))
        button.setIconSize(QSize(21, 21))
        button.setToolTip(tooltip)
        button.setCursor(Qt.PointingHandCursor)
        button.setFixedSize(46, 42)
        return button

    def toggle_sidebar_theme(self):
        self._sidebar_light = not self._sidebar_light
        self.sidebar.setProperty("lightMode", self._sidebar_light)
        self.sidebar_logo.setPixmap(
            QPixmap(self.sidebar_logo_light if self._sidebar_light else self.sidebar_logo_dark)
        )
        self._refresh_style(self.sidebar)
        self.btn_theme.setToolTip(
            "الوضع الداكن للشريط الجانبي" if self._sidebar_light else "الوضع الفاتح للشريط الجانبي"
        )
        self.change_page(self.stack.currentIndex(), self._active_button())

    def _active_button(self):
        for button in self.icon_files:
            if button.property("active") is True:
                return button
        return self.btn_dashboard

    @staticmethod
    def _refresh_style(widget):
        widget.style().unpolish(widget)
        widget.style().polish(widget)
        widget.update()

    def show_notifications(self):
        QMessageBox.information(self, "التنبيهات", "لا توجد تنبيهات جديدة حاليًا.")

    def confirm_exit(self):
        answer = QMessageBox.question(
            self,
            "خروج",
            "هل تريد إغلاق نظام Bloom Food؟",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
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
            self._refresh_style(button)
