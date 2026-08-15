from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QDialog,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from database.batches import BatchRepository
from database.products import ProductRepository
from utils.refresh_manager import refresh_manager


class AddBatchDialog(QDialog):
    """Create a batch for a product with safe numeric/date validation."""

    def __init__(self, parent=None, product_id=None):
        super().__init__(parent)
        self.setWindowTitle("إضافة باتش جديد")
        self.setMinimumWidth(430)
        self.setLayoutDirection(Qt.RightToLeft)

        self.product_repo = ProductRepository()
        self.batch_repo = BatchRepository()
        self.product_id = product_id

        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(14)

        title = QLabel("إضافة باتش جديد")
        title.setObjectName("section_title")
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(10)

        self.product_combo = QComboBox()
        products = self.product_repo.get_all_products()
        for _, row in products.iterrows():
            self.product_combo.addItem(str(row["Product_Name"]), str(row["product_ID"]))

        if self.product_id:
            index = self.product_combo.findData(str(self.product_id))
            if index >= 0:
                self.product_combo.setCurrentIndex(index)

        self.batch_code = QLabel()
        from PySide6.QtWidgets import QLineEdit
        self.batch_code = QLineEdit()
        self.batch_code.setPlaceholderText("مثال: K14")

        self.production_date = QDateEdit(QDate.currentDate())
        self.production_date.setCalendarPopup(True)
        self.production_date.setDisplayFormat("yyyy-MM-dd")

        self.expiry_date = QDateEdit(QDate.currentDate())
        self.expiry_date.setCalendarPopup(True)
        self.expiry_date.setDisplayFormat("yyyy-MM-dd")

        self.opening_balance = QDoubleSpinBox()
        self.opening_balance.setRange(0.0, 999999999.0)
        self.opening_balance.setDecimals(3)
        self.opening_balance.setSingleStep(1.0)

        form.addRow("الصنف", self.product_combo)
        form.addRow("كود الباتش", self.batch_code)
        form.addRow("تاريخ الإنتاج", self.production_date)
        form.addRow("تاريخ الصلاحية", self.expiry_date)
        form.addRow("رصيد أول المدة", self.opening_balance)
        layout.addLayout(form)

        buttons = QHBoxLayout()
        save = QPushButton("حفظ الباتش")
        save.setObjectName("primary_button")
        cancel = QPushButton("إلغاء")
        cancel.setObjectName("secondary_button")
        save.clicked.connect(self.save_batch)
        cancel.clicked.connect(self.reject)
        buttons.addWidget(save)
        buttons.addWidget(cancel)
        layout.addLayout(buttons)

        self.batch_code.setFocus()

    def save_batch(self):
        product_id = self.product_combo.currentData()
        code = self.batch_code.text().strip()
        production = self.production_date.date()
        expiry = self.expiry_date.date()
        opening = self.opening_balance.value()

        if not product_id:
            QMessageBox.warning(self, "خطأ", "اختيار الصنف مطلوب.")
            return
        if not code:
            QMessageBox.warning(self, "خطأ", "كود الباتش مطلوب.")
            return
        if expiry < production:
            QMessageBox.warning(self, "خطأ", "تاريخ الصلاحية لا يمكن أن يكون قبل تاريخ الإنتاج.")
            return

        try:
            self.batch_repo.add_batch(
                product_id,
                code,
                production.toPython(),
                expiry.toPython(),
                opening,
            )
        except Exception as exc:
            QMessageBox.critical(self, "خطأ", str(exc))
            return

        refresh_manager.data_changed.emit()
        QMessageBox.information(self, "تم الحفظ", "تمت إضافة الباتش بنجاح.")
        self.accept()
