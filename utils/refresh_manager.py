from PySide6.QtCore import QObject, Signal


class RefreshManager(QObject):

    # خاص بالحركات
    data_changed = Signal()

    # خاص بالأصناف
    products_changed = Signal()


refresh_manager = RefreshManager()
