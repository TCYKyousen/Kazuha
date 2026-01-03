import os
import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QObject

# Mock Bridge
class Bridge(QObject):
    def __init__(self):
        super().__init__()
    @property
    def versionText(self): return "1.0.0"
    @property
    def themeMode(self): return "Auto"
    @property
    def themeModeIndex(self): return 0
    @property
    def isUpdating(self): return False
    @property
    def updateStatusTitle(self): return "Title"
    @property
    def updateLastCheckText(self): return "Text"
    @property
    def updateLogs(self): return "Logs"
    @property
    def baseDir(self): return "."
    @property
    def updateProgress(self): return 0.0
    @property
    def screenPaddingIndex(self): return 0

class ThemeManager(QObject):
    def __init__(self):
        super().__init__()
    def toggle_theme(self, mode): pass

app = QApplication(sys.argv)
engine = QQmlApplicationEngine()

# Add RinUI path
import RinUI
rin_ui_path = os.path.dirname(os.path.dirname(RinUI.__file__))
engine.addImportPath(rin_ui_path)
engine.addImportPath(str(Path("h:/Dev/Kazuha/ui")))

bridge = Bridge()
theme_manager = ThemeManager()
engine.rootContext().setContextProperty("Bridge", bridge)
engine.rootContext().setContextProperty("ThemeManager", theme_manager)

qml_path = "h:/Dev/Kazuha/ui/Settings.qml"
engine.load(qml_path)

if not engine.rootObjects():
    for w in engine.warnings():
        print(w.toString())
    sys.exit(-1)
sys.exit(0)
