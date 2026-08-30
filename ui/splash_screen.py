import os

from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QPixmap
from PySide6.QtWidgets import QSplashScreen


class BloomSplashScreen(QSplashScreen):
    """Minimal branded splash shown while the application initializes."""

    def __init__(self, logo_path: str):
        logo = QPixmap(logo_path)
        if logo.isNull():
            raise FileNotFoundError(f"Unable to load splash logo: {logo_path}")

        scaled_logo = logo.scaled(
            360,
            120,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        canvas = QPixmap(520, 260)
        canvas.fill(Qt.GlobalColor.white)

        painter = QPainter(canvas)
        x = (canvas.width() - scaled_logo.width()) // 2
        y = (canvas.height() - scaled_logo.height()) // 2
        painter.drawPixmap(x, y, scaled_logo)
        painter.end()

        super().__init__(
            canvas,
            Qt.WindowType.SplashScreen
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint,
        )
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, False)


def show_splash(app):
    """Show the splash immediately; the caller closes it when initialization is ready."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    logo_path = os.path.join(base_dir, "icons", "bloom_logo_light.svg")

    splash = BloomSplashScreen(logo_path)
    splash.show()
    splash.raise_()
    splash.activateWindow()
    app.processEvents()
    return splash
