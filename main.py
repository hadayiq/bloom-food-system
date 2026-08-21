import os
import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QLineEdit

from main_window import MainWindow


def apply_reference_input_icons(root):
    """Apply the reference-sheet input icons without changing business logic."""
    icon_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icons")
    rules = [
        ("search", ("بحث", "search"), "input_search.svg"),
        ("user", ("عميل", "مندوب", "اسم العميل", "اسم المندوب"), "input_user.svg"),
        ("product", ("اسم الصنف", "الصنف"), "input_box.svg"),
    ]

    for edit in root.findChildren(QLineEdit):
        if edit.property("bloom_input_icon_applied"):
            continue

        text = f"{edit.objectName()} {edit.placeholderText()}".strip().lower()
        icon_name = None
        for _, keywords, filename in rules:
            if any(keyword.lower() in text for keyword in keywords):
                icon_name = filename
                break

        if icon_name:
            icon_path = os.path.join(icon_dir, icon_name)
            if os.path.exists(icon_path):
                # In the Arabic RTL layout, LeadingPosition places the icon on the right.
                edit.addAction(QIcon(icon_path), QLineEdit.LeadingPosition)
                edit.setProperty("bloom_input_icon_applied", True)


app = QApplication(sys.argv)


with open("styles/bloom.qss", "r", encoding="utf-8") as file:
    base_styles = file.read()

with open("styles/ui_v1.qss", "r", encoding="utf-8") as file:
    ui_v1_styles = file.read()

with open("styles/ui_v2_components.qss", "r", encoding="utf-8") as file:
    ui_v2_component_styles = file.read()

with open("styles/modern_inputs.qss", "r", encoding="utf-8") as file:
    modern_input_styles = file.read()

app.setStyleSheet(
    base_styles
    + "\n\n"
    + ui_v1_styles
    + "\n\n"
    + ui_v2_component_styles
    + "\n\n"
    + modern_input_styles
)


window = MainWindow()
apply_reference_input_icons(window)

window.show()

sys.exit(app.exec())
