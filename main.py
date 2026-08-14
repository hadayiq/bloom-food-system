import sys

from PySide6.QtWidgets import QApplication

from main_window import MainWindow

app = QApplication(sys.argv)


with open("styles/bloom.qss", "r", encoding="utf-8") as file:
    app.setStyleSheet(file.read())


window = MainWindow()

window.show()

sys.exit(app.exec())
