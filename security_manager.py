from PyQt5.QtCore import QObject

class SecurityManager(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)

    def check_url_safety(self, url):
        """Check if the URL is safe (placeholder)"""
        if not url:
            return False
        return url.startswith("https://")

    def block_malicious_content(self, content):
        """Block malicious content (placeholder)"""
        malicious_keywords = ["malware", "phishing", "exploit"]
        if not content:
            return False
        return any(keyword in content.lower() for keyword in malicious_keywords)
