from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
                             QLineEdit, QFileDialog, QMenu, QAction,
                             QComboBox, QTabBar, QLabel,
                             QFrame, QSizePolicy, QDialog, QMessageBox,
                             QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt5.QtCore import QUrl, Qt, pyqtSignal, QSize, QTimer, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QIcon, QPixmap, QCursor, QFont, QPalette, QColor


class BrowserUI:
    def __init__(self, parent):
        self.parent = parent
        self.url_bar = None
        self.settings_menu = None
        self.theme = "light"
        self.setup_fonts()
        self.navbar_visible = True
        self.navbar_container = None
        self.loading_animation = None

    def setup_fonts(self):
        self.main_font = QFont("Roboto", 10)
        self.url_font = QFont("Roboto", 12)
        self.button_font = QFont("Roboto", 12)

    def create_navbar(self, browser):
        self.navbar_container = QFrame()
        self.navbar_container.setObjectName("navContainer")
        self.navbar_container.setFrameShape(QFrame.NoFrame)
        self.navbar_container.setMinimumHeight(40)
        self.navbar_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        container_layout = QVBoxLayout()
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        navbar = QWidget()
        navbar.setObjectName("navbar")
        navbar.setMinimumHeight(36)
        navbar.setMaximumHeight(36)
        navbar.setStyleSheet("background: #f1f3f4;")
        navbar_layout = QHBoxLayout()
        navbar_layout.setContentsMargins(8, 2, 8, 2)
        navbar_layout.setSpacing(4)

        nav_group = QFrame()
        nav_layout = QHBoxLayout()
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(4)

        back_btn = self.create_nav_button("◄", "Go Back", lambda: browser.current_browser().back(), is_navigation=True)
        forward_btn = self.create_nav_button("►", "Go Forward", lambda: browser.current_browser().forward(),
                                             is_navigation=True)
        reload_btn = self.create_nav_button("↻", "Reload Page", lambda: browser.current_browser().reload())
        home_btn = self.create_nav_button("🏠", "Go to Homepage",
                                          lambda: browser.current_browser().setUrl(QUrl("https://www.google.com")))

        nav_layout.addWidget(back_btn)
        nav_layout.addWidget(forward_btn)
        nav_layout.addWidget(reload_btn)
        nav_layout.addWidget(home_btn)
        nav_group.setLayout(nav_layout)

        self.url_bar = QLineEdit()
        self.url_bar.setObjectName("urlBar")
        self.url_bar.setPlaceholderText("Search Google or type a URL")
        self.url_bar.setFont(self.url_font)
        self.url_bar.setClearButtonEnabled(True)
        self.url_bar.returnPressed.connect(lambda: self.navigate_to_url(browser.current_browser()))
        self.url_bar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.url_bar.setMinimumHeight(32)
        self.url_bar.setMaximumWidth(800)
        self.url_bar.setStyleSheet("""
            QLineEdit {
                background-color: #ffffff;
                color: #202124;
                border: 1px solid #dadce0;
                border-radius: 16px;
                padding: 4px 12px;
                font-family: Roboto, Arial, sans-serif;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #1a73e8;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            }
        """)

        action_group = QFrame()
        action_layout = QHBoxLayout()
        action_layout.setContentsMargins(0, 0, 0, 0)
        action_layout.setSpacing(4)

        voice_search_btn = self.create_action_button("🎤", "Voice Search",
                                                     lambda: self.parent.voice_search(self.url_bar,
                                                                                      browser.current_browser()))
        bookmark_btn = self.create_action_button("★", "Bookmark This Page",
                                                 lambda: self.bookmark_current_page(browser.current_browser()),
                                                 is_bookmark=True)
        history_btn = self.create_action_button("⏱", "View History",
                                                lambda: self.show_history())
        settings_btn = self.create_action_button("⋮", "Settings",
                                                 lambda: self.show_settings_menu())
        action_layout.addWidget(voice_search_btn)
        action_layout.addWidget(bookmark_btn)
        action_layout.addWidget(history_btn)
        action_layout.addWidget(settings_btn)
        action_group.setLayout(action_layout)

        self.create_settings_menu(browser)

        navbar_layout.addWidget(nav_group)
        navbar_layout.addStretch()
        navbar_layout.addWidget(self.url_bar)
        navbar_layout.addStretch()
        navbar_layout.addWidget(action_group)
        navbar.setLayout(navbar_layout)

        container_layout.addWidget(navbar)
        self.navbar_container.setLayout(container_layout)

        return self.navbar_container

    def create_nav_button(self, text, tooltip, callback, is_navigation=False):
        button = QPushButton(text)
        button.setObjectName("navButton")
        button.setToolTip(tooltip)
        button.clicked.connect(callback)
        button.setFont(self.button_font)
        button.setFixedSize(36, 36)
        button.setStyleSheet("""
            QPushButton {
                background-color: #f1f3f4;
                color: #5f6368;
                border: none;
                border-radius: 18px;
                font-family: Roboto, Arial, sans-serif;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #e8eaed;
                box-shadow: 0 1px 2px rgba(0,0,0,0.1);
            }
            QPushButton:pressed {
                background-color: #dadce0;
            }
        """)
        return button

    def create_action_button(self, text, tooltip, callback, is_bookmark=False):
        button = QPushButton(text)
        button.setObjectName("actionButton" if not is_bookmark else "bookmarkButton")
        button.setToolTip(tooltip)
        button.clicked.connect(callback)
        button.setFont(self.button_font)
        button.setFixedSize(36, 36)
        if is_bookmark:
            button.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #1a73e8;
                    border: none;
                    border-radius: 18px;
                    font-size: 18px;
                }
                QPushButton:hover {
                    background-color: #e8eaed;
                    box-shadow: 0 1px 2px rgba(0,0,0,0.1);
                }
                QPushButton:pressed {
                    background-color: #dadce0;
                }
            """)
        else:
            button.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #202124;
                    border: none;
                    border-radius: 18px;
                    font-size: 18px;
                }
                QPushButton:hover {
                    background-color: #e8eaed;
                    box-shadow: 0 1px 2px rgba(0,0,0,0.1);
                }
                QPushButton:pressed {
                    background-color: #dadce0;
                }
            """)
        return button

    def navigate_to_url(self, browser):
        url_text = self.url_bar.text().strip()
        if not url_text:
            return
        if not url_text.startswith(('http://', 'https://', 'file://')):
            if '.' in url_text and ' ' not in url_text:
                url_text = 'https://' + url_text
            else:
                url_text = 'https://www.google.com/search?q=' + url_text.replace(' ', '+')
        browser.setUrl(QUrl(url_text))

    def start_loading_animation(self):
        self.parent.loading_bar.setVisible(True)
        self.loading_animation = QPropertyAnimation(self.parent.loading_bar, b"geometry")
        self.loading_animation.setDuration(1500)
        start_rect = self.parent.loading_bar.geometry()
        start_rect.setWidth(0)
        end_rect = self.parent.loading_bar.geometry()
        end_rect.setWidth(self.parent.loading_bar.parent().width())
        self.loading_animation.setStartValue(start_rect)
        self.loading_animation.setEndValue(end_rect)
        self.loading_animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.loading_animation.setLoopCount(-1)  # Loop indefinitely
        self.loading_animation.start()

    def update_progress(self, progress):
        # Progress updates are now handled by the animation
        pass

    def stop_loading_animation(self):
        if self.loading_animation:
            self.loading_animation.stop()
        self.parent.loading_bar.setVisible(False)

    def bookmark_current_page(self, browser):
        url = browser.url().toString()
        title = browser.page().title()
        if hasattr(self.parent, 'bookmark_manager'):
            self.parent.bookmark_manager.add_bookmark(url, title)
            self.show_notification(f"Bookmarked: {title}")
        else:
            self.show_notification("Bookmark feature not yet implemented")

    def show_history(self):
        if hasattr(self.parent, 'history_manager'):
            history_dialog = QDialog(self.parent)
            history_dialog.setWindowTitle("Browsing History")
            history_dialog.setMinimumSize(600, 400)
            layout = QVBoxLayout()
            layout.setContentsMargins(8, 8, 8, 8)

            history_table = QTableWidget()
            history_table.setRowCount(0)
            history_table.setColumnCount(3)
            history_table.setHorizontalHeaderLabels(["URL", "Title", "Timestamp"])
            history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            history_table.setStyleSheet("""
                QTableWidget {
                    background-color: #ffffff;
                    border: 1px solid #dadce0;
                    border-radius: 4px;
                    font-family: Roboto, Arial, sans-serif;
                }
                QHeaderView::section {
                    background-color: #f1f3f4;
                    color: #202124;
                    padding: 4px;
                }
            """)

            history_entries = self.parent.history_manager.get_history()
            history_table.setRowCount(len(history_entries))
            for row, (url, title, timestamp) in enumerate(history_entries):
                history_table.setItem(row, 0, QTableWidgetItem(url))
                history_table.setItem(row, 1, QTableWidgetItem(title or "Untitled"))
                history_table.setItem(row, 2, QTableWidgetItem(timestamp))

            layout.addWidget(history_table)

            clear_btn = QPushButton("Clear History")
            clear_btn.clicked.connect(self.clear_history)
            clear_btn.setStyleSheet("""
                QPushButton {
                    background-color: #1a73e8;
                    color: white;
                    border-radius: 4px;
                    padding: 6px;
                    font-family: Roboto, Arial, sans-serif;
                }
                QPushButton:hover {
                    background-color: #1557b0;
                }
            """)
            layout.addWidget(clear_btn)

            history_dialog.setLayout(layout)
            history_dialog.exec_()
        else:
            self.show_notification("History feature not yet implemented")

    def show_downloads(self):
        if hasattr(self.parent, 'download_manager'):
            downloads_dialog = QDialog(self.parent)
            downloads_dialog.setWindowTitle("Downloads")
            downloads_dialog.setMinimumSize(600, 400)
            layout = QVBoxLayout()
            layout.setContentsMargins(8, 8, 8, 8)

            downloads_table = QTableWidget()
            downloads_table.setRowCount(0)
            downloads_table.setColumnCount(4)
            downloads_table.setHorizontalHeaderLabels(["File Path", "URL", "Date", "Size"])
            downloads_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            downloads_table.setStyleSheet("""
                QTableWidget {
                    background-color: #ffffff;
                    border: 1px solid #dadce0;
                    border-radius: 4px;
                    font-family: Roboto, Arial, sans-serif;
                }
                QHeaderView::section {
                    background-color: #f1f3f4;
                    color: #202124;
                    padding: 4px;
                }
            """)

            download_entries = self.parent.download_manager.get_download_history()
            downloads_table.setRowCount(len(download_entries))
            for row, entry in enumerate(download_entries):
                downloads_table.setItem(row, 0, QTableWidgetItem(entry['path']))
                downloads_table.setItem(row, 1, QTableWidgetItem(entry['url']))
                downloads_table.setItem(row, 2, QTableWidgetItem(entry['date']))
                downloads_table.setItem(row, 3, QTableWidgetItem(str(entry['size'])))

            layout.addWidget(downloads_table)

            clear_btn = QPushButton("Clear Download History")
            clear_btn.clicked.connect(lambda: self.parent.download_manager.clear_download_history())
            clear_btn.clicked.connect(downloads_dialog.close)
            clear_btn.setStyleSheet("""
                QPushButton {
                    background-color: #1a73e8;
                    color: white;
                    border-radius: 4px;
                    padding: 6px;
                    font-family: Roboto, Arial, sans-serif;
                }
                QPushButton:hover {
                    background-color: #1557b0;
                }
            """)
            layout.addWidget(clear_btn)

            downloads_dialog.setLayout(layout)
            downloads_dialog.exec_()
        else:
            self.show_notification("Downloads manager not yet implemented")

    def create_settings_menu(self, browser):
        self.settings_menu = QMenu()
        self.settings_menu.setFont(self.main_font)
        self.settings_menu.setStyleSheet("""
            QMenu {
                background-color: #ffffff;
                border: 1px solid #dadce0;
                border-radius: 4px;
                padding: 4px;
                font-family: Roboto, Arial, sans-serif;
            }
            QMenu::item {
                padding: 6px 20px;
                border-radius: 2px;
            }
            QMenu::item:selected {
                background-color: #f1f3f4;
                color: #1a73e8;
            }
            QMenu::separator {
                height: 1px;
                background-color: #dadce0;
                margin: 4px 10px;
            }
        """)

        theme_menu = QMenu("Theme")
        theme_menu.setFont(self.main_font)
        light_theme_action = QAction("Light Theme", self.settings_menu)
        dark_theme_action = QAction("Dark Theme", self.settings_menu)
        light_theme_action.triggered.connect(lambda: self.change_theme("light"))
        dark_theme_action.triggered.connect(lambda: self.change_theme("dark"))
        theme_menu.addAction(light_theme_action)
        theme_menu.addAction(dark_theme_action)

        zoom_menu = QMenu("Zoom")
        zoom_menu.setFont(self.main_font)
        zoom_in_action = QAction("Zoom In (Ctrl++)", self.settings_menu)
        zoom_out_action = QAction("Zoom Out (Ctrl+-)", self.settings_menu)
        zoom_reset_action = QAction("Reset Zoom (Ctrl+0)", self.settings_menu)
        zoom_in_action.triggered.connect(
            lambda: browser.current_browser().setZoomFactor(browser.current_browser().zoomFactor() + 0.1))
        zoom_out_action.triggered.connect(
            lambda: browser.current_browser().setZoomFactor(browser.current_browser().zoomFactor() - 0.1))
        zoom_reset_action.triggered.connect(lambda: browser.current_browser().setZoomFactor(1.0))
        zoom_menu.addAction(zoom_in_action)
        zoom_menu.addAction(zoom_out_action)
        zoom_menu.addAction(zoom_reset_action)

        privacy_menu = QMenu("Privacy")
        privacy_menu.setFont(self.main_font)
        incognito_action = QAction("Incognito Mode", self.settings_menu)
        clear_cookies_action = QAction("Clear Cookies", self.settings_menu)
        clear_history_action = QAction("Clear History", self.settings_menu)
        incognito_action.triggered.connect(self.toggle_incognito_mode)
        clear_cookies_action.triggered.connect(self.clear_cookies)
        clear_history_action.triggered.connect(self.clear_history)
        privacy_menu.addAction(incognito_action)
        privacy_menu.addAction(clear_cookies_action)
        privacy_menu.addAction(clear_history_action)

        self.settings_menu.addMenu(theme_menu)
        self.settings_menu.addMenu(zoom_menu)
        self.settings_menu.addMenu(privacy_menu)
        self.settings_menu.addSeparator()
        downloads_action = QAction("Downloads", self.settings_menu)
        downloads_action.triggered.connect(self.show_downloads)
        extensions_action = QAction("Extensions", self.settings_menu)
        extensions_action.triggered.connect(self.show_extensions)
        about_action = QAction("About Apex Browser", self.settings_menu)
        about_action.triggered.connect(self.show_about)
        self.settings_menu.addAction(downloads_action)
        self.settings_menu.addAction(extensions_action)
        self.settings_menu.addSeparator()
        self.settings_menu.addAction(about_action)

    def show_settings_menu(self):
        if self.settings_menu:
            for button in self.parent.findChildren(QPushButton):
                if button.toolTip() == "Settings":
                    self.settings_menu.exec_(button.mapToGlobal(button.rect().bottomLeft()))
                    return
            self.settings_menu.exec_(QCursor.pos())

    def change_theme(self, theme):
        self.theme = theme
        if theme == "light":
            self.apply_light_theme(self.parent)
        else:
            self.apply_dark_theme(self.parent)
        self.show_notification(f"{theme.capitalize()} theme applied")

    def toggle_incognito_mode(self):
        if hasattr(self.parent, 'incognito_manager'):
            self.parent.incognito_manager.toggle_incognito()
            self.show_notification("Incognito mode toggled")
        else:
            self.show_notification("Incognito mode not yet implemented")

    def clear_cookies(self):
        if hasattr(self.parent, 'clear_cookies'):
            self.parent.clear_cookies()
            self.show_notification("Cookies cleared")
        else:
            self.show_notification("Cookie management not yet implemented")

    def clear_history(self):
        if hasattr(self.parent, 'history_manager'):
            self.parent.history_manager.clear_history()
            self.show_notification("Browsing history cleared")
        else:
            self.show_notification("History management not yet implemented")

    def show_extensions(self):
        if hasattr(self.parent, 'extension_handler'):
            extensions_dialog = QDialog(self.parent)
            extensions_dialog.setWindowTitle("Extensions")
            extensions_dialog.setMinimumSize(400, 300)
            layout = QVBoxLayout()
            layout.setContentsMargins(8, 8, 8, 8)

            extensions = self.parent.extension_handler.get_extensions()
            for ext_id, ext_info in extensions.items():
                ext_widget = QWidget()
                ext_layout = QHBoxLayout()
                ext_label = QLabel(f"{ext_info['name']} (v{ext_info['version']})")
                ext_label.setStyleSheet("font-family: Roboto, Arial, sans-serif; font-size: 14px;")
                toggle_btn = QPushButton("Disable" if ext_info['enabled'] else "Enable")
                toggle_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #1a73e8;
                        color: white;
                        border-radius: 4px;
                        padding: 4px;
                        font-family: Roboto, Arial, sans-serif;
                    }
                    QPushButton:hover {
                        background-color: #1557b0;
                    }
                """)
                toggle_btn.clicked.connect(lambda checked, eid=ext_id: self.toggle_extension(eid))
                ext_layout.addWidget(ext_label)
                ext_layout.addStretch()
                ext_layout.addWidget(toggle_btn)
                ext_widget.setLayout(ext_layout)
                layout.addWidget(ext_widget)

            extensions_dialog.setLayout(layout)
            extensions_dialog.exec_()
        else:
            self.show_notification("Extensions manager not yet implemented")

    def toggle_extension(self, ext_id):
        if hasattr(self.parent, 'extension_handler'):
            ext = self.parent.extension_handler.get_extensions().get(ext_id)
            if ext['enabled']:
                self.parent.extension_handler.disable_extension(ext_id)
                self.show_notification(f"Disabled {ext['name']}")
            else:
                self.parent.extension_handler.enable_extension(ext_id)
                self.show_notification(f"Enabled {ext['name']}")

    def show_about(self):
        about_box = QMessageBox(self.parent)
        about_box.setWindowTitle("About Apex Browser")
        about_box.setTextFormat(Qt.RichText)
        about_box.setText("""
        <div style='text-align: center; font-family: Roboto, Arial, sans-serif;'>
            <h2 style='color: #1a73e8;'>Apex Browser</h2>
            <p>Version 1.2.0</p>
            <p style='margin-top: 10px;'>An elite, modern web browser</p>
            <p style='margin-top: 15px; color: #5f6368;'>Built with Python and PyQt5</p>
            <p style='margin-top: 15px;'>© 2025 ApexSoft</p>
        </div>
        """)
        about_box.setStandardButtons(QMessageBox.Ok)
        about_box.setStyleSheet("""
            QMessageBox {
                background-color: #ffffff;
                font-family: Roboto, Arial, sans-serif;
            }
            QPushButton {
                background-color: #1a73e8;
                color: white;
                border: none;
                padding: 6px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1557b0;
            }
        """)
        about_box.exec_()

    def show_notification(self, message, duration=3000):
        notification = QDialog(self.parent)
        notification.setObjectName("notification")
        notification.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        notification.setStyleSheet("""
            #notification {
                background-color: #323232;
                color: #ffffff;
                border-radius: 4px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.2);
            }
        """)
        layout = QVBoxLayout()
        label = QLabel(message)
        label.setStyleSheet(
            "padding: 8px 16px; font-family: Roboto, Arial, sans-serif; font-size: 13px; color: #ffffff;")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        notification.setLayout(layout)
        notification.setFixedWidth(250)
        notification.layout().setContentsMargins(0, 0, 0, 0)
        x = self.parent.x() + self.parent.width() - notification.width() - 20
        y = self.parent.y() + self.parent.height() - notification.height() - 20
        notification.move(x, y)
        notification.setWindowOpacity(0.0)
        notification.show()
        fade_in = QPropertyAnimation(notification, b"windowOpacity")
        fade_in.setDuration(200)
        fade_in.setStartValue(0.0)
        fade_in.setEndValue(0.9)
        fade_in.setEasingCurve(QEasingCurve.InOutCubic)
        fade_in.start()
        fade_out = QPropertyAnimation(notification, b"windowOpacity")
        fade_out.setDuration(300)
        fade_out.setStartValue(0.9)
        fade_out.setEndValue(0.0)
        fade_out.setEasingCurve(QEasingCurve.InOutCubic)
        QTimer.singleShot(duration, fade_out.start)
        fade_out.finished.connect(notification.close)

    def open_file(self):
        file_dialog = QFileDialog(self.parent)
        file_dialog.setWindowTitle("Open File")
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setNameFilter("All Files (*);;HTML Files (*.html *.htm);;Text Files (*.txt)")
        file_dialog.setStyleSheet("""
            QFileDialog {
                background-color: #ffffff;
                font-family: Roboto, Arial, sans-serif;
            }
            QPushButton {
                background-color: #f1f3f4;
                border: 1px solid #dadce0;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #e8eaed;
            }
            QLineEdit {
                border: 1px solid #dadce0;
                padding: 6px;
                border-radius: 4px;
            }
        """)
        if file_dialog.exec_():
            file_paths = file_dialog.selectedFiles()
            if file_paths:
                file_path = file_paths[0]
                if file_path.lower().endswith(('.html', '.htm')):
                    self.parent.current_browser().setUrl(QUrl.fromLocalFile(file_path))
                else:
                    self.show_notification(f"File opened: {file_path.split('/')[-1]}")

    def update_fullscreen_ui(self, is_fullscreen):
        self.navbar_visible = not is_fullscreen
        self.url_bar.setVisible(self.navbar_visible)
        self.navbar_container.setVisible(self.navbar_visible)
        self.show_notification(f"Fullscreen mode {'enabled' if is_fullscreen else 'disabled'}")

    def show_navbar(self):
        if not self.navbar_visible and self.parent.is_fullscreen:
            self.navbar_visible = True
            self.navbar_container.setVisible(True)
            fade_in = QPropertyAnimation(self.navbar_container, b"windowOpacity")
            fade_in.setDuration(200)
            fade_in.setStartValue(0.0)
            fade_in.setEndValue(1.0)
            fade_in.setEasingCurve(QEasingCurve.InOutCubic)
            fade_in.start()

    def hide_navbar(self):
        if self.navbar_visible and self.parent.is_fullscreen:
            self.navbar_visible = False
            fade_out = QPropertyAnimation(self.navbar_container, b"windowOpacity")
            fade_out.setDuration(200)
            fade_out.setStartValue(1.0)
            fade_out.setEndValue(0.0)
            fade_out.setEasingCurve(QEasingCurve.InOutCubic)
            fade_out.start()
            fade_out.finished.connect(lambda: self.navbar_container.setVisible(False))

    @staticmethod
    def apply_dark_theme(main_window):
        try:
            with open("assets/dark_theme.qss", "r") as file:
                main_window.setStyleSheet(file.read())
        except Exception as e:
            print(f"Error loading dark theme: {e}")
            main_window.setStyleSheet("""
                QWidget {
                    background-color: #202124;
                    color: #E0E0E0;
                    font-family: Roboto, Arial, sans-serif;
                }
                QTabWidget::pane {
                    border: none;
                }
                QTabBar::tab {
                    background-color: #2D2D30;
                    color: #E0E0E0;
                    padding: 6px 12px;
                    border-radius: 4px;
                }
                QTabBar::tab:selected {
                    background-color: #3C4043;
                    border-bottom: 2px solid #1a73e8;
                }
            """)

    @staticmethod
    def apply_light_theme(main_window):
        try:
            with open("assets/light_theme.qss", "r") as file:
                main_window.setStyleSheet(file.read())
        except Exception as e:
            print(f"Error loading light theme: {e}")
            main_window.setStyleSheet("""
                QWidget {
                    background-color: #FFFFFF;
                    color: #202124;
                    font-family: Roboto, Arial, sans-serif;
                }
                QTabWidget::pane {
                    border: none;
                }
                QTabBar::tab {
                    background-color: #F1F3F4;
                    color: #202124;
                    padding: 6px 12px;
                    border-radius: 4px;
                }
                QTabBar::tab:selected {
                    background-color: #FFFFFF;
                    border-bottom: 2px solid #1a73e8;
                }
            """)
