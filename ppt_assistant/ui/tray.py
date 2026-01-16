from PySide6.QtWidgets import QSystemTrayIcon
from PySide6.QtGui import QIcon, QPainter, QPixmap, QCursor
from PySide6.QtCore import Signal, QObject, Qt
from PySide6.QtSvg import QSvgRenderer
import os
from qfluentwidgets import RoundMenu, Action, themeColor, FluentIcon as FIF
from ppt_assistant.core.i18n import t

ICON_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "icons")

class SystemTray(QObject):
    show_settings = Signal()
    show_timer = Signal()
    restart_app = Signal()
    exit_app = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.tray_icon = QSystemTrayIcon(parent)
        self._update_icon()
        self.tray_icon.setToolTip(t("tray.tooltip"))
        self.menu = RoundMenu(parent=parent)
        self.act_header = Action(QIcon(os.path.join(ICON_DIR, "logo.svg")), t("tray.title"), self.menu)
        self.menu.addAction(self.act_header)
        
        self.menu.addSeparator()
        
        self.act_settings = Action(FIF.SETTING, t("tray.settings"), self.menu)
        self.act_settings.triggered.connect(self.show_settings.emit)
        self.menu.addAction(self.act_settings)
        
        self.act_timer = Action(QIcon(os.path.join(ICON_DIR, "Timer.svg")), t("tray.timer"), self.menu)
        self.act_timer.triggered.connect(self.show_timer.emit)
        self.menu.addAction(self.act_timer)
        
        self.menu.addSeparator()
        
        self.act_restart = Action(FIF.SYNC, t("tray.restart"), self.menu)
        self.act_restart.triggered.connect(self.restart_app.emit)
        self.menu.addAction(self.act_restart)
        
        self.act_exit = Action(FIF.POWER_BUTTON, t("tray.exit"), self.menu)
        self.act_exit.triggered.connect(self.exit_app.emit)
        self.menu.addAction(self.act_exit)
        
        self.tray_icon.setContextMenu(self.menu)
        self.tray_icon.activated.connect(self._on_activated)
        
        self.tray_icon.show()

    def _on_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self.menu.exec(QCursor.pos())

    def _update_icon(self):
        logo_path = os.path.join(ICON_DIR, "logo.svg")
        if not os.path.exists(logo_path):
             logo_path = os.path.join(ICON_DIR, "Pen.svg")
        
        color = themeColor()
        
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        renderer = QSvgRenderer(logo_path)
        renderer.render(painter)
        
        painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
        painter.fillRect(pixmap.rect(), color)
        painter.end()
        
        self.tray_icon.setIcon(QIcon(pixmap))
    
    def show_message(self, title, message):
        self.tray_icon.showMessage(title, message, QSystemTrayIcon.Information, 2000)
