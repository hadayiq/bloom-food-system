import os

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QFrame, QMessageBox, QCheckBox, QToolButton, QBoxLayout,
)


class LoginWindow(QDialog):
    """Bloom Food login screen matching the approved reference layout."""
    DEMO_EMAIL = "abdelwahabrefat@bloomfood.com"
    DEMO_PASSWORD = "1041999"
    DISPLAY_NAME = "عبدالوهاب"

    def __init__(self):
        super().__init__()
        self.user_name = self.DISPLAY_NAME
        self.setWindowTitle("Bloom Food - تسجيل الدخول")
        self.setMinimumSize(1100, 700)
        self.resize(1280, 820)
        self.setModal(True)
        self.setLayoutDirection(Qt.LeftToRight)
        self._build_ui()

    def _build_ui(self):
        self.setStyleSheet("""
            QDialog { background: #F7F8FA; }
            QLabel { background: transparent; }
            QFrame#login_card { background: #FFFFFF; border: 1px solid #E4E7EC; border-radius: 18px; }
            QLabel#login_heading { color: #101828; font-family: Inter, 'Segoe UI'; font-size: 30px; font-weight: 600; }
            QLabel#login_support { color: #667085; font-family: Inter, 'Segoe UI'; font-size: 16px; font-weight: 400; }
            QLabel#form_label { color: #344054; font-family: Inter, 'Segoe UI'; font-size: 14px; font-weight: 500; }
            QLineEdit#login_input { background: #FFFFFF; color: #101828; border: 1px solid #D0D5DD; border-radius: 8px; padding: 0 14px; font-family: Inter, 'Segoe UI'; font-size: 16px; }
            QLineEdit#login_input:focus { border: 1px solid #1366D9; }
            QCheckBox#remember { color: #344054; font-family: Inter, 'Segoe UI'; font-size: 14px; spacing: 8px; }
            QCheckBox#remember::indicator { width: 18px; height: 18px; border: 1px solid #D0D5DD; border-radius: 4px; background: #FFFFFF; }
            QCheckBox#remember::indicator:checked { background: #1366D9; border-color: #1366D9; }
            QPushButton#link_button { border: none; background: transparent; color: #1366D9; font-family: Inter, 'Segoe UI'; font-size: 14px; font-weight: 500; padding: 0; }
            QPushButton#sign_in { background: #1769E8; color: #FFFFFF; border: none; border-radius: 6px; font-family: Inter, 'Segoe UI'; font-size: 16px; font-weight: 500; }
            QPushButton#sign_in:hover { background: #125BCB; }
            QPushButton#google_button { background: #FFFFFF; color: #101828; border: 1px solid #D0D5DD; border-radius: 6px; font-family: Inter, 'Segoe UI'; font-size: 16px; font-weight: 500; }
            QLabel#brand_tag { color: #1366D9; font-family: Inter, 'Segoe UI'; font-size: 16px; font-weight: 500; }
            QToolButton#password_eye { border: none; background: transparent; color: #667085; font-size: 18px; padding: 0; }
        """)

        root = QHBoxLayout(self)
        root.setContentsMargins(40, 32, 40, 32)
        root.setSpacing(44)
        root.setDirection(QBoxLayout.LeftToRight)

        brand_panel = QFrame()
        brand_layout = QVBoxLayout(brand_panel)
        brand_layout.setContentsMargins(20, 20, 20, 20)
        brand_layout.setAlignment(Qt.AlignCenter)
        logo = QLabel()
        logo_pixmap = QPixmap(self._asset_path("bloom_logo_splash.svg"))
        if not logo_pixmap.isNull():
            logo.setPixmap(logo_pixmap.scaled(440, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo.setFixedSize(480, 320)
        logo.setAlignment(Qt.AlignCenter)
        brand_layout.addWidget(logo, 0, Qt.AlignCenter)
        brand_layout.addStretch(1)
        root.addWidget(brand_panel, 1)

        card = QFrame()
        card.setObjectName("login_card")
        card.setFixedWidth(690)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(64, 50, 64, 50)

        header = QHBoxLayout()
        header.setSpacing(18)
        header_text = QVBoxLayout()
        header_text.setSpacing(10)
        tag = QLabel("BLOOM FOOD")
        tag.setObjectName("brand_tag")
        header_text.addWidget(tag)
        title = QLabel("Log in to your account")
        title.setObjectName("login_heading")
        header_text.addWidget(title)
        subtitle = QLabel("Welcome back! Please enter your details.")
        subtitle.setObjectName("login_support")
        header_text.addWidget(subtitle)
        header.addLayout(header_text, 1)
        avatar = QLabel()
        avatar.setObjectName("login_avatar")
        avatar_pixmap = QPixmap(self._asset_path("abdelwahab_login.svg"))
        if not avatar_pixmap.isNull():
            avatar.setPixmap(avatar_pixmap.scaled(116, 116, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        avatar.setFixedSize(120, 120)
        avatar.setAlignment(Qt.AlignCenter)
        header.addWidget(avatar, 0, Qt.AlignTop | Qt.AlignRight)
        card_layout.addLayout(header)
        card_layout.addSpacing(38)

        email_label = QLabel("Email")
        email_label.setObjectName("form_label")
        card_layout.addWidget(email_label)
        card_layout.addSpacing(10)
        self.email_input = QLineEdit(self.DEMO_EMAIL)
        self.email_input.setObjectName("login_input")
        self.email_input.setFixedHeight(50)
        card_layout.addWidget(self.email_input)
        card_layout.addSpacing(28)

        password_label = QLabel("Password")
        password_label.setObjectName("form_label")
        card_layout.addWidget(password_label)
        card_layout.addSpacing(10)
        password_row = QFrame()
        password_row.setStyleSheet("QFrame { background: #FFFFFF; border: 1px solid #D0D5DD; border-radius: 8px; }")
        password_layout = QHBoxLayout(password_row)
        password_layout.setContentsMargins(14, 0, 8, 0)
        self.password_input = QLineEdit(self.DEMO_PASSWORD)
        self.password_input.setObjectName("login_input")
        self.password_input.setStyleSheet("QLineEdit#login_input { border: none; padding: 0; }")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.returnPressed.connect(self.login)
        password_layout.addWidget(self.password_input, 1)
        self.password_eye = QToolButton()
        self.password_eye.setObjectName("password_eye")
        self.password_eye.setText("◉")
        self.password_eye.clicked.connect(self._toggle_password)
        password_layout.addWidget(self.password_eye)
        password_row.setFixedHeight(50)
        card_layout.addWidget(password_row)
        card_layout.addSpacing(18)

        options = QHBoxLayout()
        self.remember = QCheckBox("Remember for 30 days")
        self.remember.setObjectName("remember")
        options.addWidget(self.remember)
        options.addStretch(1)
        forgot = QPushButton("Forgot password?")
        forgot.setObjectName("link_button")
        options.addWidget(forgot)
        card_layout.addLayout(options)
        card_layout.addSpacing(28)

        self.login_button = QPushButton("Sign in")
        self.login_button.setObjectName("sign_in")
        self.login_button.setFixedHeight(50)
        self.login_button.clicked.connect(self.login)
        card_layout.addWidget(self.login_button)
        card_layout.addSpacing(18)

        google = QPushButton("G   Sign in with Google")
        google.setObjectName("google_button")
        google.setFixedHeight(50)
        card_layout.addWidget(google)
        card_layout.addSpacing(34)

        footer = QHBoxLayout()
        footer.setAlignment(Qt.AlignCenter)
        footer.setSpacing(6)
        footer.addWidget(QLabel("Don't have an account?"))
        sign_up = QPushButton("Sign up")
        sign_up.setObjectName("link_button")
        footer.addWidget(sign_up)
        card_layout.addLayout(footer)

        root.addWidget(card, 0, Qt.AlignVCenter | Qt.AlignRight)
        self.email_input.setFocus()

    def _toggle_password(self):
        if self.password_input.echoMode() == QLineEdit.Password:
            self.password_input.setEchoMode(QLineEdit.Normal)
            self.password_eye.setText("○")
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
            self.password_eye.setText("◉")

    @staticmethod
    def _asset_path(filename):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_dir, "icons", filename)

    def login(self):
        email = self.email_input.text().strip().lower()
        password = self.password_input.text()
        if email == self.DEMO_EMAIL and password == self.DEMO_PASSWORD:
            self.accept()
            return
        QMessageBox.warning(self, "بيانات الدخول غير صحيحة", "البريد الإلكتروني أو كلمة المرور غير صحيحة.")
        self.password_input.selectAll()
        self.password_input.setFocus()
