import os
import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication, QMessageBox

from main_window import MainWindow
from ui.login_page import LoginWindow
from ui.splash_screen import show_splash


app = QApplication(sys.argv)

# UI Kit foundation: consistent rendering and Arabic-first layout.
app.setStyle("Fusion")
app.setLayoutDirection(Qt.RightToLeft)
app.setFont(QFont("Segoe UI", 10))

base_dir = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(base_dir, "styles/bloom.qss"), "r", encoding="utf-8") as file:
    base_styles = file.read()

with open(os.path.join(base_dir, "styles/ui_v1.qss"), "r", encoding="utf-8") as file:
    ui_v1_styles = file.read()

with open(os.path.join(base_dir, "styles/ui_v2_components.qss"), "r", encoding="utf-8") as file:
    ui_v2_component_styles = file.read()

with open(os.path.join(base_dir, "styles/modern_inputs.qss"), "r", encoding="utf-8") as file:
    modern_input_styles = file.read()

app.setStyleSheet(
    base_styles
    + "\n\n"
    + ui_v1_styles
    + "\n\n"
    + ui_v2_component_styles
    + "\n\n"
    + modern_input_styles
    + "\n\n"
    + "QFrame#login_card { background: #FFFFFF; border: 1px solid #DCE6DE; border-radius: 18px; }\n"
    + "QLabel#login_title { color: #2F6338; font-size: 23pt; font-weight: 800; }\n"
    + "QLabel#login_subtitle { color: #7B877F; font-size: 10.5pt; }\n"
    + "QLabel#login_tagline { color: #4B9A4A; font-size: 15pt; font-weight: 700; }\n"
    + "QLabel#login_name { color: #25332A; font-size: 14pt; font-weight: 700; }\n"
    + "QLabel#login_hint { color: #89958D; font-size: 9pt; }\n"
    + "QLabel#login_avatar { border: 4px solid #E7F3E7; border-radius: 75px; background: #FFFFFF; }\n"
)


# Show the splash first, then require authentication before opening the system.
splash = show_splash(app)

login = LoginWindow()
login.show()
login.raise_()
login.activateWindow()
app.processEvents()

if login.exec() != LoginWindow.Accepted:
    splash.close()
    sys.exit(0)

try:
    window = MainWindow()
    window.show()
    app.processEvents()
    splash.finish(window)
    QMessageBox.information(window, "مرحبًا", "أهلاً بك عبدالوهاب 👋")
except Exception:
    splash.close()
    raise

sys.exit(app.exec())
