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

        # Excel is the source of truth for this project. Polling its modification
        # time keeps open windows in sync even when a repository writes directly
        # to the workbook (for example after a count/liquidation).
        self._watch_timer = QTimer(self)
        self._watch_timer.setInterval(350)
        self._watch_timer.timeout.connect(self._check_inventory_file)
        self._watch_timer.start()

    def _get_mtime(self):
        try:
            return os.path.getmtime(self._inventory_file)
        except OSError:
            return None

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
