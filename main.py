import os
import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication, QMessageBox

from main_window import MainWindow
from ui.login_page import LoginWindow
from ui.splash_screen import show_splash


app = QApplication(sys.argv)
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

app.setStyleSheet(base_styles + "\n\n" + ui_v1_styles + "\n\n" + ui_v2_component_styles + "\n\n" + modern_input_styles)

# Startup flow: Splash -> Login -> Main Window.
splash = show_splash(app)
app.processEvents()

# The splash must not remain above the login dialog.
splash.close()
app.processEvents()

login = LoginWindow()
if login.exec() != LoginWindow.Accepted:
    sys.exit(0)

try:
    window = MainWindow()
    window.show()
    app.processEvents()
    QMessageBox.information(window, "مرحبًا", "أهلاً بك عبدالوهاب 👋")
except Exception:
    raise

sys.exit(app.exec())
