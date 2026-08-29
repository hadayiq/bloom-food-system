import base64

from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QPainter, QPixmap
from PySide6.QtWidgets import QSplashScreen


# Official Bloom Food logo supplied for the application splash screen.
_LOGO_B64 = ""  # populated by the implementation commit


class BloomSplashScreen(QSplashScreen):
    """Minimal branded splash screen shown before the main window."""

    def __init__(self, logo_data: bytes):
        super().__init__(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)

        logo = QPixmap()
        logo.loadFromData(logo_data, "JPEG")

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


def show_splash(app, logo_data: bytes, on_finished, duration_ms: int = 900):
    splash = BloomSplashScreen(logo_data)
    splash.show()
    app.processEvents()

    def finish():
        splash.close()
        on_finished()

    QTimer.singleShot(duration_ms, finish)
    return splash
