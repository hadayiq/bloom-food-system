import os

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QSplashScreen


class BloomSplashScreen(QSplashScreen):
    """Simple Bloom Food splash screen."""

    def __init__(self, logo_path: str):
        logo = QPixmap(logo_path)

        if logo.isNull():
            raise FileNotFoundError(f"Unable to load splash logo: {logo_path}")

        # Keep the approved vector logo clear and proportionally scaled.
        logo = logo.scaled(
            560,
            230,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        super().__init__(
            logo,
            Qt.WindowType.SplashScreen
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint,
        )

        self.setAttribute(
            Qt.WidgetAttribute.WA_DeleteOnClose,
            False,
        )


def show_splash(app):
    """Show the splash immediately while the application initializes."""

    # splash_screen.py lives directly under <project>/ui/.
    # Two parent levels reach the project root.
    base_dir = os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )

    logo_path = os.path.join(
        base_dir,
        "icons",
        "bloom_logo_splash.svg",
    )

    splash = BloomSplashScreen(logo_path)

    screen = app.primaryScreen()
    if screen:
        geometry = screen.availableGeometry()
        x = geometry.center().x() - splash.width() // 2
        y = geometry.center().y() - splash.height() // 2
        splash.move(x, y)

    splash.show()
    splash.raise_()
    app.processEvents()

    return splash
