import os

from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QPainter, QPixmap
from PySide6.QtWidgets import QSplashScreen


class BloomSplashScreen(QSplashScreen):
    """Minimal branded splash screen shown before the main window."""

    def __init__(self, logo_path: str):
        super().__init__(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)

        logo = QPixmap(logo_path)
        canvas = QPixmap(1250, 750)
        canvas.fill(Qt.GlobalColor.white)

        scaled_logo = logo.scaled(
            500,
            180,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        x = (canvas.width() - scaled_logo.width()) // 2
        y = (canvas.height() - scaled_logo.height()) // 2

        painter = QPainter(canvas)
        painter.drawPixmap(x, y, scaled_logo)
        painter.end()

        self.setPixmap(canvas)


def show_splash(app, on_finished, duration_ms: int = 900):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    logo_path = os.path.join(base_dir, "icons", "bloom_logo_light.svg")

    splash = BloomSplashScreen(logo_path)
    splash.show()
    app.processEvents()

    def finish():
        splash.close()
        on_finished()

    QTimer.singleShot(duration_ms, finish)
    return splash
