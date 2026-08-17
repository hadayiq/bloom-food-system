from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QDoubleSpinBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QScrollArea, QFrame, QMessageBox,
)
from PySide6.QtCore import Qt

from database.products import ProductRepository
from database.batches import BatchRepository
from database.issues import IssueRepository


class IssueVoucherDialog(QDialog):
    """Create one issue voucher containing many product/batch lines."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("إضافة إذن صرف")
        self.resize(1180, 820)
        self.setMinimumSize(980, 680)
        self.setSizeGripEnabled(True)
        self.product_repo = ProductRepository()
        self.batch_repo = BatchRepository()
        self.issue_repo = IssueRepository()
        self.products = self.product_repo.get_product_names() or []
        self.rows = []
        self._build_ui()
        self._load_products()
        self._load_next_issue_no()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(18, 16, 18, 14)
        root.setSpacing(10)

        # Main content scrolls; actions remain fixed at the bottom.
        content_scroll = QScrollArea()
        content_scroll.setWidgetResizable(True)
        content_scroll.setFrameShape(QFrame.NoFrame)
        content_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        content_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        content = QFrame()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(6, 6, 12, 6)
        content_layout.setSpacing(12)
        content_scroll.setWidget(content)
        root.addWidget(content_scroll, 1)

        title = QLabel("إذن صرف")
        title.setObjectName("page_title")
        subtitle = QLabel("تحميل أصناف متعددة إلى مخزن المندوب في إذن واحد")
        subtitle.setObjectName("page_subtitle")
        content_layout.addWidget(title)
        content_layout.addWidget(subtitle)

        header_card = QFrame()
        header_card.setObjectName("transaction_card")
        header_layout = QGridLayout(header_card)
        header_layout.setContentsMargins(16, 14, 16, 14)
        header_layout.setHorizontalSpacing(14)
        header_layout.setVerticalSpacing(8)

        self.issue_no = QLineEdit()
        self.issue_no.setMinimumHeight(40)
        self.issue_no.setPlaceholderText("رقم الإذن")
        self.rep_input = QLineEdit()
        self.rep_input.setMinimumHeight(40)
        self.rep_input.setPlaceholderText("اسم المندوب / العميل")

        date_value = __import__("datetime").datetime.now().strftime("%Y-%m-%d")
        self.date_label = QLabel(date_value)
        self.date_label.setObjectName("section_description")
        self.date_label.setMinimumHeight(40)
        self.date_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)

        self._add_field(header_layout, 0, 0, "رقم الإذن", self.issue_no)
        self._add_field(header_layout, 0, 1, "التاريخ", self.date_label)
        self._add_field(header_layout, 0, 2, "المندوب / العميل", self.rep_input)
        content_layout.addWidget(header_card)

        summary_title = QLabel("إجماليات الأصناف")
        summary_title.setObjectName("section_title")
        content_layout.addWidget(summary_title)

        self.summary_scroll = QScrollArea()
        self.summary_scroll.setWidgetResizable(True)
        self.summary_scroll.setFrameShape(QFrame.NoFrame)
        self.summary_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.summary_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.summary_scroll.setMinimumHeight(72)
        self.summary_scroll.setMaximumHeight(132)
        self.summary_widget = QFrame()
        self.summary_grid = QGridLayout(self.summary_widget)
        self.summary_grid.setContentsMargins(2, 2, 2, 2)
        self.summary_grid.setHorizontalSpacing(8)
        self.summary_grid.setVerticalSpacing(8)
        self.summary_scroll.setWidget(self.summary_widget)
        content_layout.addWidget(self.summary_scroll)

        table_title = QLabel("الأصناف")
        table_title.setObjectName("section_title")
        content_layout.addWidget(table_title)

        table_frame = QFrame()
        table_frame.setObjectName("transaction_card")
        table_layout = QVBoxLayout(table_frame)
        table_layout.setContentsMargins(8, 8, 8, 8)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["الصنف", "الكمية", "الباتش", "الصلاحية", "إجراء"])
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionMode(QTableWidget.NoSelection)
        self.table.setFocusPolicy(Qt.NoFocus)
        self.table.setMinimumHeight(260)
        self.table.setMaximumHeight(440)
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.table.setWordWrap(False)
        header = self.table.horizontalHeader()
        header.setHighlightSections(False)
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        table_layout.addWidget(self.table)
        content_layout.addWidget(table_frame)

        hint = QLabel("يمكنك إضافة نفس الصنف مرة أخرى إذا احتجت صرفه من Batch مختلف.")
        hint.setObjectName("section_description")
        hint.setWordWrap(True)
        content_layout.addWidget(hint)
        content_layout.addStretch(1)

        # Fixed action bar: never scrolls away or overlaps form fields.
        bottom_frame = QFrame()
        bottom_frame.setObjectName("transaction_card")
        bottom = QHBoxLayout(bottom_frame)
        bottom.setContentsMargins(10, 8, 10, 8)
        bottom.setSpacing(10)
        self.cancel_button = QPushButton("إلغاء")
        self.cancel_button.setObjectName("secondary_button")
        self.cancel_button.setMinimumHeight(46)
        self.cancel_button.clicked.connect(self.reject)
        self.save_button = QPushButton("حفظ إذن الصرف")
        self.save_button.setObjectName("primary_button")
        self.save_button.setMinimumHeight(46)
        self.save_button.setMinimumWidth(190)
        self.save_button.clicked.connect(self.save_issue)
        bottom.addWidget(self.cancel_button)
        bottom.addStretch()
        bottom.addWidget(self.save_button)
        root.addWidget(bottom_frame)

    def _add_field(self, layout, row, col, label_text, widget):
        box = QVBoxLayout()
        box.setSpacing(4)
        label = QLabel(label_text)
        label.setObjectName("form_label")
        box.addWidget(label)
        box.addWidget(widget)
        layout.addLayout(box, row, col)

    def _load_next_issue_no(self):
        self.issue_no.setText(self.issue_repo.get_next_issue_no())
        self.issue_no.selectAll()

    def _load_products(self):
        self.table.setRowCount(0)
        self.rows = []
        for product in self.products:
            self._add_product_row(product)
        self._refresh_summary()

    def _get_batches(self, product):
        product_id = self.product_repo.get_product_id(product)
        batches = self.batch_repo.get_batches(product_id) if product_id is not None else []
        return sorted(batches, key=lambda b: str(b.get("expiry_date") or "9999-12-31"))

    def _add_product_row(self, product, selected_batch=None):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setRowHeight(row, 58)
        product_item = QTableWidgetItem(product)
        product_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.table.setItem(row, 0, product_item)

        quantity = QDoubleSpinBox()
        quantity.setRange(0.0, 999999999.0)
        quantity.setDecimals(2)
        quantity.setSingleStep(1.0)
        quantity.setButtonSymbols(QDoubleSpinBox.NoButtons)
        quantity.setMinimumHeight(40)
        quantity.setAlignment(Qt.AlignCenter)
        quantity.valueChanged.connect(self._refresh_summary)
        self.table.setCellWidget(row, 1, quantity)

        batch_combo = QComboBox()
        batch_combo.setMinimumHeight(40)
        batch_combo.addItem("بدون باتش", "")
        batches = self._get_batches(product)
        if batches:
            batch_combo.clear()
            for batch in batches:
                batch_combo.addItem(str(batch["code"]), str(batch["code"]))
            if selected_batch:
                index = batch_combo.findData(selected_batch)
                batch_combo.setCurrentIndex(index if index >= 0 else 0)
            else:
                batch_combo.setCurrentIndex(0)
        else:
            batch_combo.setEnabled(False)
        self.table.setCellWidget(row, 2, batch_combo)

        expiry = QLabel("—")
        expiry.setAlignment(Qt.AlignCenter)
        expiry.setObjectName("section_description")
        self.table.setCellWidget(row, 3, expiry)
        batch_combo.currentIndexChanged.connect(
            lambda _=0, r=row, combo=batch_combo, label=expiry: self._update_expiry(r, combo, label)
        )
        self._update_expiry(row, batch_combo, expiry)

        add_button = QPushButton("＋ Batch")
        add_button.setObjectName("secondary_button")
        add_button.setMinimumHeight(36)
        add_button.setCursor(Qt.PointingHandCursor)
        add_button.clicked.connect(lambda _=False, p=product: self._add_product_row(p))
        self.table.setCellWidget(row, 4, add_button)

        self.rows.append({"product": product, "quantity": quantity, "batch": batch_combo, "expiry": expiry})
        self.table.scrollToItem(product_item, QTableWidget.PositionAtCenter)

    def _update_expiry(self, row, combo, label):
        code = combo.currentData()
        if not code:
            label.setText("—")
            return
        product = self.table.item(row, 0).text()
        product_id = self.product_repo.get_product_id(product)
        batch = self.batch_repo.get_batch(product_id, code)
        label.setText(str(batch["expiry_date"]) if batch else "—")

    def _refresh_summary(self, *_):
        while self.summary_grid.count():
            item = self.summary_grid.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        totals = {}
        for entry in self.rows:
            qty = float(entry["quantity"].value())
            if qty > 0:
                totals[entry["product"]] = totals.get(entry["product"], 0.0) + qty
        for index, product in enumerate(self.products):
            if product not in totals:
                continue
            card = QFrame()
            card.setObjectName("kpi_card")
            layout = QVBoxLayout(card)
            layout.setContentsMargins(10, 7, 10, 7)
            layout.setSpacing(1)
            name = QLabel(product)
            name.setObjectName("kpi_title")
            name.setAlignment(Qt.AlignCenter)
            value = QLabel(f"{totals[product]:,.2f}")
            value.setObjectName("kpi_value")
            value.setAlignment(Qt.AlignCenter)
            layout.addWidget(name)
            layout.addWidget(value)
            self.summary_grid.addWidget(card, index // 4, index % 4)
        self.summary_widget.adjustSize()

    def _collect_lines(self):
        lines = []
        seen = set()
        for entry in self.rows:
            quantity = float(entry["quantity"].value())
            if quantity <= 0:
                continue
            product = entry["product"]
            batch_code = str(entry["batch"].currentData() or "").strip()
            key = (product, batch_code.lower())
            if key in seen:
                raise ValueError(f"الصنف {product} مكرر بنفس الباتش. استخدم Batch مختلفًا.")
            seen.add(key)
            lines.append({"product": product, "batch_code": batch_code, "quantity": quantity})
        return lines

    def save_issue(self):
        try:
            lines = self._collect_lines()
            issue_no = self.issue_repo.save_issue(self.issue_no.text(), self.rep_input.text(), lines)
        except Exception as exc:
            QMessageBox.warning(self, "تعذر حفظ الإذن", str(exc))
            return
        QMessageBox.information(self, "تم الحفظ", f"تم حفظ إذن الصرف رقم {issue_no} وتحميل البضاعة إلى مخزن المندوب.")
        self.accept()
