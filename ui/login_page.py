import os
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFrame, QMessageBox, QCheckBox, QToolButton, QBoxLayout

class LoginWindow(QDialog):
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
            QDialog { background: #FFFFFF; }
            QLabel { background: transparent; border: none; }
            QFrame#brand_panel, QFrame#login_card { background: #FFFFFF; border: none; }
            QLabel#login_heading { color: #101828; border: none; font-size: 30px; font-weight: 600; }
            QLabel#login_support { color: #667085; border: none; font-size: 16px; }
            QLabel#form_label { color: #344054; border: none; font-size: 14px; }
            QLineEdit#login_input { background: #FFFFFF; color: #101828; border: 1px solid #D0D5DD; border-radius: 8px; padding: 0 14px; font-size: 16px; }
            QLineEdit#login_input:focus { border: 1px solid #1366D9; }
            QCheckBox#remember { color: #344054; font-size: 14px; spacing: 8px; }
            QPushButton#link_button { border: none; background: transparent; color: #1366D9; font-size: 14px; padding: 0; }
            QPushButton#sign_in { background: #1769E8; color: #FFFFFF; border: none; border-radius: 6px; font-size: 16px; }
            QPushButton#google_button { background: #FFFFFF; color: #101828; border: 1px solid #D0D5DD; border-radius: 6px; font-size: 16px; }
            QToolButton#password_eye { border: none; background: transparent; color: #667085; font-size: 18px; }
        """)
        root = QHBoxLayout(self)
        root.setContentsMargins(56, 44, 56, 44)
        root.setSpacing(70)
        brand_panel = QFrame(); brand_panel.setObjectName("brand_panel")
        brand_layout = QVBoxLayout(brand_panel); brand_layout.setAlignment(Qt.AlignCenter)
        logo = QLabel(); logo.setAlignment(Qt.AlignCenter)
        logo_pixmap = QPixmap(self._asset_path("bloomfood_logo.png"))
        if logo_pixmap.isNull(): logo_pixmap = QPixmap(self._asset_path("bloom_logo.png"))
        if not logo_pixmap.isNull(): logo.setPixmap(logo_pixmap.scaled(420, 284, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo.setFixedSize(420, 284); brand_layout.addWidget(logo, 0, Qt.AlignCenter); root.addWidget(brand_panel, 1)
        card = QFrame(); card.setObjectName("login_card"); card.setFixedWidth(560)
        card_layout = QVBoxLayout(card); card_layout.setContentsMargins(52, 42, 52, 42)
        title = QLabel("Log in to your account"); title.setObjectName("login_heading"); title.setAlignment(Qt.AlignCenter); card_layout.addWidget(title); card_layout.addSpacing(8)
        subtitle = QLabel("Welcome back! Please enter your details."); subtitle.setObjectName("login_support"); subtitle.setAlignment(Qt.AlignCenter); card_layout.addWidget(subtitle); card_layout.addSpacing(34)
        email_label = QLabel("Email"); email_label.setObjectName("form_label"); card_layout.addWidget(email_label); card_layout.addSpacing(10)
        self.email_input = QLineEdit(self.DEMO_EMAIL); self.email_input.setObjectName("login_input"); self.email_input.setFixedHeight(50); card_layout.addWidget(self.email_input); card_layout.addSpacing(24)
        password_label = QLabel("Password"); password_label.setObjectName("form_label"); card_layout.addWidget(password_label); card_layout.addSpacing(10)
        password_row = QFrame(); password_row.setStyleSheet("QFrame { background: #FFFFFF; border: 1px solid #D0D5DD; border-radius: 8px; }")
        password_layout = QHBoxLayout(password_row); password_layout.setContentsMargins(14, 0, 8, 0)
        self.password_input = QLineEdit(self.DEMO_PASSWORD); self.password_input.setObjectName("login_input"); self.password_input.setStyleSheet("QLineEdit#login_input { border: none; padding: 0; }"); self.password_input.setEchoMode(QLineEdit.Password); self.password_input.returnPressed.connect(self.login); password_layout.addWidget(self.password_input, 1)
        self.password_eye = QToolButton(); self.password_eye.setObjectName("password_eye"); self.password_eye.setText("◉"); self.password_eye.clicked.connect(self._toggle_password); password_layout.addWidget(self.password_eye); password_row.setFixedHeight(50); card_layout.addWidget(password_row); card_layout.addSpacing(18)
        options = QHBoxLayout(); self.remember = QCheckBox("Remember for 30 days"); self.remember.setObjectName("remember"); options.addWidget(self.remember); options.addStretch(1); forgot = QPushButton("Forgot password?"); forgot.setObjectName("link_button"); options.addWidget(forgot); card_layout.addLayout(options); card_layout.addSpacing(28)
        self.login_button = QPushButton("Sign in"); self.login_button.setObjectName("sign_in"); self.login_button.setFixedHeight(50); self.login_button.clicked.connect(self.login); card_layout.addWidget(self.login_button); card_layout.addSpacing(18)
        google = QPushButton("Sign in with Google"); google.setObjectName("google_button"); google.setFixedHeight(50); card_layout.addWidget(google); card_layout.addSpacing(30)
        footer = QHBoxLayout(); footer.setAlignment(Qt.AlignCenter); footer.setSpacing(6); footer.addWidget(QLabel("Don't have an account?")); sign_up = QPushButton("Sign up"); sign_up.setObjectName("link_button"); footer.addWidget(sign_up); card_layout.addLayout(footer)
        root.addWidget(card, 0, Qt.AlignVCenter | Qt.AlignRight); self.email_input.setFocus()

    def _toggle_password(self):
        if self.password_input.echoMode() == QLineEdit.Password: self.password_input.setEchoMode(QLineEdit.Normal); self.password_eye.setText("○")
        else: self.password_input.setEchoMode(QLineEdit.Password); self.password_eye.setText("◉")

    @staticmethod
    def _asset_path(filename): return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "icons", filename)

    def login(self):
        if self.email_input.text().strip().lower() == self.DEMO_EMAIL and self.password_input.text() == self.DEMO_PASSWORD: self.accept(); return
        QMessageBox.warning(self, "بيانات الدخول غير صحيحة", "البريد الإلكتروني أو كلمة المرور غير صحيحة.")
        self.password_input.selectAll(); self.password_input.setFocus()
