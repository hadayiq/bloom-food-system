import sys
from database.products import ProductRepository
from database.transactions import TransactionRepository
import os
from PySide6.QtWidgets import QMessageBox
from PySide6.QtWidgets import QStackedWidget
from ui.dashboard_page import DashboardPage
from ui.add_transaction_page import AddTransactionPage
from ui.product_card_page import ProductCardPage
from ui.reports_page import ReportsPage
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QComboBox,
    QLineEdit,
    QTextEdit
)

app = QApplication(sys.argv)

window = QWidget()
window.setWindowTitle("Inventory System")
window.resize(1200, 700)

# ======================
# القائمة الجانبية
# ======================

sidebar = QFrame()
sidebar.setFixedWidth(250)

sidebar_layout = QVBoxLayout()

title = QLabel("Inventory System")

btn_dashboard = QPushButton("Dashboard")
btn_add = QPushButton("إضافة حركة")
btn_search = QPushButton("كارت الصنف")
btn_reports = QPushButton("التقارير")

sidebar_layout.addWidget(title)
sidebar_layout.addSpacing(30)

sidebar_layout.addWidget(btn_dashboard)
sidebar_layout.addWidget(btn_add)
sidebar_layout.addWidget(btn_search)
sidebar_layout.addWidget(btn_reports)

sidebar_layout.addStretch()

sidebar.setLayout(sidebar_layout)

# ======================
# الجزء الرئيسي
# ======================

content = QFrame()

content_layout = QVBoxLayout()

page_title = QLabel("إضافة حركة جديدة")

# اختيار الصنف
product_label = QLabel("الصنف")
product_combo = QComboBox()

excel_path = os.path.join(
    os.path.dirname(__file__),
    "inventory.xlsx"
)

repo = ProductRepository()

product_combo.addItems(
    repo.get_product_names()
)

# نوع الحركة
type_label = QLabel("نوع الحركة")
type_combo = QComboBox()

type_combo.addItems([
    "إنتاج",
    "مشتريات",
    "صرف للتجزئة",
    "صرف للتسليمات",
    "مردودات مبيعات"
])

# الكمية
quantity_label = QLabel("الكمية")
quantity_input = QLineEdit()

# الملاحظات
notes_label = QLabel("ملاحظات")
notes_input = QTextEdit()
def save_transaction():

    quantity = quantity_input.text()

    if quantity == "":
        QMessageBox.warning(
            window,
            "خطأ",
            "من فضلك أدخل الكمية"
        )
        return

    product = product_combo.currentText()
    transaction_type = type_combo.currentText()
    notes = notes_input.toPlainText()

    repo = TransactionRepository()

    repo.save_transaction(
        product,
        transaction_type,
        quantity,
        notes
    )

    QMessageBox.information(
        window,
        "نجاح",
        "تم حفظ الحركة بنجاح"
    )

    quantity_input.clear()
    notes_input.clear()

    product_combo.setCurrentIndex(0)
    type_combo.setCurrentIndex(0)
# زر الحفظ
save_button = QPushButton("حفظ الحركة")
save_button.clicked.connect(save_transaction)

content_layout.addWidget(page_title)

content_layout.addWidget(product_label)
content_layout.addWidget(product_combo)

content_layout.addWidget(type_label)
content_layout.addWidget(type_combo)

content_layout.addWidget(quantity_label)
content_layout.addWidget(quantity_input)

content_layout.addWidget(notes_label)
content_layout.addWidget(notes_input)

content_layout.addWidget(save_button)

content_layout.addStretch()

content.setLayout(content_layout)

# ======================
# تقسيم الشاشة
# ======================

main_layout = QHBoxLayout()

main_layout.addWidget(sidebar)
main_layout.addWidget(stack)

window.setLayout(main_layout)


window.show()


sys.exit(app.exec())