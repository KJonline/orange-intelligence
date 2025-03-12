from config import CONFIG
from PyQt6.QtCore import QCoreApplication, pyqtSignal
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QMenu, QSystemTrayIcon


class SystemTray(QSystemTrayIcon):
    # Signal to notify when settings should be opened
    open_settings_signal = pyqtSignal()
    # Signal to notify when app should quit
    quit_signal = pyqtSignal()
    
    def __init__(self):
        icon = CONFIG.get("app").get("icon")

        super().__init__(QIcon(icon))

        # Create the tray menu
        self.menu = QMenu()

        # Add actions to the menu
        self.create_menu_actions()

        # Set the menu to the tray icon
        self.setContextMenu(self.menu)

    def create_menu_actions(self):
        """Creates and adds actions to the context menu."""
        
        # Action to open settings
        settings_action = QAction("⚙️ Settings", self)
        settings_action.triggered.connect(self.open_settings)
        settings_action.setToolTip("Open application settings")
        
        # Action to quit the application
        quit_action = QAction("❌ Quit", self)
        quit_action.triggered.connect(self.quit_app)
        quit_action.setToolTip("Quit the application")

        # Add actions to the menu
        self.menu.addAction(settings_action)
        self.menu.addSeparator()
        self.menu.addAction(quit_action)

    def open_settings(self):
        """Emit signal to open settings window."""
        self.open_settings_signal.emit()

    def show_message(self, title: str, message: str):
        """Displays a message balloon from the system tray."""
        self.showMessage(title, message, QSystemTrayIcon.MessageIcon.Information)

    def quit_app(self):
        """Emits signal to quit the application."""
        self.quit_signal.emit()
