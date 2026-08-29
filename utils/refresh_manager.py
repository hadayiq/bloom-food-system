import os

from PySide6.QtCore import QObject, Signal, QTimer


class RefreshManager(QObject):
    # خاص بالحركات
    data_changed = Signal()

    # خاص بالأصناف
    products_changed = Signal()

    # خاص بالمخازن الفرعية / مناديب السيارات
    subwarehouse_changed = Signal()

    def __init__(self):
        super().__init__()
        self._inventory_file = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "inventory.xlsx"
        )
        self._last_mtime = self._get_mtime()

        # Excel is the source of truth. Polling is kept for changes made by
        # other code/windows, but repository writes can notify immediately.
        self._watch_timer = QTimer(self)
        self._watch_timer.setInterval(500)
        self._watch_timer.timeout.connect(self._check_inventory_file)
        self._watch_timer.start()

    def _get_mtime(self):
        try:
            return os.path.getmtime(self._inventory_file)
        except OSError:
            return None

    def notify_data_changed(self):
        """Emit immediately after an internal write and suppress the duplicate poll event."""
        self._last_mtime = self._get_mtime()
        self.data_changed.emit()

    def _check_inventory_file(self):
        current_mtime = self._get_mtime()
        if current_mtime is None:
            return
        if self._last_mtime is None:
            self._last_mtime = current_mtime
            return
        if current_mtime != self._last_mtime:
            self._last_mtime = current_mtime
            self.data_changed.emit()


refresh_manager = RefreshManager()
