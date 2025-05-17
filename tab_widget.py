from PyQt5.QtWidgets import QTabWidget
from PyQt5.QtCore import pyqtSignal

class TabWidget(QTabWidget):
    tab_count_changed = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self.close_tab)

    def close_tab(self, index):
        """Close the tab at the given index"""
        if self.count() > 1:
            self.removeTab(index)
            self.tab_count_changed.emit(self.count())
