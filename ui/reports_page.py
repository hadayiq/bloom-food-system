from PySide6.QtWidgets import QWidget,QVBoxLayout,QLabel


class ReportsPage(QWidget):

    def __init__(self):

        super().__init__()

        layout = QVBoxLayout()

        layout.addWidget(
            QLabel("التقارير")
        )

        self.setLayout(layout)