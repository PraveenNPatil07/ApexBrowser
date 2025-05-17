import sys
import os
import logging
import platform
from PyQt5.QtWidgets import QApplication, QSplashScreen, QMessageBox
from PyQt5.QtCore import Qt, QTimer, QSettings
from PyQt5.QtGui import QPixmap, QIcon, QPainter, QColor, QFont, QLinearGradient
from PyQt5.QtCore import QT_VERSION_STR
from browser import Browser
from bookmark_manager import BookmarkManager
from history_manager import HistoryManager
from ad_blocker import AdBlocker
from download_manager import DownloadManager
from incognito import IncognitoManager
from ai_assistant import BrowserAssistant
from extension_handler import ExtensionHandler

APP_NAME = "Apex Browser"
VERSION = "1.2.0"
ORGANIZATION = "ApexSoft"
DEFAULT_HOMEPAGE = "https://www.google.com"


def setup_logging():
    os.makedirs("logs", exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("logs/apex_browser.log", encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(APP_NAME)


def check_dependencies():
    """
    Check if all required dependencies are installed and log their versions.
    Returns True if all dependencies are satisfied, False otherwise.
    """
    required_modules = [
        ('PyQt5', '5.15.0'),
        ('platform', None),
        ('logging', None),
    ]

    for module_name, min_version in required_modules:
        try:
            if module_name == 'PyQt5':
                import PyQt5
                # Use QT_VERSION_STR to get the Qt version PyQt5 is built against
                version = QT_VERSION_STR
                logger.info(f"PyQt5 version (Qt): {version}")
            else:
                module = __import__(module_name)
                if hasattr(module, '__version__'):
                    version = module.__version__
                    logger.info(f"{module_name} version: {version}")
                else:
                    logger.info(f"{module_name} is installed (no version info available)")

            if min_version and version < min_version:
                logger.error(f"{module_name} version {version} is too old. Minimum required: {min_version}")
                return False
        except ImportError as e:
            logger.error(f"Missing required module: {module_name} ({e})")
            return False
    return True


def create_directories():
    directories = [
        "data", "downloads", "assets", "logs",
        "extensions", "cache", "profiles"  # Add these
    ]
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
        except OSError as e:
            logging.error(f"Failed to create directory {directory}: {e}")


def create_default_theme_files():
    themes = {
        "dark_theme.qss": """
            QMainWindow, QWidget { background-color: #202124; color: #E0E0E0; }
            QTabWidget::pane { border: none; }
            QTabBar::tab { background-color: #2D2D30; color: #E0E0E0; padding: 6px 12px; }
            QTabBar::tab:selected { background-color: #3C4043; border-bottom: 2px solid #1a73e8; }
            QLineEdit { background-color: #303134; color: #E0E0E0; border: 1px solid #5F6368; padding: 5px; }
            QPushButton { background-color: #1a73e8; color: white; border: none; padding: 5px 10px; }
            QPushButton:hover { background-color: #1557b0; }
        """,
        "light_theme.qss": """
            QMainWindow, QWidget { background-color: #FFFFFF; color: #202124; }
            QTabWidget::pane { border: none; }
            QTabBar::tab { background-color: #F1F3F4; color: #202124; padding: 6px 12px; }
            QTabBar::tab:selected { background-color: #FFFFFF; border-bottom: 2px solid #1a73e8; }
            QLineEdit { background-color: #FFFFFF; color: #202124; border: 1px solid #DADCE0; padding: 5px; }
            QPushButton { background-color: #1a73e8; color: white; border: none; padding: 5px 10px; }
            QPushButton:hover { background-color: #1557b0; }
        """
    }
    for filename, content in themes.items():
        filepath = os.path.join("assets", filename)
        if not os.path.exists(filepath):
            try:
                with open(filepath, "w") as f:
                    f.write(content)
            except IOError as e:
                logging.error(f"Failed to create theme file {filename}: {e}")


def create_splash_screen():
    splash_path = os.path.join("assets", "splash.png")
    if not os.path.exists(splash_path):
        splash_pixmap = QPixmap(600, 400)
        painter = QPainter(splash_pixmap)
        gradient = QLinearGradient(0, 0, 0, 400)
        gradient.setColorAt(0, QColor("#1a73e8"))
        gradient.setColorAt(1, QColor("#4285f4"))
        painter.fillRect(splash_pixmap.rect(), gradient)
        painter.setRenderHint(QPainter.Antialiasing)
        font = QFont("Roboto", 28, QFont.Bold)
        painter.setFont(font)
        painter.setPen(QColor("#FFFFFF"))
        painter.drawText(150, 220, APP_NAME)
        font = QFont("Roboto", 14)
        painter.setFont(font)
        painter.drawText(150, 260, f"Version {VERSION}")
        painter.drawText(150, 290, "Your elite web experience...")
        painter.end()
        try:
            splash_pixmap.save(splash_path)
        except Exception as e:
            logging.warning(f"Couldn't save splash image: {e}")
    else:
        splash_pixmap = QPixmap(splash_path)
    splash = QSplashScreen(splash_pixmap)
    splash.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
    return splash


def initialize_managers():
    return {
        'bookmark_manager': BookmarkManager(),
        'history_manager': HistoryManager(),
        'ad_blocker': AdBlocker(),
        'download_manager': DownloadManager(),
        'incognito_manager': IncognitoManager(),
        'ai_assistant': BrowserAssistant(),
        'extension_handler': ExtensionHandler()
    }


def apply_settings(browser, settings):
    homepage = settings.value("browser/homepage", DEFAULT_HOMEPAGE)
    zoom_factor = float(settings.value("browser/zoom", 1.0))
    theme = settings.value("ui/theme", "light")
    browser.ui.change_theme(theme)
    browser.zoom_factor = zoom_factor


def main():
    # Chromium flags for better rendering
    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = (
        "--enable-gpu-rasterization "
        "--enable-accelerated-2d-canvas "
        "--enable-zero-copy "
        "--disable-gpu-driver-bug-workarounds "
        "--ignore-gpu-blocklist "
        "--enable-native-gpu-memory-buffers "
        "--enable-webgl "
        "--disable-web-security "  # Only for development!
        "--disable-features=CalculateNativeWinOcclusion"
    )
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(VERSION)
    app.setOrganizationName(ORGANIZATION)
    app.setWindowIcon(QIcon(os.path.join("assets", "icon.png")))
    app.setFont(QFont("Roboto", 10))
    # Setup logging before any logging calls
    global logger
    logger = setup_logging()
    logger.info(f"Starting {APP_NAME} v{VERSION} on {platform.system()}")
    if not check_dependencies():
        sys.exit(1)
    create_directories()
    create_default_theme_files()
    splash = create_splash_screen()
    splash.show()
    app.processEvents()
    settings = QSettings(ORGANIZATION, APP_NAME)

    def start_browser():
        try:
            managers = initialize_managers()
            browser = Browser(
                initial_url=settings.value("browser/homepage", DEFAULT_HOMEPAGE),
                initial_zoom=float(settings.value("browser/zoom", 1.0)),
                settings=settings,
                **managers
            )
            apply_settings(browser, settings)
            browser.show()
            if splash:
                splash.finish(browser)
            logger.info("Browser window opened successfully")
        except Exception as e:
            logger.exception("Browser failed to start")
            QMessageBox.critical(None, "Critical Error", str(e))
            sys.exit(1)

    QTimer.singleShot(1500, start_browser)
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
