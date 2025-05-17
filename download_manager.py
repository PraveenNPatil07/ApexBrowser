import os
import json
from datetime import datetime
from PyQt5.QtCore import QObject, pyqtSignal, QUrl
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest

class DownloadManager(QObject):
    download_progress = pyqtSignal(int, int, str)  # bytes_received, bytes_total, filename
    download_finished = pyqtSignal(str, bool)     # filepath, success

    def __init__(self, parent=None):
        super().__init__(parent)
        self.network_manager = QNetworkAccessManager()
        self.downloads = []
        self._load_downloads()
        self.current_download = None

    def _load_downloads(self):
        """Load download history from file"""
        downloads_file = "data/downloads.json"
        if os.path.exists(downloads_file):
            try:
                with open(downloads_file, 'r') as f:
                    self.downloads = json.load(f)
            except Exception as e:
                print(f"Error loading downloads: {e}")
                self.downloads = []

    def _save_downloads(self):
        """Save download history to file"""
        downloads_file = "data/downloads.json"
        try:
            with open(downloads_file, 'w') as f:
                json.dump(self.downloads, f, indent=4)
        except Exception as e:
            print(f"Error saving downloads: {e}")

    def start_download(self, url, custom_path=None):
        """Start a new download"""
        if not url:
            return

        filename = url.split('/')[-1] or "download"
        download_path = custom_path or os.path.join("downloads", filename)

        counter = 1
        base_name = os.path.splitext(download_path)[0]
        extension = os.path.splitext(download_path)[1]
        while os.path.exists(download_path):
            download_path = f"{base_name}_{counter}{extension}"
            counter += 1

        request = QNetworkRequest(QUrl(url))
        reply = self.network_manager.get(request)
        self.current_download = {
            'reply': reply,
            'file': open(download_path, 'wb'),
            'url': url,
            'path': download_path,
            'start_time': datetime.now().isoformat()
        }

        reply.downloadProgress.connect(lambda received, total: self.download_progress.emit(received, total, filename))
        reply.finished.connect(lambda: self._handle_download_finished(download_path))

    def _handle_download_finished(self, filepath):
        """Handle download completion"""
        if not self.current_download:
            return

        reply = self.current_download['reply']
        file = self.current_download['file']
        success = not reply.error()

        if success:
            data = reply.readAll()
            file.write(data)
            self.downloads.append({
                'url': self.current_download['url'],
                'path': filepath,
                'date': datetime.now().isoformat(),
                'size': os.path.getsize(filepath)
            })
            self._save_downloads()
        else:
            print(f"Download failed: {reply.errorString()}")

        file.close()
        reply.deleteLater()
        self.download_finished.emit(filepath, success)
        self.current_download = None

    def get_download_history(self):
        """Return the download history"""
        return self.downloads

    def clear_download_history(self):
        """Clear the download history"""
        self.downloads = []
        self._save_downloads()

    def cancel_download(self):
        """Cancel the current download"""
        if self.current_download:
            self.current_download['reply'].abort()
            self.current_download['file'].close()
            if os.path.exists(self.current_download['path']):
                os.remove(self.current_download['path'])
            self.current_download = None
