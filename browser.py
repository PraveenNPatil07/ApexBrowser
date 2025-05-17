from PyQt5.QtWidgets import (QMainWindow, QTabWidget, QShortcut, QAction, QMenu,
                             QVBoxLayout, QWidget, QApplication, QPushButton,
                             QTabBar, QStatusBar, QLabel, QFrame, QHBoxLayout, QFileDialog, QSizePolicy)
from PyQt5.QtCore import QUrl, Qt, pyqtSignal, QSettings, QPropertyAnimation, QEasingCurve, QPoint, QSize, QTimer
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile, QWebEnginePage, QWebEngineSettings
from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor
from PyQt5.QtGui import QKeySequence, QIcon, QPainter, QFont, QCursor
from ui import BrowserUI
from voice_search import voice_search
from security_manager import SecurityManager
import platform
import logging
try:
    import psutil
except ImportError:
    psutil = None

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('Apex Browser')

class TitleBar(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setObjectName("titleBar")
        self.setFixedHeight(30)
        self.setStyleSheet("""
            QFrame#titleBar {
                background: #f1f3f4;
                border-bottom: 1px solid #dadce0;
            }
        """)
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(8, 0, 8, 0)
        self.layout.setSpacing(4)

        # Window title (only "APEX" in top-left, stylish font, matching color)
        self.title_label = QLabel("APEX")
        self.title_label.setFont(QFont("Montserrat", 14, QFont.Bold))
        self.title_label.setStyleSheet("color: #1a73e8;")

        # Window control buttons
        self.is_maximized = False
        button_style = """
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 8px;
                min-width: 16px;
                min-height: 16px;
                max-width: 16px;
                max-height: 16px;
                color: #202124;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #e8eaed;
            }
        """

        self.close_btn = QPushButton("×")
        self.close_btn.setStyleSheet(f"""
            {button_style}
            QPushButton:hover {{ background-color: #ff605c; }}
        """)
        self.close_btn.clicked.connect(self.parent.close)
        self.close_btn.setFont(QFont("Roboto", 10))

        self.minimize_btn = QPushButton("−")
        self.minimize_btn.setStyleSheet(button_style)
        self.minimize_btn.clicked.connect(self.parent.showMinimized)
        self.minimize_btn.setFont(QFont("Roboto", 10))

        self.maximize_btn = QPushButton("□")
        self.maximize_btn.setStyleSheet(button_style)
        self.maximize_btn.clicked.connect(self.toggle_maximize)
        self.maximize_btn.setFont(QFont("Roboto", 10))

        # Layout: "APEX" on the left, buttons on the right
        self.layout.addWidget(self.title_label)
        self.layout.addStretch()
        self.layout.addWidget(self.minimize_btn)
        self.layout.addWidget(self.maximize_btn)
        self.layout.addWidget(self.close_btn)

        self.setLayout(self.layout)
        self.drag_position = None

    def toggle_maximize(self):
        if self.is_maximized:
            self.parent.showNormal()
            self.maximize_btn.setText("□")
        else:
            self.parent.showMaximized()
            self.maximize_btn.setText("❐")
        self.is_maximized = not self.is_maximized

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and not self.is_maximized:
            self.drag_position = event.globalPos() - self.parent.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.drag_position is not None:
            self.parent.move(event.globalPos() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.drag_position = None

class CustomTabBar(QTabBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QTabBar {
                background: #f1f3f4;
                border-bottom: 1px solid #dadce0;
                padding: 2px;
            }
            QTabBar::tab {
                background: #f1f3f4;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                min-width: 100px;
                max-width: 200px;
                margin-right: 2px;
                font-family: Roboto, Arial, sans-serif;
                font-size: 13px;
                color: #202124;
            }
            QTabBar::tab:selected {
                background: #ffffff;
                border-bottom: 2px solid #1a73e8;
                color: #202124;
            }
            QTabBar::tab:hover {
                background: #e8eaed;
            }
            QTabBar::close-button {
                image: url(assets/close_tab.png);
                subcontrol-position: right;
                width: 16px;
                height: 16px;
            }
        """)
        self.new_tab_btn = QPushButton("+")
        self.new_tab_btn.setFixedSize(28, 28)
        self.new_tab_btn.setStyleSheet("""
            QPushButton {
                background-color: #f1f3f4;
                color: #5f6368;
                border: none;
                border-radius: 4px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e8eaed;
            }
            QPushButton:pressed {
                background-color: #dadce0;
            }
        """)
        self.setUsesScrollButtons(True)
        self.setElideMode(Qt.ElideRight)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.count() > 0:
            last_tab_rect = self.tabRect(self.count() - 1)
            btn_x = last_tab_rect.right() + 4
            btn_y = last_tab_rect.y() + (last_tab_rect.height() - self.new_tab_btn.height()) // 2
            self.new_tab_btn.move(btn_x, btn_y)
        else:
            self.new_tab_btn.move(4, 4)

class WebView(QWebEngineView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_browser = parent
        self.security_manager = SecurityManager()
        self.debug_webgl = QSettings("ApexSoft", "Apex Browser").value("debug/webgl", False, type=bool)
        self.hardware_acceleration = QSettings("ApexSoft", "Apex Browser").value("rendering/hardware_acceleration",
                                                                                 True, type=bool)
        self.webgl_error_reported = False
        self.setup_context_menu()
        self.setup_webgl_monitor()
        settings = self.settings()
        settings.setAttribute(QWebEngineSettings.Accelerated2dCanvasEnabled, self.hardware_acceleration)
        settings.setAttribute(QWebEngineSettings.WebGLEnabled, self.hardware_acceleration and self.debug_webgl)
        settings.setAttribute(QWebEngineSettings.PluginsEnabled, True)
        settings.setAttribute(QWebEngineSettings.FullScreenSupportEnabled, True)
        settings.setAttribute(QWebEngineSettings.ScreenCaptureEnabled, True)
        settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.JavascriptCanOpenWindows, True)
        settings.setAttribute(QWebEngineSettings.LocalStorageEnabled, True)
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.WebRTCPublicInterfacesOnly, True)
        settings.setAttribute(QWebEngineSettings.ScrollAnimatorEnabled, True)
        settings.setFontFamily(QWebEngineSettings.StandardFont, "Roboto")
        settings.setFontSize(QWebEngineSettings.DefaultFontSize, 16)
        settings.setAttribute(QWebEngineSettings.PlaybackRequiresUserGesture, False)
        settings.setAttribute(QWebEngineSettings.JavascriptCanAccessClipboard, True)

        # Enable these essential settings
        settings.setAttribute(QWebEngineSettings.Accelerated2dCanvasEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebGLEnabled, True)
        settings.setAttribute(QWebEngineSettings.PluginsEnabled, True)
        settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.LocalStorageEnabled, True)
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)

        # Add these new settings for better compatibility
        settings.setAttribute(QWebEngineSettings.AllowRunningInsecureContent, True)
        settings.setAttribute(QWebEngineSettings.AllowWindowActivationFromJavaScript, True)
        settings.setAttribute(QWebEngineSettings.ShowScrollBars, True)

        # Set default font settings
        settings.setFontFamily(QWebEngineSettings.StandardFont, "Arial")
        settings.setFontSize(QWebEngineSettings.DefaultFontSize, 16)

        self.page().javaScriptConsoleMessage = self.handle_js_console_message
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # Set a modern user agent string
        self.profile = QWebEngineProfile.defaultProfile()
        self.profile.setHttpUserAgent(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 "
            "Safari/537.36"
        )

    def sizeHint(self):
        return QSize(800, 600)

    def handle_js_console_message(self, level, msg, line, source):
        logger.info(f"JS Console: {msg} (line {line}, {source})")
        if "WebGL" in msg or "GL_INVALID" in msg:
            self.handle_webgl_error(msg)

    def setup_webgl_monitor(self):
        js_code = """
        (function() {
            const canvas = document.createElement('canvas');
            const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
            if (gl) {
                console.log('WebGL context created. Version: ' + gl.getParameter(gl.VERSION));
                const fb = gl.createFramebuffer();
                gl.bindFramebuffer(gl.FRAMEBUFFER, fb);
                const rb = gl.createRenderbuffer();
                gl.bindRenderbuffer(gl.RENDERBUFFER, rb);
                gl.renderbufferStorage(gl.RENDERBUFFER, gl.RGBA4, 256, 256);
                gl.framebufferRenderbuffer(gl.FRAMEBUFFER, gl.COLOR_ATTACHMENT0, gl.RENDERBUFFER, rb);
                const status = gl.checkFramebufferStatus(gl.FRAMEBUFFER);
                if (status !== gl.FRAMEBUFFER_COMPLETE) {
                    console.error('Framebuffer incomplete: ' + status);
                } else {
                    console.log('Framebuffer is complete');
                }
                gl.bindRenderbuffer(gl.RENDERBUFFER, null);
                gl.bindFramebuffer(gl.FRAMEBUFFER, null);
            } else {
                console.error('WebGL not supported');
            }
        })();
        """
        self.page().runJavaScript(js_code, lambda result: logger.info(f"WebGL Monitor: {result}"))

    def handle_webgl_error(self, error_msg):
        if not self.webgl_error_reported:
            logger.error(f"WebGL Error: {error_msg}")
            self.parent_browser.ui.show_notification("WebGL rendering failed. Falling back to software rendering.",
                                                     5000)
            if self.hardware_acceleration:
                QSettings("ApexSoft", "Apex Browser").setValue("rendering/hardware_acceleration", False)
                self.settings().setAttribute(QWebEngineSettings.WebGLEnabled, False)
                self.settings().setAttribute(QWebEngineSettings.Accelerated2dCanvasEnabled, False)
                logger.info("Disabled hardware acceleration due to WebGL error")
            self.webgl_error_reported = True

    def setup_context_menu(self):
        self.custom_context_menu = QMenu(self)
        actions = [
            ("New Tab", lambda: self.parent_browser.add_new_tab()),
            ("New Window", lambda: self.parent_browser.open_new_window()),
            ("Open Link in New Tab", self.open_link_new_tab),
            ("Copy Link Address", self.copy_link),
            ("Save As...", self.save_page),
            ("Reload", self.reload),
            ("Back", self.back),
            ("Forward", self.forward),
            ("Inspect Element", self.inspect_element),
        ]
        for label, callback in actions:
            action = QAction(label, self)
            action.triggered.connect(callback)
            self.custom_context_menu.addAction(action)

    def open_link_new_tab(self):
        url = self.page().contextMenuData().linkUrl()
        if url.isValid():
            self.parent_browser.add_new_tab(url.toString())

    def copy_link(self):
        url = self.page().contextMenuData().linkUrl()
        if url.isValid():
            QApplication.clipboard().setText(url.toString())

    def save_page(self):
        file_dialog = QFileDialog(self)
        file_dialog.setAcceptMode(QFileDialog.AcceptSave)
        file_dialog.setNameFilter("Web Pages (*.html);;All Files (*)")
        if file_dialog.exec_():
            file_path = file_dialog.selectedFiles()[0]
            self.page().save(file_path, QWebEnginePage.CompleteHtml)

    def inspect_element(self):
        self.page().triggerAction(QWebEnginePage.InspectElement)

    def contextMenuEvent(self, event):
        self.custom_context_menu.exec_(event.globalPos())

    def paintEvent(self, event):
        try:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing, True)
            painter.setRenderHint(QPainter.TextAntialiasing, True)
            painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
            super().paintEvent(event)
        except Exception as e:
            logger.error(f"Paint event error: {e}")
            self.parent_browser.ui.show_notification("Rendering error occurred.", 3000)

    def enable_dev_tools(self):
        """Enable developer tools for debugging"""
        self.settings().setAttribute(QWebEngineSettings.DeveloperExtrasEnabled, True)
        self.page().setDevToolsPage(self.page())
        self.page().triggerAction(QWebEnginePage.InspectElement)

class UrlRequestInterceptor(QWebEngineUrlRequestInterceptor):
    def __init__(self, parent=None):
        super().__init__(parent)

    def interceptRequest(self, info):
        request_url = info.requestUrl().toString()
        from ad_blocker import AdBlocker
        if AdBlocker.instance().should_block(request_url):
            info.block(True)

class Browser(QMainWindow):
    tab_count_changed = pyqtSignal(int)
    fullscreen_toggled = pyqtSignal(bool)

    def __init__(self, initial_url="https://www.google.com", initial_zoom=1.0, settings=None,
                 bookmark_manager=None, history_manager=None, ad_blocker=None,
                 download_manager=None, incognito_manager=None, ai_assistant=None,
                 extension_handler=None):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
        QApplication.setAttribute(Qt.AA_UseStyleSheetPropagationInWidgetStyles, True)
        super().__init__()

        # Initialize managers and settings
        self.bookmark_manager = bookmark_manager
        self.history_manager = history_manager
        self.ad_blocker = ad_blocker
        self.download_manager = download_manager
        self.incognito_manager = incognito_manager
        self.ai_assistant = ai_assistant
        self.extension_handler = extension_handler
        self.settings = settings if settings else QSettings("ApexSoft", "Apex Browser")

        # Initialize other attributes
        self.zoom_factor = float(self.settings.value("browser/zoom", initial_zoom))
        self.last_closed_tab = None
        self.is_fullscreen = False
        self.cpu_monitor_enabled = self.settings.value("monitoring/cpu_enabled", True, type=bool)
        self.cpu_monitor_timer = None

        # Set window properties
        self.setWindowTitle("Apex Browser")
        self.setWindowIcon(QIcon('assets/icon.png'))
        self.setMinimumSize(800, 600)
        self.resize(1280, 720)
        self.setWindowFlags(Qt.FramelessWindowHint)

        # Setup UI components
        self.setup_ui()

        # Setup other components
        self.setup_shortcuts()
        self.setup_connections()
        self.setup_cpu_monitor()

    def setup_ui(self):
        self.ui = BrowserUI(self)
        self.title_bar = TitleBar(self)
        navbar = self.ui.create_navbar(self)
        status_bar = self.create_status_bar()

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.setDocumentMode(True)
        self.tabs.setMovable(True)
        self.tabs.setMinimumSize(800, 600)
        self.tabs.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        custom_tab_bar = CustomTabBar(self.tabs)
        self.tabs.setTabBar(custom_tab_bar)
        custom_tab_bar.new_tab_btn.clicked.connect(lambda: self.add_new_tab())

        # Add a container for the tabs and loading bar
        tab_container = QWidget()
        tab_layout = QVBoxLayout()
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.setSpacing(0)

        # Add the loading bar
        self.loading_bar = QFrame()
        self.loading_bar.setFixedHeight(2)
        self.loading_bar.setStyleSheet("background-color: #1a73e8;")
        self.loading_bar.setVisible(False)  # Hidden by default
        tab_layout.addWidget(self.loading_bar)

        # Add the tabs widget
        tab_layout.addWidget(self.tabs)
        tab_container.setLayout(tab_layout)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.title_bar)
        layout.addWidget(navbar)
        layout.addWidget(tab_container)
        layout.addWidget(status_bar)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.add_new_tab(self.settings.value("browser/homepage", "https://www.google.com"))
        self.apply_theme(self.settings.value("ui/theme", "light"))

    def create_status_bar(self):
        status_bar = QStatusBar()
        status_bar.setStyleSheet("""
            QStatusBar {
                background: #f1f3f4;
                border-top: 1px solid #dadce0;
                padding: 4px;
                font-family: Roboto, Arial, sans-serif;
                font-size: 12px;
            }
        """)
        self.security_status = QLabel()
        self.loading_progress = QLabel()
        status_bar.addPermanentWidget(self.security_status)
        status_bar.addPermanentWidget(self.loading_progress)
        return status_bar

    def setup_shortcuts(self):
        shortcuts = {
            "Ctrl+T": self.add_new_tab,
            "Ctrl+W": lambda: self.close_tab(self.tabs.currentIndex()),
            "Ctrl+Tab": lambda: self.tabs.setCurrentIndex((self.tabs.currentIndex() + 1) % self.tabs.count()),
            "Ctrl+Shift+T": self.reopen_last_closed_tab,
            "F5": self.current_browser().reload,
            "Ctrl+H": self.show_history,
            "Ctrl+D": lambda: self.ui.bookmark_current_page(self.current_browser()),
            "Ctrl+O": self.ui.open_file,
            "F11": self.toggle_fullscreen,
            "Ctrl++": lambda: self.zoom_in(),
            "Ctrl+-": lambda: self.zoom_out(),
            "Ctrl+0": lambda: self.reset_zoom(),
            "Ctrl+N": self.open_new_window,
        }
        for key, callback in shortcuts.items():
            shortcut = QShortcut(QKeySequence(key), self)
            shortcut.activated.connect(callback)

    def setup_connections(self):
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.tab_changed)
        self.tab_count_changed.connect(self.update_window_title)
        self.fullscreen_toggled.connect(self.handle_fullscreen_change)

    def setup_cpu_monitor(self):
        if self.cpu_monitor_enabled and psutil:
            self.cpu_monitor_timer = QTimer(self)
            self.cpu_monitor_timer.timeout.connect(self.log_cpu_usage)
            self.cpu_monitor_timer.start(60000)
            logger.info("CPU monitoring enabled")
        elif not psutil:
            logger.warning("CPU monitoring unavailable: psutil not installed")
        else:
            logger.info("CPU monitoring disabled")

    def log_cpu_usage(self):
        if psutil:
            cpu_percent = psutil.cpu_percent(interval=1)
            logger.info(f"CPU Usage: {cpu_percent}%")

    def apply_theme(self, theme):
        if theme == "dark":
            self.setStyleSheet("""
                QMainWindow {
                    background: #202124;
                }
                QTabWidget::pane {
                    border: none;
                }
                QFrame#titleBar {
                    background: #2D2D30;
                    border-bottom: 1px solid #3C4043;
                }
                QLabel#titleLabel {
                    color: #E0E0E0;
                }
            """)
            self.title_bar.setStyleSheet("""
                QFrame#titleBar {
                    background: #2D2D30;
                    border-bottom: 1px solid #3C4043;
                }
                QLabel {
                    color: #E0E0E0;
                }
            """)
        else:
            self.setStyleSheet("""
                QMainWindow {
                    background: #ffffff;
                }
                QTabWidget::pane {
                    border: none;
                }
                QFrame#titleBar {
                    background: #f1f3f4;
                    border-bottom: 1px solid #dadce0;
                }
                QLabel#titleLabel {
                    color: #202124;
                }
            """)
            self.title_bar.setStyleSheet("""
                QFrame#titleBar {
                    background: #f1f3f4;
                    border-bottom: 1px solid #dadce0;
                }
                QLabel {
                    color: #202124;
                }
            """)
        self.ui.change_theme(theme)

    def add_new_tab(self, url="https://www.google.com"):
        browser = WebView(self)
        profile = QWebEngineProfile.defaultProfile()
        self.configure_web_engine_profile(profile)  # This now sets user agent too
        browser.setPage(QWebEnginePage(profile, browser))
        profile.setRequestInterceptor(UrlRequestInterceptor())

        if self.incognito_manager and self.incognito_manager.is_incognito():
            incognito_profile = QWebEngineProfile()
            self.configure_web_engine_profile(incognito_profile)
            browser.setPage(QWebEnginePage(incognito_profile, browser))

        browser.setZoomFactor(float(self.settings.value("browser/zoom", 1.0)))
        browser.load(QUrl(url))
        browser.urlChanged.connect(lambda url: self.history_manager.add_entry(url.toString(), browser.title()))
        browser.loadStarted.connect(lambda: self.ui.start_loading_animation())
        browser.loadProgress.connect(self.ui.update_progress)
        browser.loadFinished.connect(lambda ok: self.handle_load_finished(browser, ok))
        browser.titleChanged.connect(lambda title: self.update_tab_title(browser))
        browser.iconChanged.connect(lambda icon: self.tabs.setTabIcon(self.tabs.indexOf(browser), icon))

        index = self.tabs.addTab(browser, "New Tab")
        self.tabs.setCurrentIndex(index)
        self.tab_count_changed.emit(self.tabs.count())
        logger.info(f"New tab opened with URL: {url}")
        return browser

    def configure_web_engine_profile(self, profile):
        """Configure web engine profile settings for better performance and compatibility"""
        profile.setHttpUserAgent(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 "
            "Safari/537.36"
        )
        profile.setHttpCacheType(QWebEngineProfile.DiskHttpCache)
        profile.setPersistentCookiesPolicy(QWebEngineProfile.AllowPersistentCookies)
        profile.setHttpCacheType(QWebEngineProfile.DiskHttpCache)
        profile.setPersistentCookiesPolicy(QWebEngineProfile.AllowPersistentCookies)
        profile.setHttpCacheMaximumSize(500 * 1024 * 1024)  # 500MB cache
        profile.setCachePath("cache")
        profile.setPersistentStoragePath("profiles")

        if hasattr(profile, 'setSpellCheckEnabled'):
            profile.setSpellCheckEnabled(True)
            profile.setSpellCheckLanguages(["en-US"])

        if hasattr(profile, 'setHttpAcceptLanguage'):
            profile.setHttpAcceptLanguage("en-US,en;q=0.9")

    def update_tab_title(self, browser):
        url = browser.url().toString()
        domain = url.split('/')[2] if len(url.split('/')) > 2 else url
        self.tabs.setTabText(self.tabs.indexOf(browser), domain or "New Tab")

    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.last_closed_tab = (self.tabs.widget(index).url().toString(), self.tabs.tabText(index))
            self.tabs.removeTab(index)
            self.tab_count_changed.emit(self.tabs.count())

    def reopen_last_closed_tab(self):
        if self.last_closed_tab:
            url, title = self.last_closed_tab
            browser = self.add_new_tab(url)
            self.tabs.setTabText(self.tabs.indexOf(browser), title)
            self.last_closed_tab = None

    def tab_changed(self, index):
        if index >= 0:
            browser = self.tabs.widget(index)
            browser.setWindowOpacity(0.0)
            fade_in = QPropertyAnimation(browser, b"windowOpacity")
            fade_in.setDuration(300)
            fade_in.setStartValue(0.0)
            fade_in.setEndValue(1.0)
            fade_in.setEasingCurve(QEasingCurve.InOutCubic)
            fade_in.start()
            self.ui.url_bar.setText(browser.url().toString())
            self.update_window_title(self.tabs.count())

    def update_window_title(self, count):
        current_browser = self.current_browser()
        title = current_browser.title() if current_browser else "Apex Browser"
        self.setWindowTitle(f"{title} - Apex Browser")

    def current_browser(self):
        return self.tabs.currentWidget()

    def toggle_fullscreen(self):
        self.is_fullscreen = not self.is_fullscreen
        if self.is_fullscreen:
            self.showFullScreen()
        else:
            self.showNormal()
        self.fullscreen_toggled.emit(self.is_fullscreen)

    def handle_fullscreen_change(self, is_fullscreen):
        self.title_bar.setVisible(not is_fullscreen)
        self.ui.update_fullscreen_ui(is_fullscreen)

    def zoom_in(self):
        if self.current_browser():
            current_zoom = self.current_browser().zoomFactor()
            new_zoom = min(3.0, current_zoom + 0.1)
            self.current_browser().setZoomFactor(new_zoom)
            anim = QPropertyAnimation(self.current_browser(), b"zoomFactor")
            anim.setDuration(200)
            anim.setStartValue(current_zoom)
            anim.setEndValue(new_zoom)
            anim.setEasingCurve(QEasingCurve.InOutCubic)
            anim.start()
            self.settings.setValue("browser/zoom", new_zoom)
            logger.info(f"Zoomed in to {new_zoom}")

    def zoom_out(self):
        if self.current_browser():
            current_zoom = self.current_browser().zoomFactor()
            new_zoom = max(0.25, current_zoom - 0.1)
            self.current_browser().setZoomFactor(new_zoom)
            anim = QPropertyAnimation(self.current_browser(), b"zoomFactor")
            anim.setDuration(200)
            anim.setStartValue(current_zoom)
            anim.setEndValue(new_zoom)
            anim.setEasingCurve(QEasingCurve.InOutCubic)
            anim.start()
            self.settings.setValue("browser/zoom", new_zoom)
            logger.info(f"Zoomed out to {new_zoom}")

    def reset_zoom(self):
        if self.current_browser():
            self.current_browser().setZoomFactor(1.0)
            self.settings.setValue("browser/zoom", 1.0)
            logger.info("Zoom reset to 1.0")

    def handle_load_finished(self, browser, ok):
        self.ui.url_bar.setText(browser.url().toString())
        if not ok:
            self.ui.show_notification("Failed to load page", 5000)
        browser.setFixedSize(self.tabs.size())
        self.ui.stop_loading_animation()

    def open_new_window(self):
        new_browser = Browser(
            initial_url="https://www.google.com",
            initial_zoom=float(self.settings.value("browser/zoom", 1.0)),
            settings=self.settings,
            bookmark_manager=self.bookmark_manager,
            history_manager=self.history_manager,
            ad_blocker=self.ad_blocker,
            download_manager=self.download_manager,
            incognito_manager=self.incognito_manager,
            ai_assistant=self.ai_assistant,
            extension_handler=self.extension_handler
        )
        new_browser.show()

    def show_history(self):
        self.ui.show_history()

    def show_downloads(self):
        self.ui.show_downloads()

    def show_extensions(self):
        self.ui.show_extensions()

    def clear_cookies(self):
        QWebEngineProfile.defaultProfile().cookieStore().deleteAllCookies()
        self.ui.show_notification("Cookies cleared")

    def voice_search(self, url_bar, browser):
        query = voice_search()
        if query:
            url_bar.setText(query)
            browser.setUrl(QUrl(f"https://www.google.com/search?q={query}"))

    def closeEvent(self, event):
        if self.cpu_monitor_timer:
            self.cpu_monitor_timer.stop()
        event.accept()

    def force_repaint(self):
        """Force a complete repaint of all web views"""
        for i in range(self.tabs.count()):
            browser = self.tabs.widget(i)
            browser.repaint()
            browser.page().setViewportSize(browser.size())

    def reset_web_engine(self):
        """Reset all web engine settings to defaults"""
        for i in range(self.tabs.count()):
            browser = self.tabs.widget(i)
            settings = browser.settings()
            settings.setAttribute(QWebEngineSettings.Accelerated2dCanvasEnabled, True)
            settings.setAttribute(QWebEngineSettings.WebGLEnabled, True)
            settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
            browser.reload()

    def check_rendering_status(self):
        """Log current rendering status"""
        browser = self.current_browser()
        if browser:
            logger.info("Current rendering status:")
            logger.info(f"Hardware Acceleration: {browser.hardware_acceleration}")
            logger.info(f"WebGL Enabled: {browser.settings().testAttribute(QWebEngineSettings.WebGLEnabled)}")
            logger.info(f"JavaScript Enabled: {browser.settings().testAttribute(QWebEngineSettings.JavascriptEnabled)}")

            # Check WebGL support
            browser.page().runJavaScript(
                "!!window.WebGLRenderingContext && document.createElement('canvas').getContext('webgl')",
                lambda result: logger.info(f"WebGL actually working: {result}")
            )
