import os

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFrame,
    QMessageBox,
    QCheckBox,
    QSizePolicy,
)


class LoginWindow(QDialog):
    """Bloom Food login screen based on the Figma Kit login layout."""

    DEMO_EMAIL = "abdelwahabrefat@bloomfood.com"
    DEMO_PASSWORD = "1041999"
    DISPLAY_NAME = "عبدالوهاب"

    def __init__(self):
        super().__init__()
        self.user_name = self.DISPLAY_NAME
        self.setWindowTitle("Bloom Food - تسجيل الدخول")
        self.setMinimumSize(1050, 680)
        self.resize(1200, 800)
        self.setModal(True)
        self._build_ui()

    def _build_ui(self):
        # The Figma reference is a clean two-column login: brand on the left,
        # 360px form on the right, with generous white space and no card.
        self.setStyleSheet(
            """
            QDialog {
                background: #FFFFFF;
            }
            QLabel {
                background: transparent;
            }
            QLabel#login_heading {
                color: #2B2F38;
                font-family: Inter, 'Segoe UI';
                font-size: 30px;
                font-weight: 600;
            }
            QLabel#login_support {
                color: #667085;
                font-family: Inter, 'Segoe UI';
                font-size: 16px;
                font-weight: 400;
            }
            QLabel#form_label {
                color: #48505E;
                font-family: Inter, 'Segoe UI';
                font-size: 14px;
                font-weight: 500;
            }
            QLineEdit#login_input {
                background: #FFFFFF;
                color: #383E49;
                border: 1px solid #D0D5DD;
                border-radius: 8px;
                padding: 10px 14px;
                min-height: 24px;
                font-family: Inter, 'Segoe UI';
                font-size: 16px;
                font-weight: 400;
                selection-background-color: #1366D9;
            }
            QLineEdit#login_input:focus {
                border: 1px solid #1366D9;
            }
            QCheckBox#remember {
                color: #48505E;
                font-family: Inter, 'Segoe UI';
                font-size: 14px;
                font-weight: 500;
                spacing: 8px;
            }
            QCheckBox#remember::indicator {
                width: 16px;
                height: 16px;
                border: 1px solid #D0D5DD;
                border-radius: 4px;
                background: #FFFFFF;
            }
            QCheckBox#remember::indicator:checked {
                background: #1366D9;
                border: 1px solid #1366D9;
            }
            QPushButton#text_button {
                border: none;
                background: transparent;
                color: #1366D9;
                font-family: Inter, 'Segoe UI';
                font-size: 14px;
                font-weight: 500;
                padding: 0;
            }
            QPushButton#sign_in {
                background: #1366D9;
                color: #FFFFFF;
                border: 1px solid #1366D9;
                border-radius: 4px;
                padding: 10px 18px;
                min-height: 24px;
                font-family: Inter, 'Segoe UI';
                font-size: 16px;
                font-weight: 500;
            }
            QPushButton#sign_in:hover {
                background: #0F5BC2;
                border-color: #0F5BC2;
            }
            QPushButton#google_button {
                background: #FFFFFF;
                color: #383E49;
                border: 1px solid #D0D5DD;
                border-radius: 4px;
                padding: 10px 16px;
                min-height: 24px;
                font-family: Inter, 'Segoe UI';
                font-size: 16px;
                font-weight: 500;
            }
            QPushButton#google_button:hover {
                background: #F8F9FB;
            }
            QLabel#footer_text {
                color: #667085;
                font-family: Inter, 'Segoe UI';
                font-size: 14px;
                font-weight: 400;
            }
            QLabel#brand_name {
                color: #55A936;
                font-family: Inter, 'Segoe UI';
                font-size: 24px;
                font-weight: 600;
            }
            """
        )

        root = QHBoxLayout(self)
        root.setContentsMargins(70, 50, 70, 50)
        root.setSpacing(120)
        root.setDirection(QBoxLayout.LeftToRight if False else QBoxLayout.LeftToRight)

        # Left branding area. Keep the official Bloom Food logo and the user's
        # supplied profile image already stored in the repository.
        brand = QVBoxLayout()
        brand.setAlignment(Qt.AlignCenter)
        brand.setSpacing(18)
        brand.setContentsMargins(0, 0, 0, 0)

        logo_path = self._asset_path("bloom_logo_splash.svg")
        logo = QLabel()
        logo_pixmap = QPixmap(logo_path)
        if not logo_pixmap.isNull():
            logo.setPixmap(logo_pixmap.scaled(360, 142, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo.setFixedSize(360, 142)
        logo.setAlignment(Qt.AlignCenter)
        brand.addWidget(logo)

        avatar_path = self._asset_path("abdelwahab_avatar.png")
        avatar = QLabel()
        avatar.setObjectName("login_avatar")
        avatar_pixmap = QPixmap(avatar_path)
        if not avatar_pixmap.isNull():
            avatar.setPixmap(avatar_pixmap.scaled(132, 132, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
        avatar.setFixedSize(132, 132)
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setStyleSheet(
            "QLabel#login_avatar { border: 4px solid #F2F4F7; border-radius: 70px; background: #FFFFFF; }"
        )
        brand.addWidget(avatar, alignment=Qt.AlignCenter)

        name = QLabel("عبدالوهاب رفعت")
        name.setObjectName("brand_name")
        name.setAlignment(Qt.AlignCenter)
        brand.addWidget(name)
        brand.addStretch(1)

        # Right content area follows the Figma Kit's 360px content width.
        content = QVBoxLayout()
        content.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        content.setSpacing(0)
        content.setContentsMargins(0, 85, 0, 0)

        header = QVBoxLayout()
        header.setAlignment(Qt.AlignCenter)
        header.setSpacing(12)

        mark = QLabel("◆")
        mark.setAlignment(Qt.AlignCenter)
        mark.setStyleSheet(
            "QLabel { color: #1366D9; font-size: 20px; font-weight: 600; min-height: 48px; }"
        )
        header.addWidget(mark)

        title = QLabel("Log in to your account")
        title.setObjectName("login_heading")
        title.setAlignment(Qt.AlignCenter)
        header.addWidget(title)

        subtitle = QLabel("Welcome back! Please enter your details.")
        subtitle.setObjectName("login_support")
        subtitle.setAlignment(Qt.AlignCenter)
        header.addWidget(subtitle)
        content.addLayout(header)
        content.addSpacing(24)

        form = QVBoxLayout()
        form.setSpacing(20)
        form.setContentsMargins(0, 0, 0, 0)

        email_label = QLabel("Email")
        email_label.setObjectName("form_label")
        form.addWidget(email_label)

        self.email_input = QLineEdit()
        self.email_input.setObjectName("login_input")
        self.email_input.setPlaceholderText("Enter your email")
        self.email_input.setText(self.DEMO_EMAIL)
        self.email_input.setClearButtonEnabled(True)
        self.email_input.setFixedHeight(46)
        form.addWidget(self.email_input)

        password_label = QLabel("Password")
        password_label.setObjectName("form_label")
        form.addWidget(password_label)

        self.password_input = QLineEdit()
        self.password_input.setObjectName("login_input")
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setText(self.DEMO_PASSWORD)
        self.password_input.setFixedHeight(46)
        self.password_input.returnPressed.connect(self.login)
        form.addWidget(self.password_input)

        options = QHBoxLayout()
        options.setContentsMargins(0, 0, 0, 0)
        options.setSpacing(8)

        self.remember = QCheckBox("Remember for 30 days")
        self.remember.setObjectName("remember")
        options.addWidget(self.remember)
        options.addStretch(1)

        forgot = QPushButton("Forgot password")
        forgot.setObjectName("text_button")
        forgot.setCursor(Qt.PointingHandCursor)
        options.addWidget(forgot)
        form.addLayout(options)
        form.addSpacing(4)

        self.login_button = QPushButton("Sign in")
        self.login_button.setObjectName("sign_in")
        self.login_button.setCursor(Qt.PointingHandCursor)
        self.login_button.setFixedHeight(46)
        self.login_button.clicked.connect(self.login)
        form.addWidget(self.login_button)

        google = QPushButton("🌐   Sign in with Google")
        google.setObjectName("google_button")
        google.setCursor(Qt.PointingHandCursor)
        google.setFixedHeight(46)
        # Google authentication is intentionally visual-only for this demo.
        form.addWidget(google)

        content.addLayout(form)
        content.addSpacing(28)

        footer = QHBoxLayout()
        footer.setAlignment(Qt.AlignCenter)
        footer.setSpacing(4)
        footer_text = QLabel("Don't have an account?")
        footer_text.setObjectName("footer_text")
        footer.addWidget(footer_text)
        sign_up = QPushButton("Sign up")
        sign_up.setObjectName("text_button")
        sign_up.setCursor(Qt.PointingHandCursor)
        footer.addWidget(sign_up)
        content.addLayout(footer)

        root.addLayout(brand, 1)
        content_frame = QFrame()
        content_frame.setLayout(content)
        content_frame.setFixedWidth(360)
        root.addWidget(content_frame, 0, Qt.AlignTop | Qt.AlignRight)

        self.email_input.setFocus()

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

        QMessageBox.warning(
            self,
            "بيانات الدخول غير صحيحة",
            "البريد الإلكتروني أو كلمة المرور غير صحيحة.",
        )
        self.password_input.selectAll()
        self.password_input.setFocus()
