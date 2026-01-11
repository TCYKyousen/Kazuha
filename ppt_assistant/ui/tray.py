from PySide6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PySide6.QtGui import QIcon, QAction, QPainter, QColor, QPixmap, QGuiApplication
from PySide6.QtCore import Signal, QObject, Qt
from PySide6.QtSvg import QSvgRenderer
import os
from qfluentwidgets import themeColor

ICON_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "icons")

class SystemTray(QObject):
    show_settings = Signal()
    restart_app = Signal()
    exit_app = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.tray_icon = QSystemTrayIcon(parent)
        self._update_icon()
        
        self.tray_icon.setToolTip("Kazuha 助手")
        
        self.menu = QMenu()
        
        self.action_settings = QAction("设置", self.menu)
        self.action_settings.triggered.connect(self.show_settings.emit)
        
        self.action_restart = QAction("重启", self.menu)
        self.action_restart.triggered.connect(self.restart_app.emit)
        
        self.action_exit = QAction("退出", self.menu)
        self.action_exit.triggered.connect(self.exit_app.emit)
        
        self.menu.addAction(self.action_settings)
        self.menu.addSeparator()
        self.menu.addAction(self.action_restart)
        self.menu.addAction(self.action_exit)
        
        self.tray_icon.setContextMenu(self.menu)
        self.tray_icon.show()

    def _update_icon(self):
        # Use logo if available, else generic icon
        logo_path = os.path.join(ICON_DIR, "logo.svg")
        if not os.path.exists(logo_path):
             logo_path = os.path.join(ICON_DIR, "Pen.svg") # Fallback
        
        # Colorize the logo with theme color
        color = themeColor()
        
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        renderer = QSvgRenderer(logo_path)
        renderer.render(painter)
        
        # Apply theme color overlay
        painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
        painter.fillRect(pixmap.rect(), color)
        painter.end()
        
        self.tray_icon.setIcon(QIcon(pixmap))
    
    def show_message(self, title, message):
        self.tray_icon.showMessage(title, message, QSystemTrayIcon.Information, 2000)
