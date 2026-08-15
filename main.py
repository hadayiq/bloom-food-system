import sys

from PySide6.QtWidgets import QApplication

from main_window import MainWindow

app = QApplication(sys.argv)


with open("styles/bloom.qss", "r", encoding="utf-8") as file:
    base_styles = file.read()

with open("styles/ui_v1.qss", "r", encoding="utf-8") as file:
    ui_v1_styles = file.read()

app.setStyleSheet(base_styles + "\n\n" + ui_v1_styles)


window = MainWindow()

window.show()

sys.exit(app.exec())
