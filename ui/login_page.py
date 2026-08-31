import os

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFrame,
    QMessageBox,
    QSizePolicy,
)


class LoginWindow(QWidget):
    """Bloom Food login screen with a small local demo account."""

    DEMO_EMAIL = "abdelwahabrefat@bloomfood.com"
    DEMO_PASSWORD = "1041999"
    DISPLAY_NAME = "عبدالوهاب"

    def __init__(self):
        super().__init__()
        self.authenticated = False
        self.user_name = self.DISPLAY_NAME
        self.setWindowTitle("Bloom Food - تسجيل الدخول")
        self.setMinimumSize(900, 600)
        self.resize(1050, 680)
        self.setLayoutDirection(Qt.RightToLeft)
        self._build_ui()

    def _build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(55, 45, 55, 45)
        root.setSpacing(55)

        brand = QVBoxLayout()
        brand.setAlignment(Qt.AlignCenter)

        logo_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "icons",
            "bloom_logo_light.svg",
        )
        logo = QLabel()
        logo.setPixmap(QPixmap(logo_path).scaled(250, 90, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo.setAlignment(Qt.AlignCenter)
        brand.addWidget(logo)

        tagline = QLabel("نظام إدارة المخزون")
        tagline.setObjectName("login_tagline")
        tagline.setAlignment(Qt.AlignCenter)
        brand.addWidget(tagline)
        brand.addSpacing(22)

        avatar_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "icons",
            "abdelwahab_avatar.png",
        )
        avatar = QLabel()
        avatar.setObjectName("login_avatar")
        avatar.setPixmap(QPixmap(avatar_path).scaled(150, 150, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
        avatar.setFixedSize(150, 150)
        avatar.setAlignment(Qt.AlignCenter)
        brand.addWidget(avatar, alignment=Qt.AlignCenter)

        name = QLabel("عبدالوهاب رفعت")
        name.setObjectName("login_name")
        name.setAlignment(Qt.AlignCenter)
        brand.addWidget(name)
        brand.addStretch()

        card = QFrame()
        card.setObjectName("login_card")
        card.setMinimumWidth(390)
        card.setMaximumWidth(450)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(38, 38, 38, 38)
        card_layout.setSpacing(8)

        title = QLabel("تسجيل الدخول")
        title.setObjectName("login_title")
        card_layout.addWidget(title)

        subtitle = QLabel("سجّل الدخول للوصول إلى نظام Bloom Food")
        subtitle.setObjectName("login_subtitle")
        card_layout.addWidget(subtitle)
        card_layout.addSpacing(18)

        email_label = QLabel("البريد الإلكتروني")
        email_label.setObjectName("form_label")
        card_layout.addWidget(email_label)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("name@bloomfood.com")
        self.email_input.setText(self.DEMO_EMAIL)
        self.email_input.setClearButtonEnabled(True)
        card_layout.addWidget(self.email_input)

        password_label = QLabel("كلمة المرور")
        password_label.setObjectName("form_label")
        card_layout.addWidget(password_label)

        password_row = QHBoxLayout()
        password_row.setSpacing(6)
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("أدخل كلمة المرور")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setText(self.DEMO_PASSWORD)
        self.password_input.returnPressed.connect(self.login)

        self.show_password = QPushButton("إظهار")
        self.show_password.setObjectName("secondary_button")
        self.show_password.setFixedWidth(78)
        self.show_password.setMinimumHeight(45)
        self.show_password.clicked.connect(self.toggle_password)
        password_row.addWidget(self.password_input, 1)
        password_row.addWidget(self.show_password)
        card_layout.addLayout(password_row)
        card_layout.addSpacing(20)

        self.login_button = QPushButton("تسجيل الدخول")
        self.login_button.setObjectName("primary_button")
        self.login_button.setMinimumHeight(50)
        self.login_button.setCursor(Qt.PointingHandCursor)
        self.login_button.clicked.connect(self.login)
        card_layout.addWidget(self.login_button)

        hint = QLabel("استخدم بيانات الحساب المصرح بها من مسؤول النظام")
        hint.setObjectName("login_hint")
        hint.setAlignment(Qt.AlignCenter)
        hint.setWordWrap(True)
        card_layout.addWidget(hint)
        card_layout.addStretch()

        root.addLayout(brand, 1)
        root.addWidget(card)

    def toggle_password(self):
        visible = self.password_input.echoMode() == QLineEdit.Password
        self.password_input.setEchoMode(QLineEdit.Normal if visible else QLineEdit.Password)
        self.show_password.setText("إخفاء" if visible else "إظهار")

    def login(self):
        email = self.email_input.text().strip().lower()
        password = self.password_input.text()

        if email == self.DEMO_EMAIL and password == self.DEMO_PASSWORD:
            self.authenticated = True
            self.close()
            return

        QMessageBox.warning(
            self,
            "بيانات الدخول غير صحيحة",
            "البريد الإلكتروني أو كلمة المرور غير صحيحة.",
        )
        self.password_input.selectAll()
        self.password_input.setFocus()
