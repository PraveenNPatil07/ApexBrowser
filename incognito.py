from PyQt5.QtCore import QObject


class IncognitoManager(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_incognito = False

    def toggle_incognito(self):
        """Toggle incognito mode"""
        self._is_incognito = not self._is_incognito
        return self._is_incognito

    def is_incognito(self):
        """Check if incognito mode is active"""
        return self._is_incognito

    def clear_incognito_data(self):
        """Clear data associated with incognito mode (placeholder)"""
        pass
